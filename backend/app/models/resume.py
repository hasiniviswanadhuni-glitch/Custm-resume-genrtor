import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, BigInteger
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=False, index=True)
    profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    target_role = Column(String(255), nullable=True)
    tailored_content = Column(JSON, nullable=False) # Complete snapshot of tailored resume content
    ats_score = Column(Float, default=0.0) # Calculated ATS match score (0 - 100)
    ats_breakdown = Column(JSON, default=dict) # Breakdown details (keyword, skills, experience, etc.)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    profile = relationship("Profile", back_populates="resume_versions")
    job = relationship("JobDescription", back_populates="resume_versions")
    exports = relationship("Export", back_populates="resume_version", cascade="all, delete-orphan")

class Export(Base):
    __tablename__ = "exports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resume_version_id = Column(String(36), ForeignKey("resume_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    format = Column(String(10), nullable=False) # pdf, docx
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    resume_version = relationship("ResumeVersion", back_populates="exports")
