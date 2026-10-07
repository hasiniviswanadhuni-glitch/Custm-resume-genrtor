from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.models.profile import Profile
from backend.app.models.job import JobDescription
from backend.app.models.suggestions import AISuggestion
from backend.app.schemas.suggestion import (
    SuggestionResponse, SuggestionActionRequest,
    BatchSuggestionActionRequest, GenerateSuggestionsRequest
)
from backend.app.services.matching_engine import matching_engine
from backend.app.services.ai_service import ai_service
from backend.app.routers.match import _serialize_profile_for_matching

router = APIRouter(prefix="/suggestions", tags=["Explainable AI Suggestions"])

@router.post("/generate", response_model=List[SuggestionResponse])
def generate_ai_suggestions(
    req: GenerateSuggestionsRequest,
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.id == req.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    job = db.query(JobDescription).filter(JobDescription.id == req.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")

    profile_dict = _serialize_profile_for_matching(profile)
    parsed_job = job.parsed_data or {}

    # Match analysis first
    match_analysis = matching_engine.match_candidate_against_job(profile_dict, parsed_job)

    # Generate grounded explainable suggestions
    raw_suggs = ai_service.generate_suggestions(profile_dict, parsed_job, match_analysis)

    # Check for existing suggestions to avoid duplicate thrashing, or refresh pending ones
    db.query(AISuggestion).filter(
        AISuggestion.profile_id == profile.id,
        AISuggestion.job_id == job.id,
        AISuggestion.status == "pending"
    ).delete()

    created_suggs = []
    for s in raw_suggs:
        sug_record = AISuggestion(
            profile_id=profile.id,
            job_id=job.id,
            target_section=s["target_section"],
            target_item_id=s.get("target_item_id"),
            original_text=s.get("original_text"),
            suggested_text=s["suggested_text"],
            reason=s["reason"],
            job_requirement=s["job_requirement"],
            candidate_evidence=s["candidate_evidence"],
            confidence_score=s.get("confidence_score", 0.90),
            status="pending"
        )
        db.add(sug_record)
        created_suggs.append(sug_record)

    db.commit()
    for s in created_suggs:
        db.refresh(s)

    # Return all suggestions for this profile & job
    return db.query(AISuggestion).filter(
        AISuggestion.profile_id == profile.id,
        AISuggestion.job_id == job.id
    ).all()

@router.get("/{job_id}", response_model=List[SuggestionResponse])
def get_job_suggestions(
    job_id: str,
    user_id: str = "default-user-id",
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Master profile not found.")

    suggestions = db.query(AISuggestion).filter(
        AISuggestion.profile_id == profile.id,
        AISuggestion.job_id == job_id
    ).order_by(AISuggestion.created_at.desc()).all()

    if not suggestions:
        # Auto-generate if not yet present
        req = GenerateSuggestionsRequest(profile_id=profile.id, job_id=job_id)
        return generate_ai_suggestions(req, db)

    return suggestions

@router.patch("/{suggestion_id}", response_model=SuggestionResponse)
def update_suggestion_status(
    suggestion_id: str,
    action: SuggestionActionRequest,
    db: Session = Depends(get_db)
):
    sug = db.query(AISuggestion).filter(AISuggestion.id == suggestion_id).first()
    if not sug:
        raise HTTPException(status_code=404, detail="Suggestion not found.")

    sug.status = action.status
    if action.status == "edited" and action.edited_text:
        sug.edited_text = action.edited_text

    db.commit()
    db.refresh(sug)
    return sug

@router.post("/batch", response_model=List[SuggestionResponse])
def batch_update_suggestions(
    req: BatchSuggestionActionRequest,
    db: Session = Depends(get_db)
):
    updated = []
    for item in req.actions:
        sug = db.query(AISuggestion).filter(AISuggestion.id == item.suggestion_id).first()
        if sug:
            sug.status = item.status
            if item.status == "edited" and item.edited_text:
                sug.edited_text = item.edited_text
            updated.append(sug)

    db.commit()
    for s in updated:
        db.refresh(s)
    return updated
