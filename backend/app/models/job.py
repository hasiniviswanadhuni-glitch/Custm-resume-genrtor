import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)
    parsed_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    requirements = relationship("JobRequirement", back_populates="job", cascade="all, delete-orphan")
    resume_versions = relationship("ResumeVersion", back_populates="job", cascade="all, delete-orphan")
    skill_matches = relationship("SkillMatch", back_populates="job", cascade="all, delete-orphan")
    ai_suggestions = relationship("AISuggestion", back_populates="job", cascade="all, delete-orphan")

class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_type = Column(String(50), nullable=False) # required_skill, preferred_skill, technical_skill, soft_skill, education, experience, responsibility, keyword
    description = Column(Text, nullable=False)
    importance_weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("JobDescription", back_populates="requirements")
