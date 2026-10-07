import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_full_api_workflow_e2e():
    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    # 2. Seed Master Profile
    res_seed = client.post("/api/profile/seed-demo")
    assert res_seed.status_code == 200
    profile_data = res_seed.json()
    profile_id = profile_data["id"]
    assert profile_data["full_name"] == "Alex Morgan"
    assert len(profile_data["skills"]) > 5

    # 3. Seed Demo Job Description
    res_job = client.post("/api/jobs/seed-demo")
    assert res_job.status_code == 200
    job_data = res_job.json()
    job_id = job_data["id"]
    assert "Python" in job_data["raw_text"]

    # 4. Run Match Analysis
    res_match = client.post(f"/api/match?profile_id={profile_id}&job_id={job_id}")
    assert res_match.status_code == 200
    match_data = res_match.json()
    assert match_data["overall_score"] > 60.0
    assert len(match_data["exact_matches"]) > 0
    assert "score_breakdown" in match_data

    # 5. Generate AI Suggestions
    res_sugg = client.post("/api/suggestions/generate", json={
        "profile_id": profile_id,
        "job_id": job_id
    })
    assert res_sugg.status_code == 200
    suggestions = res_sugg.json()
    assert len(suggestions) > 0

    first_sug_id = suggestions[0]["id"]

    # 6. User Approves Suggestion (User Control)
    res_patch = client.patch(f"/api/suggestions/{first_sug_id}", json={
        "status": "accepted"
    })
    assert res_patch.status_code == 200
    assert res_patch.json()["status"] == "accepted"

    # 7. Generate Job-Specific Resume Version
    res_custom = client.post("/api/resumes/customize", json={
        "profile_id": profile_id,
        "job_id": job_id,
        "title": "Alex Morgan — Python & Full Stack Resume"
    })
    assert res_custom.status_code == 200
    resume_ver = res_custom.json()
    version_id = resume_ver["id"]
    assert resume_ver["ats_score"] > 60.0
    assert resume_ver["tailored_content"]["full_name"] == "Alex Morgan"

    # 8. Export to PDF
    res_pdf = client.get(f"/api/export/{version_id}/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert len(res_pdf.content) > 500

    # 9. Export to DOCX
    res_docx = client.get(f"/api/export/{version_id}/docx")
    assert res_docx.status_code == 200
    assert "openxmlformats" in res_docx.headers["content-type"]
    assert len(res_docx.content) > 500

    # 10. Verify Master Profile remains intact and unmutated
    res_prof_check = client.get("/api/profile")
    assert res_prof_check.status_code == 200
    assert res_prof_check.json()["id"] == profile_id
