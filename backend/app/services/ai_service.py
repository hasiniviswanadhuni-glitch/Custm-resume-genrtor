import json
import logging
from typing import Dict, List, Any, Optional
import httpx
from backend.app.config import settings
from backend.app.services.evidence_validator import evidence_validator

logger = logging.getLogger(__name__)

class AIService:
    """
    Evidence-Grounded AI Suggestion Engine.
    Generates explainable, verifiable suggestions grounded strictly in candidate profile facts.
    Includes:
    - Summary tailoring
    - Skill prioritization & ordering
    - Project relevance reordering & bullet refinement
    - Missing skill learning advisory
    Supports Gemini API, OpenAI API, and High-Precision Deterministic Engine.
    """

    def generate_suggestions(
        self,
        profile_data: Dict[str, Any],
        parsed_job: Dict[str, Any],
        match_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Orchestrates suggestion generation. Runs deterministic evidence engine,
        optionally enriched by Gemini/OpenAI if API keys are configured.
        """
        # 1. Generate grounded deterministic baseline suggestions
        suggestions = self._generate_grounded_deterministic_suggestions(
            profile_data, parsed_job, match_analysis
        )

        # 2. If NVIDIA NIM API key is provided, optionally refine suggestions via low-latency LLM
        if settings.NVIDIA_API_KEY and settings.AI_PROVIDER in ["hybrid", "nvidia"]:
            try:
                suggestions = self._enrich_with_nvidia_nim(
                    suggestions, profile_data, parsed_job, match_analysis
                )
            except Exception as e:
                logger.warning(f"NVIDIA NIM enrichment skipped/failed, using deterministic baseline: {e}")

        # 3. Validate every suggestion against fact preservation rules (Zero Hallucination Guard)
        candidate_facts = evidence_validator.extract_candidate_facts(profile_data)
        missing_skills = [
            m["requirement_name"] for m in match_analysis.get("missing_requirements", [])
            if m.get("requirement_type") == "technical_skill"
        ]

        validated_suggestions = []
        for sug in suggestions:
            is_valid, violations = evidence_validator.validate_suggestion(
                sug["suggested_text"],
                sug["target_section"],
                candidate_facts,
                missing_skills
            )
            if is_valid:
                validated_suggestions.append(sug)
            else:
                logger.warning(f"Suggestion sanitized due to violations: {violations}")
                sug["suggested_text"] = evidence_validator.sanitize_suggestion(sug["suggested_text"], violations)
                sug["reason"] += " (Sanitized to strictly maintain candidate factual accuracy)."
                validated_suggestions.append(sug)

        return validated_suggestions

    def _enrich_with_nvidia_nim(
        self,
        base_suggestions: List[Dict[str, Any]],
        profile_data: Dict[str, Any],
        parsed_job: Dict[str, Any],
        match_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Calls NVIDIA NIM low-latency endpoint (e.g. meta/llama-3.1-8b-instruct)
        to stylistically sharpen summary and project bullet suggestions.
        """
        headers = {
            "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }

        # Example: Refine summary suggestion via low-latency LLM
        for s in base_suggestions:
            if s["target_section"] == "summary":
                prompt = (
                    f"You are an ATS resume editor. Rewrite the candidate's professional summary for the target job.\n"
                    f"TARGET JOB: {parsed_job.get('job_title')}\n"
                    f"CANDIDATE EXISTING SUMMARY: {profile_data.get('professional_summary')}\n"
                    f"CANDIDATE VERIFIED SKILLS: {', '.join([sk.get('name', '') for sk in profile_data.get('skills', [])])}\n"
                    f"RULES:\n"
                    f"1. Only use facts, skills, and background provided above.\n"
                    f"2. DO NOT invent employers, years, degrees, or unmentioned technologies.\n"
                    f"3. Output ONLY the rewritten 2-3 sentence summary."
                )
                payload = {
                    "model": settings.NVIDIA_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 150
                }
                with httpx.Client(timeout=4.0) as client:
                    resp = client.post(
                        f"{settings.NVIDIA_BASE_URL}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    if resp.status_code == 200:
                        content = resp.json()["choices"][0]["message"]["content"].strip()
                        if content and len(content) > 30:
                            s["suggested_text"] = content
                            s["reason"] += " (Polished via NVIDIA NIM Llama 3.1 8B)."
                break

        return base_suggestions

    def _generate_grounded_deterministic_suggestions(
        self,
        profile_data: Dict[str, Any],
        parsed_job: Dict[str, Any],
        match_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        suggestions = []

        job_title = parsed_job.get("job_title", "Target Role")
        tech_reqs = parsed_job.get("technical_skills", [])
        exact_matches = match_analysis.get("exact_matches", [])
        missing_reqs = match_analysis.get("missing_requirements", [])

        # 1. Summary Suggestion (Tailoring without hallucination)
        current_summary = profile_data.get("professional_summary") or ""
        exact_tech_names = [m["requirement_name"] for m in exact_matches if m["requirement_type"] == "technical_skill"]
        top_skills = exact_tech_names[:3] if exact_tech_names else [s.get("name", "") for s in profile_data.get("skills", [])][:3]

        skills_phrase = ", ".join(top_skills) if top_skills else "software engineering principles"
        edu_list = profile_data.get("education", [])
        degree_name = edu_list[0].get("degree", "Computer Science") if edu_list else "Software Engineering"

        suggested_summary = (
            f"Results-driven {degree_name} professional specializing in {skills_phrase}. "
            f"Passionate about applying proven background in {skills_phrase} to contribute effectively to {job_title} initiatives."
        )

        suggestions.append({
            "target_section": "summary",
            "target_item_id": "summary",
            "original_text": current_summary,
            "suggested_text": suggested_summary,
            "reason": f"Aligns your opening statement with the target '{job_title}' position while highlighting verified core competencies.",
            "job_requirement": f"Target Position: {job_title}",
            "candidate_evidence": f"Candidate verified skills ({skills_phrase}) and education ({degree_name}).",
            "confidence_score": 0.95,
            "status": "pending"
        })

        # 2. Skill Prioritization Suggestion
        candidate_skills = profile_data.get("skills", [])
        if candidate_skills and exact_tech_names:
            first_skill = candidate_skills[0].get("name", "") if isinstance(candidate_skills[0], dict) else candidate_skills[0].name
            if first_skill not in exact_tech_names:
                high_priority_skill = exact_tech_names[0]
                suggestions.append({
                    "target_section": "skills",
                    "target_item_id": "skills_order",
                    "original_text": f"Skills section currently starts with: {first_skill}",
                    "suggested_text": f"Prioritize verified high-match skills: {', '.join(exact_tech_names[:5])}",
                    "reason": f"'{high_priority_skill}' is high-priority for {job_title}. Placing it prominently captures ATS and recruiter attention.",
                    "job_requirement": f"Key Technical Requirement: {high_priority_skill}",
                    "candidate_evidence": f"Candidate possesses verified skill '{high_priority_skill}' in profile.",
                    "confidence_score": 0.92,
                    "status": "pending"
                })

        # 3. Project Reordering & Bullet Suggestion
        candidate_projects = profile_data.get("projects", [])
        if candidate_projects:
            # Find project with highest overlap with target job skills
            scored_projects = []
            for idx, p in enumerate(candidate_projects):
                p_techs = {t.lower() for t in p.get("technologies", [])}
                overlap = len(p_techs.intersection({t.lower() for t in tech_reqs}))
                scored_projects.append((overlap, idx, p))

            scored_projects.sort(key=lambda x: x[0], reverse=True)
            best_overlap, best_idx, best_proj = scored_projects[0]

            if best_overlap > 0 and best_idx != 0:
                p_title = best_proj.get("title", "")
                p_techs_str = ", ".join(best_proj.get("technologies", []))
                suggestions.append({
                    "target_section": "projects",
                    "target_item_id": best_proj.get("id", f"proj_{best_idx}"),
                    "original_text": f"Project '{p_title}' is currently ranked #{best_idx + 1}",
                    "suggested_text": f"Move '{p_title}' to the top of your Projects section.",
                    "reason": f"This project directly implements {best_overlap} requirement(s) requested by the job ({p_techs_str}).",
                    "job_requirement": f"Job Technical Requirements: {p_techs_str}",
                    "candidate_evidence": f"Candidate built '{p_title}' utilizing {p_techs_str}.",
                    "confidence_score": 0.94,
                    "status": "pending"
                })

            # Check bullets for action verbs and clarity without fabricating numbers
            for p in candidate_projects:
                bullets = p.get("bullets", [])
                p_title = p.get("title", "")
                for b_idx, bullet in enumerate(bullets):
                    if len(bullet.split()) < 7 or not any(bullet.lower().startswith(v) for v in ["developed", "engineered", "built", "implemented", "designed", "architected"]):
                        refined_bullet = f"Engineered and deployed {bullet.lower().lstrip('developed ').lstrip('built ')}"
                        suggestions.append({
                            "target_section": "projects",
                            "target_item_id": f"{p.get('id', p_title)}_b{b_idx}",
                            "original_text": bullet,
                            "suggested_text": refined_bullet,
                            "reason": "Strengthens bullet phrasing with high-impact action verb while preserving the factual scope.",
                            "job_requirement": "Clear demonstration of engineering execution",
                            "candidate_evidence": f"Original project bullet from '{p_title}': '{bullet}'",
                            "confidence_score": 0.88,
                            "status": "pending"
                        })
                        break # Limit to 1 refined bullet per project to prevent overwhelm

        # 4. Missing Skill Guidance (Never invent, always advise learning)
        missing_tech = [m["requirement_name"] for m in missing_reqs if m.get("requirement_type") == "technical_skill"]
        for missing in missing_tech[:2]: # Top 2 missing skills
            suggestions.append({
                "target_section": "skills",
                "target_item_id": f"missing_{missing.lower()}",
                "original_text": None,
                "suggested_text": f"Skill Gap Advisory: Target job highlights '{missing}'. If you have completed personal labs or coursework in '{missing}', add it; otherwise, consider exploring foundational tutorials in '{missing}'.",
                "reason": f"'{missing}' is requested in target job description, but absent from candidate profile. The system refuses to fabricate this skill, upholding candidate honesty.",
                "job_requirement": f"Requested Skill: {missing}",
                "candidate_evidence": "No evidence found in candidate profile. Preserved fact integrity.",
                "confidence_score": 0.98,
                "status": "pending"
            })

        return suggestions

ai_service = AIService()
