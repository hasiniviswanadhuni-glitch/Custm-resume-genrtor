import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class SkillMatch(Base):
    __tablename__ = "skill_matches"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_name = Column(String(255), nullable=False)
    requirement_type = Column(String(50), nullable=False) # technical_skill, soft_skill, education, experience, responsibility
    candidate_evidence = Column(Text, nullable=True) # Evidence from candidate's profile
    match_type = Column(String(50), nullable=False) # exact, related, partial, missing, unsupported
    similarity_score = Column(Float, default=0.0) # 0.0 - 100.0
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    profile = relationship("Profile", back_populates="skill_matches")
    job = relationship("JobDescription", back_populates="skill_matches")
