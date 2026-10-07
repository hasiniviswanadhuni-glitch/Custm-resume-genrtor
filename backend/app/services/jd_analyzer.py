import re
from typing import Dict, List, Any

# Comprehensive domain skill taxonomies
TECHNICAL_SKILLS_TAXONOMY = {
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang", "rust", "php", "ruby", "swift", "kotlin",
    "react", "next.js", "vue", "angular", "node.js", "express", "django", "fastapi", "flask", "spring boot", "asp.net",
    "sql", "postgresql", "mysql", "sqlite", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb",
    "docker", "kubernetes", "aws", "azure", "gcp", "google cloud", "terraform", "ci/cd", "github actions", "gitlab",
    "git", "linux", "rest api", "graphql", "grpc", "microservices", "html", "css", "tailwind", "bootstrap",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "scikit-learn", "pandas",
    "numpy", "tableau", "power bi", "spark", "hadoop", "kafka", "airflow", "pytest", "jest", "cypress", "selenium"
}

SOFT_SKILLS_TAXONOMY = {
    "communication", "teamwork", "collaboration", "leadership", "problem solving", "critical thinking",
    "adaptability", "time management", "agile", "scrum", "mentorship", "presentation", "attention to detail",
    "analytical thinking", "stakeholder management", "project management"
}

DEGREE_KEYWORDS = {
    "bachelor", "bachelors", "b.tech", "b.e", "b.s", "bs", "master", "masters", "m.tech", "m.s", "ms",
    "phd", "computer science", "information technology", "electrical engineering", "data science", "stem"
}

class JobDescriptionAnalyzer:
    """
    Multi-stage NLP and pattern-based extractor for Job Descriptions.
    Extracts skills, requirements, education, responsibilities, and keywords.
    """

    def analyze(self, raw_text: str, title: str = "Target Position", company: str = "") -> Dict[str, Any]:
        cleaned_text = raw_text.strip()
        text_lower = cleaned_text.lower()

        # 1. Extract Job Title (if not explicitly provided or generic)
        extracted_title = title
        if not title or title.lower() in ["target position", "job", "position"]:
            first_line = cleaned_text.split("\n")[0].strip()
            if len(first_line) < 80:
                extracted_title = first_line

        # 2. Extract Technical Skills
        found_tech_skills = set()
        for skill in TECHNICAL_SKILLS_TAXONOMY:
            # Word boundary regex for exact matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_tech_skills.add(skill.title() if len(skill) > 3 and skill != "next.js" else skill.upper() if len(skill) <= 3 else skill)

        # 3. Extract Soft Skills
        found_soft_skills = set()
        for soft in SOFT_SKILLS_TAXONOMY:
            pattern = r'\b' + re.escape(soft) + r'\b'
            if re.search(pattern, text_lower):
                found_soft_skills.add(soft.title())

        # 4. Extract Required vs Preferred Skills based on section headers
        required_skills = []
        preferred_skills = []

        req_section_match = re.search(
            r'(?:requirements|qualifications|what you need|must have|minimum qualifications)[\s\S]*?(?:preferred|nice to have|bonus|responsibilities|\Z)',
            cleaned_text,
            re.IGNORECASE
        )
        pref_section_match = re.search(
            r'(?:preferred qualifications|nice to have|plus|bonus points)[\s\S]*?(?:responsibilities|benefits|\Z)',
            cleaned_text,
            re.IGNORECASE
        )

        req_text = req_section_match.group(0).lower() if req_section_match else text_lower
        pref_text = pref_section_match.group(0).lower() if pref_section_match else ""

        for skill in found_tech_skills:
            skill_lower = skill.lower()
            if pref_text and re.search(r'\b' + re.escape(skill_lower) + r'\b', pref_text):
                preferred_skills.append(skill)
            else:
                required_skills.append(skill)

        # 5. Extract Education Requirements
        education_reqs = []
        edu_patterns = [
            r"bachelor['’]?s?(?:\s+degree)?(?:\s+in\s+[\w\s,]+)?",
            r"master['’]?s?(?:\s+degree)?(?:\s+in\s+[\w\s,]+)?",
            r"ph\.?d\.?(?:\s+in\s+[\w\s,]+)?",
            r"degree in computer science[,\w\s]*",
            r"b\.?tech[,\w\s]*"
        ]
        for pattern in edu_patterns:
            matches = re.finditer(pattern, cleaned_text, re.IGNORECASE)
            for m in matches:
                matched_phrase = m.group(0).strip().capitalize()
                if len(matched_phrase) > 5 and matched_phrase not in education_reqs:
                    education_reqs.append(matched_phrase)

        if not education_reqs:
            # Fallback check
            if "bachelor" in text_lower or "degree in computer science" in text_lower or "b.s." in text_lower:
                education_reqs.append("Bachelor's degree in Computer Science or related STEM field")

        # 6. Extract Experience Requirements (e.g., "3+ years of experience", "2-4 years in Python")
        exp_patterns = [
            r'(\d+\+?\s*(?:to|-)\s*\d+\s+years?(?:\s+of)?(?:\s+experience)?[^.\n]*)',
            r'(\d+\+?\s+years?(?:\s+of)?(?:\s+experience)?[^.\n]*)'
        ]
        experience_reqs = []
        for pat in exp_patterns:
            for match in re.finditer(pat, cleaned_text, re.IGNORECASE):
                exp_text = match.group(0).strip()
                if len(exp_text) > 5 and exp_text not in experience_reqs:
                    experience_reqs.append(exp_text)

        # 7. Extract Responsibilities
        responsibilities = []
        resp_section_match = re.search(
            r'(?:responsibilities|what you will do|day to day|key duties)[\s\S]*?(?:requirements|qualifications|benefits|\Z)',
            cleaned_text,
            re.IGNORECASE
        )
        if resp_section_match:
            lines = resp_section_match.group(0).split("\n")
            for line in lines[1:]: # skip header
                cleaned_line = line.strip().lstrip("•-* ").strip()
                if len(cleaned_line) > 15 and not any(kw in cleaned_line.lower() for kw in ["requirement", "qualification"]):
                    responsibilities.append(cleaned_line)
                    if len(responsibilities) >= 6:
                        break

        # 8. Keywords Extraction (Top domain phrases)
        keywords = list(found_tech_skills) + list(found_soft_skills)
        # Deduplicate preserving order
        unique_keywords = []
        for kw in keywords:
            if kw not in unique_keywords:
                unique_keywords.append(kw)

        # 9. Domain Identification
        domain_requirements = []
        if any(term in text_lower for term in ["frontend", "react", "css", "ui", "ux"]):
            domain_requirements.append("Frontend Web Development")
        if any(term in text_lower for term in ["backend", "api", "database", "microservices"]):
            domain_requirements.append("Backend Systems & API Architecture")
        if any(term in text_lower for term in ["machine learning", "nlp", "ai", "model"]):
            domain_requirements.append("AI & Machine Learning")
        if any(term in text_lower for term in ["cloud", "devops", "docker", "kubernetes", "aws", "ci/cd"]):
            domain_requirements.append("Cloud & DevOps Infrastructure")

        return {
            "job_title": extracted_title,
            "company": company,
            "required_skills": sorted(list(set(required_skills))),
            "preferred_skills": sorted(list(set(preferred_skills))),
            "technical_skills": sorted(list(found_tech_skills)),
            "soft_skills": sorted(list(found_soft_skills)),
            "education_requirements": education_reqs,
            "experience_requirements": experience_reqs,
            "responsibilities": responsibilities[:6],
            "keywords": unique_keywords[:15],
            "domain_requirements": domain_requirements
        }

jd_analyzer = JobDescriptionAnalyzer()
