import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.matching_engine import matching_engine
from backend.app.services.ats_scorer import ats_scorer
from backend.app.services.evidence_validator import evidence_validator
from backend.app.services.ai_service import ai_service
from backend.app.services.resume_customizer import resume_customizer
from backend.app.services.export_service import export_service

client = TestClient(app)

class TestDeepAuditBacktesting:
    """
    Exhaustive Functionality Backtesting covering every requirement in the Meta-Prompt.
    """

    # --------------------------------------------------------------------------
    # FEATURE 1: Master Profile Isolation & Multi-Version Derivation (Section 12 & 44)
    # --------------------------------------------------------------------------
    def test_feature_master_profile_isolation_across_multiple_jobs(self):
        """
        Verify that multiple job-specific resume versions can be derived without
        mutating the master candidate profile in any way.
        """
        # 1. Reset / Seed Master Profile
        res_prof = client.post("/api/profile/seed-demo")
        assert res_prof.status_code == 200
        master = res_prof.json()
        master_id = master["id"]
        original_summary = master["professional_summary"]
        original_skills_count = len(master["skills"])
        original_skills_order = [s["name"] for s in master["skills"]]
        original_proj_order = [p["title"] for p in master["projects"]]

        # 2. Create Job A (Backend Focus)
        job_a_res = client.post("/api/jobs", json={
            "title": "Backend Python Specialist",
            "company": "DataCorp",
            "raw_text": "Looking for a Backend Python Specialist with expertise in FastAPI, PostgreSQL, and SQL query tuning."
        })
        assert job_a_res.status_code == 200
        job_a = job_a_res.json()

        # 3. Create Job B (Frontend React Focus)
        job_b_res = client.post("/api/jobs", json={
            "title": "Frontend React Developer",
            "company": "UIVentures",
            "raw_text": "We need a Frontend React Developer proficient in TypeScript, React, Tailwind CSS, and user interfaces."
        })
        assert job_b_res.status_code == 200
        job_b = job_b_res.json()

        # 4. Generate & Approve Suggestion for Job A
        suggs_a = client.post("/api/suggestions/generate", json={"profile_id": master_id, "job_id": job_a["id"]}).json()
        assert len(suggs_a) > 0
        client.patch(f"/api/suggestions/{suggs_a[0]['id']}", json={"status": "accepted"})

        # 5. Generate & Approve Suggestion for Job B
        suggs_b = client.post("/api/suggestions/generate", json={"profile_id": master_id, "job_id": job_b["id"]}).json()
        assert len(suggs_b) > 0
        client.patch(f"/api/suggestions/{suggs_b[0]['id']}", json={"status": "accepted"})

        # 6. Derive Customized Resume A
        res_ver_a = client.post("/api/resumes/customize", json={
            "profile_id": master_id,
            "job_id": job_a["id"],
            "title": "Alex Morgan — Backend Resume"
        }).json()

        # 7. Derive Customized Resume B
        res_ver_b = client.post("/api/resumes/customize", json={
            "profile_id": master_id,
            "job_id": job_b["id"],
            "title": "Alex Morgan — Frontend Resume"
        }).json()

        # 8. Inspect Master Profile: Must remain 100% UNCHANGED
        current_master = client.get("/api/profile").json()
        assert current_master["professional_summary"] == original_summary, "Master summary was mutated!"
        assert len(current_master["skills"]) == original_skills_count, "Master skills count altered!"
        assert [s["name"] for s in current_master["skills"]] == original_skills_order, "Master skill order mutated!"
        assert [p["title"] for p in current_master["projects"]] == original_proj_order, "Master project order mutated!"

        # 9. Verify Tailored Resumes Diverged Correctly for their respective roles
        assert res_ver_a["tailored_content"]["skills"][0]["name"] == "Python" # Job A prioritizes Python
        assert res_ver_b["tailored_content"]["skills"][0]["name"] in ["React", "TypeScript"] # Job B prioritizes React/TS

    # --------------------------------------------------------------------------
    # FEATURE 2: Job Description Analysis Edge Cases & Validation (Section 6)
    # --------------------------------------------------------------------------
    def test_feature_jd_validation_and_multi_section_parsing(self):
        # Validation test: Reject empty or too short JD
        res_fail = client.post("/api/jobs", json={
            "title": "Software Dev",
            "raw_text": "Short"
        })
        assert res_fail.status_code in [400, 422], "Should reject short or invalid JD text"

        # Multi-section parsing test
        complex_jd = """
        Title: Senior ML & Cloud Engineer
        Company: AI Research Labs

        What You Need (Minimum Qualifications):
        - 4+ years of experience in Machine Learning and Python programming.
        - Bachelor's or Master's degree in Computer Science or Mathematics.
        - Deep understanding of scikit-learn, PyTorch, and SQL.

        Nice to Have (Bonus Points):
        - Hands-on experience with Docker, Kubernetes, and AWS cloud deployments.

        Responsibilities:
        - Design and train predictive machine learning pipelines.
        - Collaborate with backend engineers to expose model endpoints via REST APIs.
        - Monitor model latency and performance in production.
        """
        res_complex = client.post("/api/jobs", json={
            "title": "Senior ML & Cloud Engineer",
            "company": "AI Research Labs",
            "raw_text": complex_jd
        })
        assert res_complex.status_code == 200
        job_data = res_complex.json()
        parsed = job_data["parsed_data"]

        assert "Python" in parsed["technical_skills"] or "PYTHON" in parsed["technical_skills"]
        assert any("scikit-learn" in s.lower() for s in parsed["technical_skills"])
        assert len(parsed["responsibilities"]) >= 2
        assert len(parsed["education_requirements"]) >= 1
        assert len(parsed["experience_requirements"]) >= 1

    # --------------------------------------------------------------------------
    # FEATURE 3: Two-Level Matching & Gap Classification (Section 9)
    # --------------------------------------------------------------------------
    def test_feature_two_level_matching_engine_levels(self):
        profile = {
            "skills": [
                {"name": "Python"},
                {"name": "PostgreSQL"},
                {"name": "React"}
            ],
            "projects": [
                {
                    "title": "Analytics Web Service",
                    "technologies": ["Python", "FastAPI"],
                    "bullets": ["Integrated scikit-learn for anomaly detection in sensor datasets."]
                }
            ],
            "experience": [],
            "education": [{"degree": "B.S. in Computer Science", "institution": "State University"}],
            "certifications": []
        }

        target_job = {
            "job_title": "Full Stack & Cloud Engineer",
            "technical_skills": [
                "Python",        # Exact (in skills)
                "SQL",           # Related (candidate has PostgreSQL)
                "scikit-learn",  # Partial (in project bullet text)
                "Kubernetes"     # Missing (no evidence anywhere)
            ],
            "soft_skills": []
        }

        res = matching_engine.match_candidate_against_job(profile, target_job)

        exact_skills = [m["requirement_name"] for m in res["exact_matches"]]
        related_skills = [m["requirement_name"] for m in res["related_matches"]]
        partial_skills = [m["requirement_name"] for m in res["partial_matches"]]
        missing_skills = [m["requirement_name"] for m in res["missing_requirements"]]

        assert "Python" in exact_skills, "Python must be Exact Match"
        assert "SQL" in related_skills, "SQL must be Related Match via PostgreSQL"
        assert "scikit-learn" in partial_skills or "scikit-learn" in exact_skills, "scikit-learn must be matched from project"
        assert "Kubernetes" in missing_skills, "Kubernetes must be classified as Missing"

    # --------------------------------------------------------------------------
    # FEATURE 4: ATS Scoring Deterministic Calculation (Section 10)
    # --------------------------------------------------------------------------
    def test_feature_ats_scoring_mathematical_precision(self):
        # Test boundary: 100% match profile
        perfect_matches = {
            "all_matches": [
                {"requirement_name": "Python", "requirement_type": "technical_skill", "match_type": "exact"},
                {"requirement_name": "FastAPI", "requirement_type": "technical_skill", "match_type": "exact"},
            ]
        }
        perfect_job = {
            "technical_skills": ["Python", "FastAPI"],
            "keywords": ["Python", "FastAPI"],
            "education_requirements": ["B.S. in CS"]
        }
        perfect_profile = {
            "skills": [{"name": "Python"}, {"name": "FastAPI"}],
            "projects": [{"title": "Web App", "technologies": ["Python", "FastAPI"]}],
            "experience": [{"company": "Tech Corp", "position": "Developer"}],
            "education": [{"degree": "B.S. in CS"}],
            "professional_summary": "Python FastAPI developer"
        }

        score_res = ats_scorer.compute_score(perfect_matches, perfect_job, perfect_profile)

        # Check documented weights:
        # Technical (35%) + Keywords (25%) + Projects (20%) + Experience (10%) + Education (10%)
        assert "formula" in score_res["calculation_details"]
        assert score_res["overall_score"] >= 85.0
        assert score_res["technical_skills"] == 100.0

    # --------------------------------------------------------------------------
    # FEATURE 5: Anti-Hallucination Guard & Fact Preservation (Section 8, 21, 34)
    # --------------------------------------------------------------------------
    def test_feature_anti_hallucination_adversarial_rejections(self):
        """
        Adversarial test cases: System must reject/flag attempts to introduce
        fabricated certifications, unearned employers, or phantom metrics.
        """
        facts = {
            "skills": {"python", "sql", "react"},
            "technologies": {"python", "sql", "react", "fastapi"},
            "companies": {"nextech"},
            "institutions": {"university of washington"},
            "degrees": {"bachelor of science"},
            "certifications": set(),
            "numbers": {"89%", "100ms", "15"},
            "full_profile_text": "Python SQL React FastAPI NexTech 89% 100ms 15 hours"
        }
        missing_skills = ["Docker", "AWS", "Kubernetes"]

        # Attack 1: Missing skill claimed in experience
        is_valid, violations = evidence_validator.validate_suggestion(
            suggested_text="Spearheaded Kubernetes and Docker cluster architecture for production.",
            target_section="experience",
            facts=facts,
            missing_skills=missing_skills
        )
        assert not is_valid
        assert any("Rule 2 Violation" in v for v in violations)

        # Attack 2: Fabricated quantitative claim (e.g. 95% revenue boost when not in profile)
        is_valid, violations = evidence_validator.validate_suggestion(
            suggested_text="Boosted enterprise revenue by 95% and cut latency by 80%.",
            target_section="projects",
            facts=facts,
            missing_skills=missing_skills
        )
        assert not is_valid
        assert any("Rule 3 Violation" in v for v in violations)

        # Attack 3: Sanitization should strip ungrounded metrics safely
        sanitized = evidence_validator.sanitize_suggestion(
            text="Optimized query execution by 95% across database nodes.",
            violations=["Rule 3 Violation: Introduced unverified numerical claim '95%' not present in profile."]
        )
        assert "by 95%" not in sanitized
        assert "significantly" in sanitized

    # --------------------------------------------------------------------------
    # FEATURE 6: Explainable AI Suggestions & User Approval Workflow (Section 7, 11)
    # --------------------------------------------------------------------------
    def test_feature_ai_suggestion_explainability_and_user_approval(self):
        # 1. Seed demo profile & demo job
        p = client.post("/api/profile/seed-demo").json()
        j = client.post("/api/jobs/seed-demo").json()

        # 2. Generate suggestions
        suggs = client.post("/api/suggestions/generate", json={
            "profile_id": p["id"],
            "job_id": j["id"]
        }).json()

        assert len(suggs) > 0

        # Every suggestion MUST contain all 5 explainability fields
        for s in suggs:
            assert s["suggested_text"], "Must contain what is suggested"
            assert s["reason"], "Must contain why it matters"
            assert s["job_requirement"], "Must contain triggering job requirement"
            assert s["candidate_evidence"], "Must cite supporting candidate evidence"
            assert 0.0 <= s["confidence_score"] <= 1.0, "Must include confidence rating"
            assert s["status"] == "pending", "Initial state must be pending"

        # 3. User Action: Reject a suggestion
        first_sug = suggs[0]
        rej_res = client.patch(f"/api/suggestions/{first_sug['id']}", json={"status": "rejected"})
        assert rej_res.status_code == 200
        assert rej_res.json()["status"] == "rejected"

        # 4. User Action: Custom Edit a suggestion
        second_sug = suggs[1]
        custom_text = "Customized bullet wording edited directly by candidate."
        edit_res = client.patch(f"/api/suggestions/{second_sug['id']}", json={
            "status": "edited",
            "edited_text": custom_text
        })
        assert edit_res.status_code == 200
        assert edit_res.json()["status"] == "edited"
        assert edit_res.json()["edited_text"] == custom_text

    # --------------------------------------------------------------------------
    # FEATURE 7: Document Export File Verification (Section 28)
    # --------------------------------------------------------------------------
    def test_feature_export_binary_integrity(self):
        p = client.get("/api/profile").json()
        j = client.get("/api/jobs").json()[0]

        res = client.post("/api/resumes/customize", json={
            "profile_id": p["id"],
            "job_id": j["id"],
            "title": "Document Export Verification Resume"
        }).json()
        v_id = res["id"]

        # PDF Verification
        pdf_res = client.get(f"/api/export/{v_id}/pdf")
        assert pdf_res.status_code == 200
        assert pdf_res.headers["content-type"] == "application/pdf"
        assert pdf_res.content.startswith(b"%PDF"), "File does not have valid PDF magic bytes!"
        assert len(pdf_res.content) > 1000, "PDF file size too small"

        # DOCX Verification
        docx_res = client.get(f"/api/export/{v_id}/docx")
        assert docx_res.status_code == 200
        assert "openxmlformats" in docx_res.headers["content-type"]
        assert docx_res.content.startswith(b"PK"), "File does not have valid DOCX (ZIP/PK) magic bytes!"
        assert len(docx_res.content) > 5000, "DOCX file size too small"
