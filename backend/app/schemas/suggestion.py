from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SuggestionResponse(BaseModel):
    id: str
    profile_id: str
    job_id: str
    target_section: str # summary, skills, projects, experience, certifications
    target_item_id: Optional[str] = None
    original_text: Optional[str] = None
    suggested_text: str
    reason: str
    job_requirement: str
    candidate_evidence: str
    confidence_score: float = 0.90
    status: str = "pending" # pending, accepted, rejected, edited
    edited_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class SuggestionActionRequest(BaseModel):
    status: str = Field(..., pattern="^(accepted|rejected|edited|pending)$")
    edited_text: Optional[str] = None

class BatchSuggestionItemAction(BaseModel):
    suggestion_id: str
    status: str = Field(..., pattern="^(accepted|rejected|edited)$")
    edited_text: Optional[str] = None

class BatchSuggestionActionRequest(BaseModel):
    actions: List[BatchSuggestionItemAction]

class GenerateSuggestionsRequest(BaseModel):
    profile_id: str
    job_id: str
