import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class AISuggestion(Base):
    __tablename__ = "ai_suggestions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    target_section = Column(String(50), nullable=False) # summary, skills, projects, experience, certifications
    target_item_id = Column(String(100), nullable=True) # Optional ID of the project/experience/skill being targeted
    original_text = Column(Text, nullable=True)
    suggested_text = Column(Text, nullable=False)
    reason = Column(Text, nullable=False) # Why it matters
    job_requirement = Column(Text, nullable=False) # Specific JD requirement that triggered it
    candidate_evidence = Column(Text, nullable=False) # Grounded candidate evidence
    confidence_score = Column(Float, default=0.90) # Confidence level (0.0 - 1.0)
    status = Column(String(50), default="pending", nullable=False) # pending, accepted, rejected, edited
    edited_text = Column(Text, nullable=True) # User's manual edit if status == 'edited'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    profile = relationship("Profile", back_populates="ai_suggestions")
    job = relationship("JobDescription", back_populates="ai_suggestions")
