from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class EducationBase(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    honors: Optional[str] = None

class EducationCreate(EducationBase):
    pass

class EducationResponse(EducationBase):
    id: str
    profile_id: str
    created_at: datetime

    model_config = {"from_attributes": True}

class SkillBase(BaseModel):
    name: str
    category: str = "technical" # technical, soft, tool, domain
    proficiency_level: str = "intermediate" # beginner, intermediate, advanced, expert

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: str
    profile_id: str
    created_at: datetime

    model_config = {"from_attributes": True}

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    role: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    bullets: List[str] = Field(default_factory=list)
    live_url: Optional[str] = None
    repo_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: str
    profile_id: str
    created_at: datetime

    model_config = {"from_attributes": True}

class ExperienceBase(BaseModel):
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

class ExperienceCreate(ExperienceBase):
    pass

class ExperienceResponse(ExperienceBase):
    id: str
    profile_id: str
    created_at: datetime

    model_config = {"from_attributes": True}

class CertificationBase(BaseModel):
    name: str
    issuer: str
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None

class CertificationCreate(CertificationBase):
    pass

class CertificationResponse(CertificationBase):
    id: str
    profile_id: str
    created_at: datetime

    model_config = {"from_attributes": True}

class AchievementBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: Optional[str] = None

class AchievementCreate(AchievementBase):
    pass

class AchievementResponse(AchievementBase):
    id: str
    profile_id: str
    created_at: datetime

    model_config = {"from_attributes": True}

class ProfileBase(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    professional_summary: Optional[str] = None

class ProfileCreate(ProfileBase):
    user_id: Optional[str] = "default-user-id"
    education: Optional[List[EducationCreate]] = None
    skills: Optional[List[SkillCreate]] = None
    projects: Optional[List[ProjectCreate]] = None
    experience: Optional[List[ExperienceCreate]] = None
    certifications: Optional[List[CertificationCreate]] = None
    achievements: Optional[List[AchievementCreate]] = None

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    professional_summary: Optional[str] = None

class ProfileResponse(ProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    education: List[EducationResponse] = Field(default_factory=list)
    skills: List[SkillResponse] = Field(default_factory=list)
    projects: List[ProjectResponse] = Field(default_factory=list)
    experience: List[ExperienceResponse] = Field(default_factory=list)
    certifications: List[CertificationResponse] = Field(default_factory=list)
    achievements: List[AchievementResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}
