from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.models.job import JobDescription, JobRequirement
from backend.app.schemas.job import JobCreate, JobResponse
from backend.app.services.jd_analyzer import jd_analyzer

router = APIRouter(prefix="/jobs", tags=["Job Descriptions"])

@router.post("", response_model=JobResponse)
def create_and_analyze_job(job_in: JobCreate, db: Session = Depends(get_db)):
    if len(job_in.raw_text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Job description text is too short to analyze.")

    # Run multi-stage extraction
    parsed = jd_analyzer.analyze(job_in.raw_text, title=job_in.title, company=job_in.company or "")

    job = JobDescription(
        user_id=job_in.user_id or "default-user-id",
        title=parsed.get("job_title") or job_in.title,
        company=job_in.company or parsed.get("company"),
        raw_text=job_in.raw_text,
        parsed_data=parsed
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Save extracted requirements
    for tech in parsed.get("technical_skills", []):
        db.add(JobRequirement(
            job_id=job.id,
            requirement_type="technical_skill",
            description=tech,
            importance_weight=1.2
        ))
    for soft in parsed.get("soft_skills", []):
        db.add(JobRequirement(
            job_id=job.id,
            requirement_type="soft_skill",
            description=soft,
            importance_weight=0.8
        ))
    for edu in parsed.get("education_requirements", []):
        db.add(JobRequirement(
            job_id=job.id,
            requirement_type="education",
            description=edu,
            importance_weight=1.0
        ))
    for exp in parsed.get("experience_requirements", []):
        db.add(JobRequirement(
            job_id=job.id,
            requirement_type="experience",
            description=exp,
            importance_weight=1.0
        ))

    db.commit()
    db.refresh(job)
    return job

@router.get("", response_model=List[JobResponse])
def list_jobs(user_id: str = "default-user-id", db: Session = Depends(get_db)):
    jobs = db.query(JobDescription).filter(JobDescription.user_id == user_id).order_by(JobDescription.created_at.desc()).all()
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Target job description not found.")
    return job

@router.delete("/{job_id}")
def delete_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Target job description not found.")
    db.delete(job)
    db.commit()
    return {"message": "Job description deleted successfully."}

@router.post("/seed-demo", response_model=JobResponse)
def seed_demo_job(user_id: str = "default-user-id", db: Session = Depends(get_db)):
    """
    Seeds a representative target job description for immediate evaluation.
    """
    demo_jd_text = """
Software Engineer - Python & Full Stack
TechVentures Inc. — Seattle, WA

About The Role:
We are looking for an ambitious Software Engineer to join our Core Services team. You will build high-performance APIs and interactive web interfaces powering our cloud platform.

Responsibilities:
• Architect, test, and maintain robust REST APIs using Python and modern web frameworks.
• Develop intuitive user interfaces using React and TypeScript.
• Design and optimize relational database schemas and queries in PostgreSQL.
• Implement automated tests and participate in CI/CD pipeline improvements.
• Collaborate in an agile team environment with cross-functional product designers.

Requirements:
• Bachelor's degree in Computer Science, Software Engineering, or related technical field.
• Strong programming proficiency in Python and modern JavaScript/TypeScript.
• Hands-on experience with web frameworks such as FastAPI, Django, or Flask.
• Practical familiarity with React, state management, and HTML/CSS.
• Solid foundation in SQL, relational databases (PostgreSQL or MySQL).
• Experience with Git version control and collaborative code reviews.

Preferred Qualifications:
• Familiarity with Docker containerization and AWS cloud services.
• Experience or exposure to Machine Learning pipelines (scikit-learn, Pandas).
• Strong analytical problem solving and communication skills.
"""
    parsed = jd_analyzer.analyze(demo_jd_text, title="Software Engineer - Python & Full Stack", company="TechVentures Inc.")

    job = JobDescription(
        user_id=user_id,
        title="Software Engineer - Python & Full Stack",
        company="TechVentures Inc.",
        raw_text=demo_jd_text,
        parsed_data=parsed
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    for tech in parsed.get("technical_skills", []):
        db.add(JobRequirement(job_id=job.id, requirement_type="technical_skill", description=tech))
    for soft in parsed.get("soft_skills", []):
        db.add(JobRequirement(job_id=job.id, requirement_type="soft_skill", description=soft))
    for edu in parsed.get("education_requirements", []):
        db.add(JobRequirement(job_id=job.id, requirement_type="education", description=edu))

    db.commit()
    db.refresh(job)
    return job
