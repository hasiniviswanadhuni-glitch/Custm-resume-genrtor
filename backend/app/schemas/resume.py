from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TailoredProjectItem(BaseModel):
    id: Optional[str] = None
    title: str
    role: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    bullets: List[str] = Field(default_factory=list)
    live_url: Optional[str] = None
    repo_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    relevance_score: Optional[float] = None

class TailoredExperienceItem(BaseModel):
    id: Optional[str] = None
    company: str
    position: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    is_internship: bool = False
    relevance_score: Optional[float] = None

class TailoredResumeContent(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    professional_summary: str
    skills: List[Dict[str, Any]] = Field(default_factory=list) # categorized and prioritized
    projects: List[TailoredProjectItem] = Field(default_factory=list)
    experience: List[TailoredExperienceItem] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    achievements: List[Dict[str, Any]] = Field(default_factory=list)
    applied_suggestions_count: int = 0

class ResumeCustomizationRequest(BaseModel):
    profile_id: str
    job_id: str
    title: Optional[str] = None

class ResumeVersionResponse(BaseModel):
    id: str
    user_id: str
    profile_id: str
    job_id: str
    title: str
    target_role: Optional[str] = None
    tailored_content: TailoredResumeContent
    ats_score: float
    ats_breakdown: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
