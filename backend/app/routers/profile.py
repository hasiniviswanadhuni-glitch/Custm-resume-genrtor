from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.profile import (
    Profile, Education, Skill, Project, Experience, Certification, Achievement
)
from backend.app.schemas.profile import (
    ProfileCreate, ProfileUpdate, ProfileResponse,
    EducationCreate, SkillCreate, ProjectCreate, ExperienceCreate, CertificationCreate, AchievementCreate
)

router = APIRouter(prefix="/profile", tags=["Master Profile"])

@router.get("", response_model=ProfileResponse)
def get_master_profile(user_id: str = "default-user-id", db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        # Auto-create empty profile
        profile = Profile(
            user_id=user_id,
            full_name="Alex Morgan",
            email="alex.morgan@example.com",
            phone="+1 (555) 234-5678",
            location="San Francisco, CA",
            linkedin_url="linkedin.com/in/alexmorgan",
            github_url="github.com/alexmorgan",
            professional_summary="Passionate software engineer skilled in Python, TypeScript, and modern web application development with a focus on high-reliability systems."
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.post("", response_model=ProfileResponse)
def create_master_profile(profile_in: ProfileCreate, db: Session = Depends(get_db)):
    existing = db.query(Profile).filter(Profile.user_id == profile_in.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists for this user. Use PUT to update.")

    profile = Profile(
        user_id=profile_in.user_id,
        full_name=profile_in.full_name,
        email=profile_in.email,
        phone=profile_in.phone,
        location=profile_in.location,
        linkedin_url=profile_in.linkedin_url,
        github_url=profile_in.github_url,
        portfolio_url=profile_in.portfolio_url,
        professional_summary=profile_in.professional_summary
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    if profile_in.education:
        for edu in profile_in.education:
            db.add(Education(profile_id=profile.id, **edu.model_dump()))
    if profile_in.skills:
        for sk in profile_in.skills:
            db.add(Skill(profile_id=profile.id, **sk.model_dump()))
    if profile_in.projects:
        for p in profile_in.projects:
            db.add(Project(profile_id=profile.id, **p.model_dump()))
    if profile_in.experience:
        for exp in profile_in.experience:
            db.add(Experience(profile_id=profile.id, **exp.model_dump()))
    if profile_in.certifications:
        for c in profile_in.certifications:
            db.add(Certification(profile_id=profile.id, **c.model_dump()))
    if profile_in.achievements:
        for a in profile_in.achievements:
            db.add(Achievement(profile_id=profile.id, **a.model_dump()))

    db.commit()
    db.refresh(profile)
    return profile

@router.put("", response_model=ProfileResponse)
def update_master_profile(profile_update: ProfileUpdate, user_id: str = "default-user-id", db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Master profile not found")

    for field, val in profile_update.model_dump(exclude_unset=True).items():
        setattr(profile, field, val)

    db.commit()
    db.refresh(profile)
    return profile

@router.post("/seed-demo", response_model=ProfileResponse)
def seed_demo_profile(user_id: str = "default-user-id", db: Session = Depends(get_db)):
    """
    Seeds a rich, realistic candidate profile for immediate evaluation and testing.
    """
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if profile:
        db.delete(profile)
        db.commit()

    profile = Profile(
        user_id=user_id,
        full_name="Alex Morgan",
        email="alex.morgan@example.com",
        phone="+1 (555) 234-5678",
        location="Seattle, WA",
        linkedin_url="https://linkedin.com/in/alexmorgan-dev",
        github_url="https://github.com/alexmorgan",
        portfolio_url="https://alexmorgan.dev",
        professional_summary="Detail-oriented Software Engineering graduate with strong foundations in Python, TypeScript, React, and RESTful API architecture. Proven experience building scalable web applications and machine learning prototypes through academic and internship projects."
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    # Education
    db.add(Education(
        profile_id=profile.id,
        institution="University of Washington",
        degree="Bachelor of Science",
        field_of_study="Computer Science",
        start_date="2020",
        end_date="2024",
        gpa="3.85 / 4.0",
        honors="Dean's List (2021-2024), Cum Laude"
    ))

    # Core Skills
    skills_data = [
        ("Python", "technical", "advanced"),
        ("TypeScript", "technical", "intermediate"),
        ("React", "technical", "advanced"),
        ("FastAPI", "technical", "intermediate"),
        ("SQL", "technical", "advanced"),
        ("PostgreSQL", "technical", "intermediate"),
        ("Git", "tool", "advanced"),
        ("REST API", "technical", "advanced"),
        ("Machine Learning", "domain", "intermediate"),
        ("scikit-learn", "tool", "intermediate"),
        ("Tailwind CSS", "technical", "intermediate"),
        ("Agile", "soft", "intermediate"),
        ("Problem Solving", "soft", "advanced")
    ]
    for name, cat, prof in skills_data:
        db.add(Skill(profile_id=profile.id, name=name, category=cat, proficiency_level=prof))

    # Projects
    db.add(Project(
        profile_id=profile.id,
        title="Student Performance Predictive Engine",
        role="Lead Developer",
        description="End-to-end machine learning system evaluating historical student academic trends.",
        technologies=["Python", "scikit-learn", "Pandas", "FastAPI", "React"],
        bullets=[
            "Developed predictive classification pipeline utilizing Python and scikit-learn achieving 89% accuracy.",
            "Architected RESTful FastAPI endpoints to serve real-time predictions with sub-100ms latency.",
            "Engineered responsive React dashboard displaying interactive visual analytics and feature importance charts."
        ],
        repo_url="https://github.com/alexmorgan/student-performance-ml",
        start_date="Jan 2024",
        end_date="May 2024"
    ))

    db.add(Project(
        profile_id=profile.id,
        title="Inventory & Order Management Platform",
        role="Full Stack Engineer",
        description="Scalable inventory tracking web platform with transactional consistency.",
        technologies=["TypeScript", "React", "Node.js", "PostgreSQL", "SQL"],
        bullets=[
            "Constructed relational database schema in PostgreSQL supporting automated stock auditing and order reconciliation.",
            "Designed modular React user interfaces using TypeScript for order placement and supplier catalog search.",
            "Integrated transactional SQL queries to prevent overselling anomalies during peak concurrency."
        ],
        repo_url="https://github.com/alexmorgan/inventory-manager",
        start_date="Aug 2023",
        end_date="Dec 2023"
    ))

    # Experience / Internships
    db.add(Experience(
        profile_id=profile.id,
        company="NexTech Solutions",
        position="Software Engineering Intern",
        location="Seattle, WA",
        start_date="Jun 2023",
        end_date="Sep 2023",
        is_current=False,
        description="Collaborated with core platform team on internal developer tools and API integrations.",
        bullets=[
            "Engineered automated data ingestion scripts in Python saving 15 manual hours weekly.",
            "Built unit and integration test suites using pytest increasing code coverage from 68% to 84%.",
            "Participated in daily agile standups, code reviews, and cross-functional feature planning."
        ],
        technologies=["Python", "FastAPI", "pytest", "Git", "PostgreSQL"],
        is_internship=True
    ))

    # Certifications
    db.add(Certification(
        profile_id=profile.id,
        name="Meta Front-End Developer Specialization",
        issuer="Coursera / Meta",
        issue_date="2023",
        credential_id="META-FE-9821"
    ))

    # Achievements
    db.add(Achievement(
        profile_id=profile.id,
        title="1st Place — UW Annual Hackathon 2023",
        description="Built an accessible campus navigation application for visually impaired students within 36 hours.",
        date="Nov 2023"
    ))

    db.commit()
    db.refresh(profile)
    return profile
