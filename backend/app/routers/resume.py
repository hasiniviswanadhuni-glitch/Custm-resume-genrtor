from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.models.profile import Profile
from backend.app.models.job import JobDescription
from backend.app.models.suggestions import AISuggestion
from backend.app.models.resume import ResumeVersion
from backend.app.schemas.resume import ResumeCustomizationRequest, ResumeVersionResponse
from backend.app.services.matching_engine import matching_engine
from backend.app.services.ats_scorer import ats_scorer
from backend.app.services.resume_customizer import resume_customizer
from backend.app.routers.match import _serialize_profile_for_matching

router = APIRouter(prefix="/resumes", tags=["Customized Resume Versions"])

@router.post("/customize", response_model=ResumeVersionResponse)
def customize_resume(
    req: ResumeCustomizationRequest,
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.id == req.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    job = db.query(JobDescription).filter(JobDescription.id == req.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Target job description not found.")

    profile_dict = _serialize_profile_for_matching(profile)
    parsed_job = job.parsed_data or {}

    # Run matching
    match_analysis = matching_engine.match_candidate_against_job(profile_dict, parsed_job)
    score_data = ats_scorer.compute_score(match_analysis, parsed_job, profile_dict)

    # Fetch all user-approved or edited suggestions for this job
    approved_suggs = db.query(AISuggestion).filter(
        AISuggestion.profile_id == profile.id,
        AISuggestion.job_id == job.id,
        AISuggestion.status.in_(["accepted", "edited"])
    ).all()

    approved_list = [{
        "target_section": s.target_section,
        "target_item_id": s.target_item_id,
        "original_text": s.original_text,
        "suggested_text": s.suggested_text,
        "edited_text": s.edited_text,
        "status": s.status
    } for s in approved_suggs]

    # Derive tailored snapshot (Master profile is NEVER modified)
    tailored_content = resume_customizer.customize(
        profile_data=profile_dict,
        parsed_job=parsed_job,
        match_analysis=match_analysis,
        approved_suggestions=approved_list,
        ats_score=score_data["overall_score"],
        ats_breakdown=score_data
    )

    resume_title = req.title or f"{job.title} — Customized Resume"

    # Save as new version
    version = ResumeVersion(
        user_id=profile.user_id,
        profile_id=profile.id,
        job_id=job.id,
        title=resume_title,
        target_role=job.title,
        tailored_content=tailored_content,
        ats_score=score_data["overall_score"],
        ats_breakdown=score_data
    )
    db.add(version)
    db.commit()
    db.refresh(version)

    return version

@router.get("", response_model=List[ResumeVersionResponse])
def list_resume_versions(
    user_id: str = "default-user-id",
    db: Session = Depends(get_db)
):
    versions = db.query(ResumeVersion).filter(
        ResumeVersion.user_id == user_id
    ).order_by(ResumeVersion.created_at.desc()).all()
    return versions

@router.get("/{version_id}", response_model=ResumeVersionResponse)
def get_resume_version(version_id: str, db: Session = Depends(get_db)):
    version = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Customized resume version not found.")
    return version

@router.delete("/{version_id}")
def delete_resume_version(version_id: str, db: Session = Depends(get_db)):
    version = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Customized resume version not found.")
    db.delete(version)
    db.commit()
    return {"message": "Customized resume version deleted successfully."}
