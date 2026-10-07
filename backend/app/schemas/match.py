from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class SkillMatchSchema(BaseModel):
    id: Optional[str] = None
    requirement_name: str
    requirement_type: str # technical_skill, soft_skill, education, experience, responsibility
    candidate_evidence: Optional[str] = None
    match_type: str # exact, related, partial, missing, unsupported
    similarity_score: float = 0.0 # 0.0 - 100.0
    explanation: str

class ATSScoreBreakdown(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=100.0)
    keyword_match: float = Field(..., ge=0.0, le=100.0)
    technical_skills: float = Field(..., ge=0.0, le=100.0)
    experience_relevance: float = Field(..., ge=0.0, le=100.0)
    education_match: float = Field(..., ge=0.0, le=100.0)
    project_relevance: float = Field(..., ge=0.0, le=100.0)
    calculation_details: Dict[str, str] = Field(default_factory=dict)

class MatchAnalysisResponse(BaseModel):
    profile_id: str
    job_id: str
    job_title: str
    candidate_name: str
    overall_score: float
    score_breakdown: ATSScoreBreakdown
    exact_matches: List[SkillMatchSchema] = Field(default_factory=list)
    related_matches: List[SkillMatchSchema] = Field(default_factory=list)
    partial_matches: List[SkillMatchSchema] = Field(default_factory=list)
    missing_requirements: List[SkillMatchSchema] = Field(default_factory=list)
    all_matches: List[SkillMatchSchema] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
