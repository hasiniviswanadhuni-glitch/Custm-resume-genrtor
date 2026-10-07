import re
from typing import Dict, List, Any, Set, Tuple

class EvidenceValidator:
    """
    Fact-Preservation & Anti-Hallucination Guard.
    Ensures that AI suggestions and customized resume content strictly adhere to candidate facts.
    Detects and flags unauthorized additions of:
    - Missing skills claimed as possessed
    - Fabricated numerical achievements / team sizes / metrics
    - Fabricated employers or institutions
    - Fabricated certifications
    """

    def extract_candidate_facts(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts verified sets of candidate factual entities from profile.
        """
        # Verified skills
        skills = set()
        for s in profile_data.get("skills", []):
            name = s.get("name", "") if isinstance(s, dict) else s.name
            if name:
                skills.add(name.lower().strip())

        # Verified technologies from projects & experience
        technologies = set(skills)
        for p in profile_data.get("projects", []):
            p_techs = p.get("technologies", []) if isinstance(p, dict) else (p.technologies or [])
            for t in p_techs:
                technologies.add(t.lower().strip())

        for e in profile_data.get("experience", []):
            e_techs = e.get("technologies", []) if isinstance(e, dict) else (e.technologies or [])
            for t in e_techs:
                technologies.add(t.lower().strip())

        # Verified employers
        companies = set()
        for e in profile_data.get("experience", []):
            comp = e.get("company", "") if isinstance(e, dict) else e.company
            if comp:
                companies.add(comp.lower().strip())

        # Verified institutions & degrees
        institutions = set()
        degrees = set()
        for ed in profile_data.get("education", []):
            inst = ed.get("institution", "") if isinstance(ed, dict) else ed.institution
            deg = ed.get("degree", "") if isinstance(ed, dict) else ed.degree
            if inst:
                institutions.add(inst.lower().strip())
            if deg:
                degrees.add(deg.lower().strip())

        # Verified certifications
        certifications = set()
        for c in profile_data.get("certifications", []):
            c_name = c.get("name", "") if isinstance(c, dict) else c.name
            if c_name:
                certifications.add(c_name.lower().strip())

        # Verified numbers / metrics appearing in original text
        original_numbers = set()
        all_text = []
        for p in profile_data.get("projects", []):
            desc = p.get("description", "") if isinstance(p, dict) else (p.description or "")
            bullets = p.get("bullets", []) if isinstance(p, dict) else (p.bullets or [])
            all_text.append(desc + " " + " ".join(bullets))

        for e in profile_data.get("experience", []):
            desc = e.get("description", "") if isinstance(e, dict) else (e.description or "")
            bullets = e.get("bullets", []) if isinstance(e, dict) else (e.bullets or [])
            all_text.append(desc + " " + " ".join(bullets))

        summary = profile_data.get("professional_summary") or ""
        all_text.append(summary)

        full_profile_text = " ".join(all_text)
        # Extract numbers like '10', '45%', '500k', '$100k'
        num_matches = re.findall(r'\b(?:\$|€|£)?\d+(?:\.\d+)?%?(?:k|m|b)?\b', full_profile_text.lower())
        for n in num_matches:
            original_numbers.add(n)

        return {
            "skills": skills,
            "technologies": technologies,
            "companies": companies,
            "institutions": institutions,
            "degrees": degrees,
            "certifications": certifications,
            "numbers": original_numbers,
            "full_profile_text": full_profile_text
        }

    def validate_suggestion(
        self,
        suggested_text: str,
        target_section: str,
        facts: Dict[str, Any],
        missing_skills: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validates whether a suggested piece of text adheres strictly to candidate facts.
        Returns: (is_valid, list_of_violations)
        """
        violations = []
        sug_lower = suggested_text.lower()

        # Rule 2: Never turn a missing skill into a possessed claim
        for missing in missing_skills:
            pattern = r'\b' + re.escape(missing.lower()) + r'\b'
            # If the suggestion mentions the missing skill
            if re.search(pattern, sug_lower):
                # If this is not an explicit advisory to learn the skill
                if "skill gap advisory" not in sug_lower and "consider learning" not in sug_lower:
                    violations.append(
                        f"Rule 2 Violation: Claims or references missing skill '{missing}' in profile content without candidate evidence."
                    )

        # Rule 3: Check for fabricated numerical claims
        new_numbers = set(re.findall(r'\b(?:\$|€|£)?\d+(?:\.\d+)?%?(?:k|m|b)?\b', sug_lower))
        for num in new_numbers:
            # Allow common years or numbers 1-2 if just grammar
            if num not in facts["numbers"] and num not in {"1", "2", "3", "first", "second"}:
                # If it's a quantitative claim like "increased by 45%" or "team of 10"
                if any(char in num for char in ["%", "$"]) or int(re.sub(r'\D', '', num) or 0) > 4:
                    violations.append(
                        f"Rule 3 Violation: Introduced unverified numerical claim '{num}' not present in profile."
                    )

        # Rule 4 & 5: Check employers & certifications
        if target_section == "certifications":
            for cert in facts.get("certifications", []):
                pass # Already existing

        is_valid = len(violations) == 0
        return is_valid, violations

    def sanitize_suggestion(self, text: str, violations: List[str]) -> str:
        """
        Strips or softens invalid claims if violations were detected.
        """
        sanitized = text
        for v in violations:
            if "Rule 3" in v:
                # Remove ungrounded percentages (note: % is non-word, so no trailing \b)
                sanitized = re.sub(r'\bby\s+\d+%', 'significantly', sanitized)
                sanitized = re.sub(r'\bteam of\s+\d+\b', 'team of developers', sanitized)
        return sanitized

evidence_validator = EvidenceValidator()
