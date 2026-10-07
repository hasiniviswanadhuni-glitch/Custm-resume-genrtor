import pytest
from backend.app.services.matching_engine import matching_engine

def test_exact_and_missing_skill_classification():
    profile_data = {
        "skills": [{"name": "Python"}, {"name": "SQL"}, {"name": "React"}],
        "projects": [
            {
                "title": "Inventory System",
                "technologies": ["Python", "SQL"],
                "bullets": ["Designed relational tables"]
            }
        ],
        "experience": [],
        "education": [{"degree": "B.S. in Computer Science", "institution": "State University"}],
        "certifications": []
    }
    
    parsed_job = {
        "technical_skills": ["Python", "AWS", "Docker"],
        "soft_skills": [],
        "education_requirements": ["Bachelor's degree in Computer Science"],
        "experience_requirements": []
    }
    
    matches = matching_engine.match_candidate_against_job(profile_data, parsed_job)
    
    exact_req_names = [m["requirement_name"] for m in matches["exact_matches"]]
    missing_req_names = [m["requirement_name"] for m in matches["missing_requirements"]]
    
    # Python is an exact match
    assert "Python" in exact_req_names
    # AWS and Docker are missing
    assert "AWS" in missing_req_names
    assert "Docker" in missing_req_names
    assert "Docker" not in exact_req_names
    assert "AWS" not in exact_req_names

def test_related_semantic_match():
    # If candidate has PostgreSQL and job asks for SQL, or React and job asks for Next.js
    profile_data = {
        "skills": [{"name": "PostgreSQL"}, {"name": "React"}],
        "projects": [],
        "experience": [],
        "education": [],
        "certifications": []
    }
    parsed_job = {
        "technical_skills": ["SQL", "Next.js"],
        "soft_skills": []
    }
    matches = matching_engine.match_candidate_against_job(profile_data, parsed_job)
    related_names = [m["requirement_name"].lower() for m in matches["related_matches"]]
    
    assert "sql" in related_names or "next.js" in related_names
