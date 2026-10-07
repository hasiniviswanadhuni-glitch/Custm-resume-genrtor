from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.profile import Profile
from backend.app.models.job import JobDescription
from backend.app.models.match import SkillMatch
from backend.app.schemas.match import MatchAnalysisResponse, ATSScoreBreakdown
from backend.app.services.matching_engine import matching_engine
from backend.app.services.ats_scorer import ats_scorer

router = APIRouter(prefix="/match", tags=["Matching & Gap Analysis"])

def _serialize_profile_for_matching(profile: Profile) -> dict:
    return {
        "id": profile.id,
        "full_name": profile.full_name,
        "email": profile.email,
        "professional_summary": profile.professional_summary,
        "skills": [{"name": s.name, "category": s.category, "proficiency_level": s.proficiency_level} for s in profile.skills],
        "projects": [{
            "id": p.id, "title": p.title, "description": p.description,
            "technologies": p.technologies or [], "bullets": p.bullets or []
        } for p in profile.projects],
        "experience": [{
            "id": e.id, "company": e.company, "position": e.position,
            "description": e.description, "bullets": e.bullets or [], "technologies": e.technologies or []
        } for e in profile.experience],
        "education": [{
            "institution": ed.institution, "degree": ed.degree, "field_of_study": ed.field_of_study
        } for ed in profile.education],
        "certifications": [{"name": c.name, "issuer": c.issuer} for c in profile.certifications],
    }

@router.post("", response_model=MatchAnalysisResponse)
def perform_match_analysis(
    profile_id: str,
    job_id: str,
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")

    profile_dict = _serialize_profile_for_matching(profile)
    parsed_job = job.parsed_data or {}

    # Run two-level matching
    raw_match_results = matching_engine.match_candidate_against_job(profile_dict, parsed_job)

    # Compute ATS transparent score breakdown
    score_data = ats_scorer.compute_score(raw_match_results, parsed_job, profile_dict)

    # Clear prior stored matches for this profile and job
    db.query(SkillMatch).filter(SkillMatch.profile_id == profile.id, SkillMatch.job_id == job.id).delete()

    # Save fresh matches
    for m in raw_match_results.get("all_matches", []):
        db.add(SkillMatch(
            profile_id=profile.id,
            job_id=job.id,
            requirement_name=m["requirement_name"],
            requirement_type=m["requirement_type"],
            candidate_evidence=m["candidate_evidence"],
            match_type=m["match_type"],
            similarity_score=m["similarity_score"],
            explanation=m["explanation"]
        ))
    db.commit()

    return MatchAnalysisResponse(
        profile_id=profile.id,
        job_id=job.id,
        job_title=job.title,
        candidate_name=profile.full_name,
        overall_score=score_data["overall_score"],
        score_breakdown=ATSScoreBreakdown(**score_data),
        exact_matches=raw_match_results.get("exact_matches", []),
        related_matches=raw_match_results.get("related_matches", []),
        partial_matches=raw_match_results.get("partial_matches", []),
        missing_requirements=raw_match_results.get("missing_requirements", []),
        all_matches=raw_match_results.get("all_matches", [])
    )

@router.get("/{job_id}", response_model=MatchAnalysisResponse)
def get_match_analysis(
    job_id: str,
    user_id: str = "default-user-id",
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Master profile not found.")

    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")

    return perform_match_analysis(profile_id=profile.id, job_id=job.id, db=db)
