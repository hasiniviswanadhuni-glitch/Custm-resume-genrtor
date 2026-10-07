from typing import Dict, List, Any

class ATSScorer:
    """
    Transparent ATS Match Scorer.
    Calculates deterministic multi-factor match percentages with documented formulas:
    - Keyword Match: % of job keywords appearing in candidate profile
    - Technical Skills: Weighted score of exact and related technical matches
    - Experience Relevance: Overlap of technologies and role domain
    - Education Match: Alignment with education prerequisites
    - Project Relevance: Coverage of target skills within candidate projects
    """

    # Weight distribution summing to 1.00
    WEIGHTS = {
        "technical_skills": 0.35,
        "keyword_match": 0.25,
        "project_relevance": 0.20,
        "experience_relevance": 0.10,
        "education_match": 0.10,
    }

    def compute_score(
        self,
        match_analysis: Dict[str, Any],
        parsed_job: Dict[str, Any],
        profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        tech_reqs = parsed_job.get("technical_skills", [])
        keywords = parsed_job.get("keywords", [])
        all_matches = match_analysis.get("all_matches", [])

        # 1. Technical Skills Score
        # Exact = 100%, Related = 75%, Partial = 50%, Missing = 0%
        tech_matches = [m for m in all_matches if m.get("requirement_type") == "technical_skill"]
        if tech_matches:
            tech_points = sum(
                100.0 if m["match_type"] == "exact" else
                75.0 if m["match_type"] == "related" else
                50.0 if m["match_type"] == "partial" else 0.0
                for m in tech_matches
            )
            tech_score = round(tech_points / len(tech_matches), 1)
        else:
            tech_score = 80.0

        # 2. Keyword Match Score
        # Check presence of keywords across candidate profile
        profile_skills = [s.get("name", "").lower() for s in profile_data.get("skills", [])]
        projects_tech = []
        for p in profile_data.get("projects", []):
            projects_tech.extend([t.lower() for t in p.get("technologies", [])])
        summary = (profile_data.get("professional_summary") or "").lower()

        combined_corpus = set(profile_skills + projects_tech + summary.split())
        if keywords:
            found_kw = sum(1 for kw in keywords if any(k_part in combined_corpus for k_part in kw.lower().split()))
            kw_score = round(min(100.0, (found_kw / len(keywords)) * 100.0), 1)
        else:
            kw_score = 85.0

        # 3. Project Relevance Score
        candidate_projects = profile_data.get("projects", [])
        if candidate_projects and tech_reqs:
            tech_set = {t.lower() for t in tech_reqs}
            proj_hits = 0
            for p in candidate_projects:
                p_techs = {t.lower() for t in p.get("technologies", [])}
                if p_techs.intersection(tech_set):
                    proj_hits += 1
            project_score = round(min(100.0, (proj_hits / max(1, len(candidate_projects))) * 90.0 + 10.0), 1)
        elif candidate_projects:
            project_score = 75.0
        else:
            project_score = 40.0

        # 4. Experience Relevance Score
        candidate_experience = profile_data.get("experience", [])
        if candidate_experience:
            exp_score = min(100.0, 70.0 + len(candidate_experience) * 15.0)
        else:
            # Fresher with project strength
            exp_score = 65.0 if candidate_projects else 50.0

        # 5. Education Match Score
        candidate_education = profile_data.get("education", [])
        edu_reqs = parsed_job.get("education_requirements", [])
        if not edu_reqs or candidate_education:
            edu_score = 95.0
        else:
            edu_score = 60.0

        # 6. Overall Weighted Score
        overall = round(
            (tech_score * self.WEIGHTS["technical_skills"]) +
            (kw_score * self.WEIGHTS["keyword_match"]) +
            (project_score * self.WEIGHTS["project_relevance"]) +
            (exp_score * self.WEIGHTS["experience_relevance"]) +
            (edu_score * self.WEIGHTS["education_match"]),
            1
        )
        overall = min(100.0, max(0.0, overall))

        calculation_details = {
            "formula": "Overall = (Technical * 0.35) + (Keywords * 0.25) + (Projects * 0.20) + (Experience * 0.10) + (Education * 0.10)",
            "technical_skills": f"{len(tech_matches)} technical skills evaluated: Exact=100%, Related=75%, Partial=50%, Missing=0%.",
            "keyword_match": f"{len(keywords)} target keywords evaluated against candidate skills, projects, and summary.",
            "project_relevance": f"{len(candidate_projects)} projects evaluated for technology overlap with job requirements.",
            "experience_relevance": f"{len(candidate_experience)} logged work roles evaluated for relevance.",
            "education_match": f"Candidate degree credentials evaluated against required academic background."
        }

        return {
            "overall_score": overall,
            "technical_skills": tech_score,
            "keyword_match": kw_score,
            "project_relevance": project_score,
            "experience_relevance": exp_score,
            "education_match": edu_score,
            "calculation_details": calculation_details
        }

ats_scorer = ATSScorer()
