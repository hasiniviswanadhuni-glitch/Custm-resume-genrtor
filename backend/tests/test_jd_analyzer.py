import pytest
from backend.app.services.jd_analyzer import jd_analyzer

def test_extract_technical_and_soft_skills():
    sample_jd = """
    We are seeking a Senior Backend Engineer.
    Must have strong hands-on experience in Python, FastAPI, PostgreSQL, and Docker.
    Nice to have: Kubernetes and AWS.
    Strong communication and problem solving skills required.
    """
    result = jd_analyzer.analyze(sample_jd, title="Senior Backend Engineer")
    
    assert "Python" in result["technical_skills"] or "PYTHON" in result["technical_skills"]
    assert any("fastapi" in s.lower() for s in result["technical_skills"])
    assert any("postgresql" in s.lower() for s in result["technical_skills"])
    assert any("docker" in s.lower() for s in result["technical_skills"])
    assert any("communication" in s.lower() for s in result["soft_skills"])

def test_extract_education_and_experience():
    sample_jd = """
    Requirements:
    - Bachelor's degree in Computer Science or related STEM field.
    - 3+ years of experience in backend web development.
    """
    result = jd_analyzer.analyze(sample_jd)
    
    assert len(result["education_requirements"]) > 0
    assert any("bachelor" in e.lower() for e in result["education_requirements"])
    assert len(result["experience_requirements"]) > 0
