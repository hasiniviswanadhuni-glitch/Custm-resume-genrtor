import pytest
from backend.app.services.resume_customizer import resume_customizer

def test_resume_customizer_preserves_master_profile_and_prioritizes():
    master_profile = {
        "full_name": "Taylor Swift",
        "email": "taylor@example.com",
        "professional_summary": "Original generic summary.",
        "skills": [
            {"name": "HTML", "category": "technical", "proficiency_level": "advanced"},
            {"name": "Python", "category": "technical", "proficiency_level": "expert"},
            {"name": "React", "category": "technical", "proficiency_level": "intermediate"}
        ],
        "projects": [
            {
                "id": "proj_1",
                "title": "Static Web Page",
                "technologies": ["HTML", "CSS"],
                "bullets": ["Built static landing page."]
            },
            {
                "id": "proj_2",
                "title": "Python Microservice",
                "technologies": ["Python", "FastAPI"],
                "bullets": ["Built API endpoints."]
            }
        ],
        "experience": [],
        "education": [{"degree": "B.S. in CS", "institution": "State University"}],
        "certifications": [],
        "achievements": []
    }

    parsed_job = {
        "job_title": "Python Backend Developer",
        "technical_skills": ["Python", "FastAPI"]
    }

    approved_suggestions = [
        {
            "target_section": "summary",
            "target_item_id": "summary",
            "status": "accepted",
            "suggested_text": "Tailored summary highlighting Python Backend capabilities."
        }
    ]

    tailored = resume_customizer.customize(
        profile_data=master_profile,
        parsed_job=parsed_job,
        match_analysis={"all_matches": []},
        approved_suggestions=approved_suggestions,
        ats_score=85.0,
        ats_breakdown={}
    )

    # 1. Summary updated with approved suggestion
    assert tailored["professional_summary"] == "Tailored summary highlighting Python Backend capabilities."
    # 2. Master profile original summary remains unchanged in source dictionary!
    assert master_profile["professional_summary"] == "Original generic summary."

    # 3. Skills reordered: Python should be first because it matches the job!
    assert tailored["skills"][0]["name"] == "Python"

    # 4. Projects reordered: Python Microservice should be ranked #1
    assert tailored["projects"][0]["title"] == "Python Microservice"
