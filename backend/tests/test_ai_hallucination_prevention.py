import pytest
from backend.app.services.matching_engine import matching_engine
from backend.app.services.ai_service import ai_service
from backend.app.services.evidence_validator import evidence_validator

def test_anti_hallucination_guarantee_section_34():
    """
    Test Section 34 specification:
    Candidate: Python, SQL, React
    Job: Python, AWS, Docker
    Expected:
    Python -> Match
    AWS -> Missing
    Docker -> Missing
    System must NOT hallucinate Docker experience or AWS certifications.
    """
    candidate_profile = {
        "full_name": "Jordan Lee",
        "email": "jordan@example.com",
        "professional_summary": "Junior developer with foundation in Python and React.",
        "skills": [{"name": "Python"}, {"name": "SQL"}, {"name": "React"}],
        "projects": [
            {
                "title": "Data Aggregator",
                "technologies": ["Python", "SQL"],
                "bullets": ["Wrote SQL queries to process dataset in Python."]
            }
        ],
        "experience": [],
        "education": [{"degree": "B.S. in Computer Science", "institution": "Tech University"}],
        "certifications": []
    }

    job_description = {
        "job_title": "Cloud Platform Engineer",
        "technical_skills": ["Python", "AWS", "Docker"],
        "soft_skills": []
    }

    # 1. Matching Engine Verification
    matches = matching_engine.match_candidate_against_job(candidate_profile, job_description)

    exact_matches = [m["requirement_name"] for m in matches["exact_matches"]]
    missing_matches = [m["requirement_name"] for m in matches["missing_requirements"]]

    assert "Python" in exact_matches
    assert "AWS" in missing_matches
    assert "Docker" in missing_matches
    assert "AWS" not in exact_matches
    assert "Docker" not in exact_matches

    # 2. AI Suggestions Verification
    suggestions = ai_service.generate_suggestions(candidate_profile, job_description, matches)

    # Verify no suggestion claims the candidate has AWS or Docker experience
    for s in suggestions:
        sug_text = s["suggested_text"].lower()
        # Should NOT claim candidate is an AWS or Docker engineer
        assert "docker engineer" not in sug_text
        assert "aws certified" not in sug_text
        assert "experienced in docker" not in sug_text
        assert "proficient in aws" not in sug_text

    # 3. Evidence Validator Fact Extraction & Enforcement
    candidate_facts = evidence_validator.extract_candidate_facts(candidate_profile)
    assert "docker" not in candidate_facts["skills"]
    assert "aws" not in candidate_facts["skills"]

    # Simulating a rogue prompt attempt trying to claim Docker
    rogue_claim = "Engineered cloud microservices using Docker and AWS resulting in 40% speedup."
    is_valid, violations = evidence_validator.validate_suggestion(
        suggested_text=rogue_claim,
        target_section="projects",
        facts=candidate_facts,
        missing_skills=["Docker", "AWS"]
    )
    assert not is_valid
    assert len(violations) > 0
    assert any("Docker" in v or "AWS" in v for v in violations)
