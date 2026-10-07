import copy
from typing import Dict, List, Any
from backend.app.schemas.resume import TailoredResumeContent, TailoredProjectItem, TailoredExperienceItem

class ResumeCustomizer:
    """
    Derives job-specific customized resumes based on:
    - Master Profile (Never modified)
    - Target Job Requirements
    - User-Approved/Edited AI Suggestions
    """

    def customize(
        self,
        profile_data: Dict[str, Any],
        parsed_job: Dict[str, Any],
        match_analysis: Dict[str, Any],
        approved_suggestions: List[Dict[str, Any]],
        ats_score: float,
        ats_breakdown: Dict[str, Any]
    ) -> Dict[str, Any]:
        # 1. Base personal information
        full_name = profile_data.get("full_name", "")
        email = profile_data.get("email", "")
        phone = profile_data.get("phone", "")
        location = profile_data.get("location", "")
        linkedin_url = profile_data.get("linkedin_url", "")
        github_url = profile_data.get("github_url", "")
        portfolio_url = profile_data.get("portfolio_url", "")

        # 2. Professional Summary Customization
        summary = profile_data.get("professional_summary") or ""
        # Check if an accepted/edited suggestion exists for summary
        for sug in approved_suggestions:
            if sug.get("target_section") == "summary" and sug.get("status") in ["accepted", "edited"]:
                summary = sug.get("edited_text") or sug.get("suggested_text")
                break

        # 3. Skills Prioritization
        tech_reqs = {t.lower() for t in parsed_job.get("technical_skills", [])}
        raw_skills = profile_data.get("skills", [])
        
        # Split into matching skills and other skills
        matching_skills = []
        other_skills = []
        for s in raw_skills:
            s_name = s.get("name", "") if isinstance(s, dict) else s.name
            s_cat = s.get("category", "technical") if isinstance(s, dict) else s.category
            s_prof = s.get("proficiency_level", "intermediate") if isinstance(s, dict) else s.proficiency_level
            
            skill_dict = {"name": s_name, "category": s_cat, "proficiency_level": s_prof}
            if s_name.lower() in tech_reqs:
                matching_skills.append(skill_dict)
            else:
                other_skills.append(skill_dict)

        # Prioritized skills: Job-matched skills first!
        prioritized_skills = matching_skills + other_skills

        # 4. Projects Reordering & Bullet Application
        raw_projects = copy.deepcopy(profile_data.get("projects", []))
        tailored_projects = []

        for p in raw_projects:
            p_dict = p if isinstance(p, dict) else {
                "id": p.id, "title": p.title, "role": p.role, "description": p.description,
                "technologies": p.technologies or [], "bullets": p.bullets or [],
                "live_url": p.live_url, "repo_url": p.repo_url, "start_date": p.start_date, "end_date": p.end_date
            }
            
            # Check overlap score
            p_tech_set = {t.lower() for t in p_dict.get("technologies", [])}
            overlap = len(p_tech_set.intersection(tech_reqs))
            relevance = round(min(100.0, overlap * 30.0 + (40.0 if overlap > 0 else 20.0)), 1)
            p_dict["relevance_score"] = relevance

            # Check if any approved suggestion modifies this project's bullets
            bullets = list(p_dict.get("bullets", []))
            for sug in approved_suggestions:
                if sug.get("target_section") == "projects" and sug.get("status") in ["accepted", "edited"]:
                    target_id = sug.get("target_item_id", "")
                    # If this suggestion targets this project
                    if p_dict.get("id") and p_dict.get("id") in target_id or p_dict.get("title") in target_id:
                        orig = sug.get("original_text")
                        new_text = sug.get("edited_text") or sug.get("suggested_text")
                        if orig in bullets:
                            b_idx = bullets.index(orig)
                            bullets[b_idx] = new_text

            p_dict["bullets"] = bullets
            tailored_projects.append(TailoredProjectItem(**p_dict))

        # Sort projects by relevance score descending
        tailored_projects.sort(key=lambda x: x.relevance_score or 0.0, reverse=True)

        # 5. Experience Tailoring
        raw_exp = copy.deepcopy(profile_data.get("experience", []))
        tailored_experience = []

        for e in raw_exp:
            e_dict = e if isinstance(e, dict) else {
                "id": e.id, "company": e.company, "position": e.position, "location": e.location,
                "start_date": e.start_date, "end_date": e.end_date, "is_current": e.is_current,
                "description": e.description, "bullets": e.bullets or [], "technologies": e.technologies or [],
                "is_internship": e.is_internship
            }
            e_tech_set = {t.lower() for t in e_dict.get("technologies", [])}
            overlap = len(e_tech_set.intersection(tech_reqs))
            relevance = round(min(100.0, overlap * 25.0 + 50.0), 1)
            e_dict["relevance_score"] = relevance
            tailored_experience.append(TailoredExperienceItem(**e_dict))

        # 6. Education, Certifications, Achievements
        raw_edu = profile_data.get("education", [])
        edu_list = [e if isinstance(e, dict) else {
            "institution": e.institution, "degree": e.degree, "field_of_study": e.field_of_study,
            "start_date": e.start_date, "end_date": e.end_date, "gpa": e.gpa, "honors": e.honors
        } for e in raw_edu]

        raw_certs = profile_data.get("certifications", [])
        cert_list = [c if isinstance(c, dict) else {
            "name": c.name, "issuer": c.issuer, "issue_date": c.issue_date,
            "expiration_date": c.expiration_date, "credential_id": c.credential_id, "credential_url": c.credential_url
        } for c in raw_certs]

        raw_achieve = profile_data.get("achievements", [])
        achieve_list = [a if isinstance(a, dict) else {
            "title": a.title, "description": a.description, "date": a.date
        } for a in raw_achieve]

        applied_count = sum(1 for s in approved_suggestions if s.get("status") in ["accepted", "edited"])

        tailored_content = TailoredResumeContent(
            full_name=full_name,
            email=email,
            phone=phone,
            location=location,
            linkedin_url=linkedin_url,
            github_url=github_url,
            portfolio_url=portfolio_url,
            professional_summary=summary,
            skills=prioritized_skills,
            projects=tailored_projects,
            experience=tailored_experience,
            education=edu_list,
            certifications=cert_list,
            achievements=achieve_list,
            applied_suggestions_count=applied_count
        )

        return tailored_content.model_dump()

resume_customizer = ResumeCustomizer()
