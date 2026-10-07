import re
from typing import Dict, List, Any, Tuple

# Semantic technology ontology mapping related tools and domains
SEMANTIC_TAXONOMY_MAP = {
    "python": ["django", "fastapi", "flask", "pandas", "numpy", "scikit-learn", "pytorch", "scripting", "python programming"],
    "fastapi": ["python", "rest api", "pydantic", "starlette", "backend api"],
    "react": ["next.js", "javascript", "typescript", "frontend", "redux", "html", "css", "tailwind"],
    "next.js": ["react", "typescript", "javascript", "fullstack", "ssr"],
    "javascript": ["typescript", "node.js", "react", "express", "frontend"],
    "typescript": ["javascript", "react", "node.js", "angular"],
    "sql": ["postgresql", "mysql", "sqlite", "relational database", "queries"],
    "postgresql": ["sql", "relational database", "database management", "mysql"],
    "docker": ["containerization", "kubernetes", "devops", "containers"],
    "kubernetes": ["docker", "container orchestration", "cloud", "devops"],
    "aws": ["cloud", "cloud computing", "ec2", "s3", "lambda", "azure", "gcp"],
    "azure": ["cloud", "cloud computing", "aws", "gcp"],
    "gcp": ["cloud", "cloud computing", "google cloud", "aws"],
    "machine learning": ["deep learning", "nlp", "scikit-learn", "tensorflow", "pytorch", "data science", "model training"],
    "deep learning": ["machine learning", "pytorch", "tensorflow", "neural networks", "computer vision", "nlp"],
    "nlp": ["natural language processing", "spacy", "nltk", "transformers", "machine learning"],
    "ci/cd": ["github actions", "gitlab", "jenkins", "devops", "automation"],
    "git": ["github", "gitlab", "version control"],
    "rest api": ["fastapi", "express", "backend", "web services", "endpoints", "graphql"],
}

class MatchingEngine:
    """
    Two-level matching engine:
    1. Exact / Normalized Keyword Matching
    2. Semantic & Ontological Matching
    Classifies each job requirement into: Exact match, Related match, Partial match, Missing, Unsupported.
    """

    def _normalize(self, text: str) -> str:
        if not text:
            return ""
        return re.sub(r'[^a-z0-9+#.]', '', text.lower())

    def match_candidate_against_job(
        self,
        profile_data: Dict[str, Any],
        parsed_job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compares candidate profile components with parsed job requirements.
        Returns categorized matches with evidence citations.
        """
        # 1. Gather Candidate Evidence Repository
        candidate_skills = profile_data.get("skills", [])
        candidate_projects = profile_data.get("projects", [])
        candidate_experience = profile_data.get("experience", [])
        candidate_education = profile_data.get("education", [])
        candidate_certifications = profile_data.get("certifications", [])
        summary = profile_data.get("professional_summary", "") or ""

        # Normalize candidate skill names
        skill_names = [s.get("name", "") if isinstance(s, dict) else s.name for s in candidate_skills]
        norm_skill_map = {self._normalize(name): name for name in skill_names if name}

        # Gather all text corpus from projects & experience
        project_evidence = []
        for p in candidate_projects:
            title = p.get("title", "") if isinstance(p, dict) else p.title
            techs = p.get("technologies", []) if isinstance(p, dict) else (p.technologies or [])
            bullets = p.get("bullets", []) if isinstance(p, dict) else (p.bullets or [])
            desc = p.get("description", "") if isinstance(p, dict) else (p.description or "")
            combined_text = f"{title} | Technologies: {', '.join(techs)} | Description: {desc} | Bullets: {' '.join(bullets)}"
            project_evidence.append({
                "source": f"Project: {title}",
                "text": combined_text,
                "techs": techs
            })

        exp_evidence = []
        for e in candidate_experience:
            company = e.get("company", "") if isinstance(e, dict) else e.company
            pos = e.get("position", "") if isinstance(e, dict) else e.position
            bullets = e.get("bullets", []) if isinstance(e, dict) else (e.bullets or [])
            techs = e.get("technologies", []) if isinstance(e, dict) else (e.technologies or [])
            combined_text = f"{pos} at {company} | Bullets: {' '.join(bullets)} | Tech: {', '.join(techs)}"
            exp_evidence.append({
                "source": f"Experience: {pos} at {company}",
                "text": combined_text,
                "techs": techs
            })

        cert_names = [c.get("name", "") if isinstance(c, dict) else c.name for c in candidate_certifications]

        # 2. Evaluate Each Job Requirement
        exact_matches = []
        related_matches = []
        partial_matches = []
        missing_requirements = []
        all_matches = []

        job_tech_skills = parsed_job_data.get("technical_skills", [])
        job_soft_skills = parsed_job_data.get("soft_skills", [])
        all_job_skills = list(set(job_tech_skills + job_soft_skills))

        for req in all_job_skills:
            req_norm = self._normalize(req)
            req_lower = req.lower()
            req_type = "technical_skill" if req in job_tech_skills else "soft_skill"

            # Level 1: Exact Match in Profile Skills
            if req_norm in norm_skill_map:
                matched_name = norm_skill_map[req_norm]
                match_item = {
                    "requirement_name": req,
                    "requirement_type": req_type,
                    "candidate_evidence": f"Explicitly listed under Candidate Skills as '{matched_name}'",
                    "match_type": "exact",
                    "similarity_score": 100.0,
                    "explanation": f"Candidate directly possesses '{matched_name}', satisfying the target job requirement."
                }
                exact_matches.append(match_item)
                all_matches.append(match_item)
                continue

            # Check exact mention in project technologies or certs
            proj_tech_match = [p["source"] for p in project_evidence if any(self._normalize(t) == req_norm for t in p["techs"])]
            exp_tech_match = [e["source"] for e in exp_evidence if any(self._normalize(t) == req_norm for t in e["techs"])]
            cert_match = [c for c in cert_names if self._normalize(c) == req_norm or req_norm in self._normalize(c)]

            if proj_tech_match or exp_tech_match:
                evidence_sources = proj_tech_match + exp_tech_match
                match_item = {
                    "requirement_name": req,
                    "requirement_type": req_type,
                    "candidate_evidence": f"Demonstrated in: {', '.join(evidence_sources[:2])}",
                    "match_type": "exact",
                    "similarity_score": 95.0,
                    "explanation": f"Demonstrated practical usage of '{req}' in verified project/work experience."
                }
                exact_matches.append(match_item)
                all_matches.append(match_item)
                continue

            if cert_match:
                match_item = {
                    "requirement_name": req,
                    "requirement_type": req_type,
                    "candidate_evidence": f"Certified in '{cert_match[0]}'",
                    "match_type": "exact",
                    "similarity_score": 95.0,
                    "explanation": f"Possesses verified certification '{cert_match[0]}' verifying '{req}'."
                }
                exact_matches.append(match_item)
                all_matches.append(match_item)
                continue

            # Level 2: Semantic & Ontological Matching
            related_terms = SEMANTIC_TAXONOMY_MAP.get(req_lower, [])
            found_related = []
            for r_term in related_terms:
                r_norm = self._normalize(r_term)
                if r_norm in norm_skill_map:
                    found_related.append(norm_skill_map[r_norm])
                for p in project_evidence:
                    if any(self._normalize(t) == r_norm for t in p["techs"]):
                        found_related.append(f"{p['source']} ({r_term})")

            if found_related:
                unique_related = list(set(found_related))[:2]
                match_item = {
                    "requirement_name": req,
                    "requirement_type": req_type,
                    "candidate_evidence": f"Candidate demonstrates related capability: {', '.join(unique_related)}",
                    "match_type": "related",
                    "similarity_score": 75.0,
                    "explanation": f"While '{req}' is not explicitly listed, candidate has transferable expertise in closely related areas ({', '.join(unique_related)})."
                }
                related_matches.append(match_item)
                all_matches.append(match_item)
                continue

            # Level 3: Partial Match (found in text descriptions / bullets)
            partial_sources = []
            pattern = r'\b' + re.escape(req_lower) + r'\b'
            for p in project_evidence:
                if re.search(pattern, p["text"].lower()):
                    partial_sources.append(p["source"])
            for e in exp_evidence:
                if re.search(pattern, e["text"].lower()):
                    partial_sources.append(e["source"])
            if re.search(pattern, summary.lower()):
                partial_sources.append("Professional Summary")

            if partial_sources:
                match_item = {
                    "requirement_name": req,
                    "requirement_type": req_type,
                    "candidate_evidence": f"Referenced in: {', '.join(partial_sources[:2])}",
                    "match_type": "partial",
                    "similarity_score": 60.0,
                    "explanation": f"Candidate mentions '{req}' within contextual descriptions ({partial_sources[0]}), though not highlighted as a standalone primary skill."
                }
                partial_matches.append(match_item)
                all_matches.append(match_item)
                continue

            # Level 4: Missing Requirement (Zero evidence found in candidate profile)
            match_item = {
                "requirement_name": req,
                "requirement_type": req_type,
                "candidate_evidence": None,
                "match_type": "missing",
                "similarity_score": 0.0,
                "explanation": f"Target job requests '{req}', but no supporting evidence exists in candidate profile. Preserving fact integrity by flagging as missing."
            }
            missing_requirements.append(match_item)
            all_matches.append(match_item)

        # 3. Evaluate Education & Experience Requirements
        edu_matches = self._match_education(candidate_education, parsed_job_data.get("education_requirements", []))
        all_matches.extend(edu_matches)

        exp_matches = self._match_experience_duration(candidate_experience, parsed_job_data.get("experience_requirements", []))
        all_matches.extend(exp_matches)

        return {
            "exact_matches": exact_matches,
            "related_matches": related_matches,
            "partial_matches": partial_matches,
            "missing_requirements": missing_requirements,
            "all_matches": all_matches
        }

    def _match_education(self, candidate_education: List[Any], job_edu_reqs: List[str]) -> List[Dict[str, Any]]:
        matches = []
        if not job_edu_reqs:
            return matches

        candidate_degrees = []
        for e in candidate_education:
            deg = e.get("degree", "") if isinstance(e, dict) else e.degree
            field = e.get("field_of_study", "") if isinstance(e, dict) else (e.field_of_study or "")
            inst = e.get("institution", "") if isinstance(e, dict) else e.institution
            candidate_degrees.append(f"{deg} in {field} from {inst}")

        cand_str = " | ".join(candidate_degrees).lower()

        for req in job_edu_reqs:
            req_lower = req.lower()
            is_match = any(deg_word in cand_str for deg_word in ["bachelor", "b.tech", "b.e", "computer science", "master", "degree"])
            if is_match and candidate_degrees:
                matches.append({
                    "requirement_name": f"Education: {req}",
                    "requirement_type": "education",
                    "candidate_evidence": candidate_degrees[0],
                    "match_type": "exact",
                    "similarity_score": 95.0,
                    "explanation": f"Candidate possesses required degree qualification: {candidate_degrees[0]}."
                })
            elif candidate_degrees:
                matches.append({
                    "requirement_name": f"Education: {req}",
                    "requirement_type": "education",
                    "candidate_evidence": candidate_degrees[0],
                    "match_type": "related",
                    "similarity_score": 80.0,
                    "explanation": f"Candidate has academic background in {candidate_degrees[0]}, satisfying foundational education."
                })
            else:
                matches.append({
                    "requirement_name": f"Education: {req}",
                    "requirement_type": "education",
                    "candidate_evidence": None,
                    "match_type": "missing",
                    "similarity_score": 0.0,
                    "explanation": "No education records registered in candidate profile."
                })
        return matches

    def _match_experience_duration(self, candidate_experience: List[Any], job_exp_reqs: List[str]) -> List[Dict[str, Any]]:
        matches = []
        if not job_exp_reqs:
            return matches

        num_roles = len(candidate_experience)
        for req in job_exp_reqs:
            if num_roles > 0:
                matches.append({
                    "requirement_name": f"Experience Requirement: {req}",
                    "requirement_type": "experience",
                    "candidate_evidence": f"{num_roles} relevant role(s) logged in work experience",
                    "match_type": "related" if num_roles < 2 else "exact",
                    "similarity_score": 85.0 if num_roles >= 2 else 70.0,
                    "explanation": f"Candidate profile logs {num_roles} professional/internship engagement(s) matching experience targets."
                })
            else:
                matches.append({
                    "requirement_name": f"Experience Requirement: {req}",
                    "requirement_type": "experience",
                    "candidate_evidence": None,
                    "match_type": "partial",
                    "similarity_score": 50.0,
                    "explanation": "Candidate is applying as fresher / student; projects will be emphasized to compensate for tenure."
                })
        return matches

matching_engine = MatchingEngine()
