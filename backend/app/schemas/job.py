from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class JobRequirementBase(BaseModel):
    requirement_type: str # required_skill, preferred_skill, technical_skill, soft_skill, education, experience, responsibility, keyword
    description: str
    importance_weight: float = 1.0

class JobRequirementCreate(JobRequirementBase):
    pass

class JobRequirementResponse(JobRequirementBase):
    id: str
    job_id: str
    created_at: datetime

    model_config = {"from_attributes": True}

class JobCreate(BaseModel):
    title: str = Field(..., min_length=2)
    company: Optional[str] = None
    raw_text: str = Field(..., min_length=20)
    user_id: Optional[str] = "default-user-id"

class ParsedJobData(BaseModel):
    job_title: str
    company: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    education_requirements: List[str] = Field(default_factory=list)
    experience_requirements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    domain_requirements: List[str] = Field(default_factory=list)

class JobResponse(BaseModel):
    id: str
    user_id: str
    title: str
    company: Optional[str] = None
    raw_text: str
    parsed_data: Dict[str, Any] = Field(default_factory=dict)
    requirements: List[JobRequirementResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
