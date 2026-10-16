"""Job Description (JD) vs Resume Matching Engine.

Computes skill overlap, keyword similarity, identifies missing critical skills,
and provides targeted resume tailoring suggestions.
"""

import re
import math
from collections import Counter
from typing import Dict, List, Any, Set
from app.taxonomy import SKILLS_TAXONOMY


class JobMatcher:
    """Matches a parsed resume against a job description."""

    def __init__(self, resume_text: str, resume_skills: List[str], jd_text: str):
        self.resume_text = resume_text or ""
        self.resume_skills_set: Set[str] = {s.lower() for s in resume_skills}
        self.jd_text = jd_text or ""
        self.jd_words = re.findall(r'\b[a-zA-Z0-9+#.-]+\b', self.jd_text.lower())

    def match(self) -> Dict[str, Any]:
        """Perform comparison between resume and job description."""
        if not self.jd_text.strip():
            return {
                "has_job_description": False,
                "match_score": None,
                "matching_skills": [],
                "missing_skills": [],
                "keyword_overlap_score": 0,
                "recommendations": []
            }

        # 1. Extract skills from JD
        jd_skills_by_cat, jd_skills_list = self._extract_jd_skills()
        jd_skills_set = {s.lower() for s in jd_skills_list}

        # 2. Compare skills
        matching_skills = []
        missing_skills = []

        for skill in jd_skills_list:
            if skill.lower() in self.resume_skills_set:
                matching_skills.append(skill)
            else:
                missing_skills.append(skill)

        # 3. Compute skill coverage ratio
        skill_coverage = 0.0
        if jd_skills_list:
            skill_coverage = len(matching_skills) / len(jd_skills_list)
        else:
            # If no specific taxonomy skills found in JD, use textual similarity
            skill_coverage = 0.5

        # 4. Compute TF-IDF / Token Cosine Similarity
        cosine_sim = self._calculate_cosine_similarity(self.resume_text, self.jd_text)

        # 5. Composite Match Score (0 - 100)
        # 65% skill overlap + 35% general textual/keyword similarity
        composite_score = round(((skill_coverage * 0.65) + (cosine_sim * 0.35)) * 100, 1)
        composite_score = max(5.0, min(99.0, composite_score))

        # 6. Extract top JD keywords that are missing in resume
        missing_keywords = self._extract_missing_important_keywords()

        # 7. Tailoring recommendations
        recs = self._generate_tailoring_tips(
            match_score=composite_score,
            missing_skills=missing_skills,
            missing_keywords=missing_keywords
        )

        return {
            "has_job_description": True,
            "match_score": composite_score,
            "match_grade": self._get_match_grade(composite_score),
            "matching_skills": sorted(matching_skills),
            "missing_skills": sorted(missing_skills),
            "jd_skills_count": len(jd_skills_list),
            "matching_skills_count": len(matching_skills),
            "missing_skills_count": len(missing_skills),
            "missing_keywords": missing_keywords[:8],
            "recommendations": recs
        }

    def _extract_jd_skills(self) -> tuple[Dict[str, List[str]], List[str]]:
        """Identify required skills from JD text using taxonomy."""
        found_skills = set()
        by_category = {}
        jd_lower = f" {self.jd_text.lower()} "

        for category, skill_list in SKILLS_TAXONOMY.items():
            cat_skills = []
            for skill in skill_list:
                escaped = re.escape(skill)
                pattern = rf'(?<![a-zA-Z0-9_#+.-]){escaped}(?![a-zA-Z0-9_#+.-])'
                if re.search(pattern, jd_lower):
                    display_name = skill.capitalize() if len(skill) > 3 else skill.upper()
                    if skill in ["javascript", "typescript"]:
                        display_name = skill[:4].capitalize() + skill[4:].capitalize()
                    elif skill in ["react", "next.js", "vue", "angular", "fastapi", "django", "postgresql", "docker", "kubernetes", "mongodb"]:
                        display_name = skill.title()
                    cat_skills.append(display_name)
                    found_skills.add(display_name)

            if cat_skills:
                by_category[category] = sorted(list(set(cat_skills)))

        return by_category, list(found_skills)

    def _calculate_cosine_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate word-level cosine similarity between two texts."""
        stop_words = {
            "the", "and", "is", "in", "to", "of", "with", "for", "a", "an", "on", "at",
            "by", "this", "that", "from", "as", "be", "are", "or", "your", "our", "you",
            "we", "will", "can", "have", "has", "it", "all", "work", "job", "experience"
        }

        words_a = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', text_a.lower()) if w not in stop_words]
        words_b = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', text_b.lower()) if w not in stop_words]

        if not words_a or not words_b:
            return 0.0

        vec_a = Counter(words_a)
        vec_b = Counter(words_b)

        intersection = set(vec_a.keys()) & set(vec_b.keys())
        numerator = sum([vec_a[x] * vec_b[x] for x in intersection])

        sum1 = sum([vec_a[x] ** 2 for x in vec_a.keys()])
        sum2 = sum([vec_b[x] ** 2 for x in vec_b.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        return float(numerator) / denominator

    def _extract_missing_important_keywords(self) -> List[str]:
        """Find frequent substantive words in the JD not present in resume."""
        stop_words = {
            "the", "and", "for", "with", "you", "will", "our", "are", "that", "this", "from",
            "have", "experience", "role", "team", "work", "years", "candidate", "responsibilities",
            "requirements", "qualification", "must", "plus", "ability", "strong", "knowledge",
            "skills", "company", "looking", "position", "preferred", "including", "across", "about"
        }

        resume_tokens = set(re.findall(r'\b[a-zA-Z]{3,}\b', self.resume_text.lower()))
        jd_tokens = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', self.jd_text.lower()) if w not in stop_words]

        jd_freq = Counter(jd_tokens)
        missing = []
        for word, count in jd_freq.most_common(25):
            if word not in resume_tokens and len(word) > 3:
                missing.append(word.title())

        return missing

    @staticmethod
    def _get_match_grade(score: float) -> str:
        """Categorize match score into human-readable grade."""
        if score >= 80:
            return "High Compatibility (Strong Match)"
        elif score >= 65:
            return "Good Alignment (Competitive)"
        elif score >= 50:
            return "Moderate Match (Gaps to Address)"
        else:
            return "Low Match (Needs Tailoring)"

    def _generate_tailoring_tips(
        self,
        match_score: float,
        missing_skills: List[str],
        missing_keywords: List[str]
    ) -> List[Dict[str, str]]:
        """Generate targeted tips to boost alignment with this specific JD."""
        tips = []

        if missing_skills:
            top_missing = ", ".join(missing_skills[:5])
            tips.append({
                "type": "skills",
                "title": f"Incorporate Key Missing Skills ({top_missing})",
                "detail": f"The job description specifically mentions {top_missing}. If you have practical experience with these, make sure they appear explicitly under your 'Skills' or 'Work Experience' bullets."
            })

        if missing_keywords:
            top_kw = ", ".join(missing_keywords[:4])
            tips.append({
                "type": "keywords",
                "title": f"Align with JD Terminology ({top_kw})",
                "detail": f"ATS filters scan for specific keywords used in the job post. Consider weaving these concepts into your summary or project descriptions if applicable."
            })

        if match_score < 70:
            tips.append({
                "type": "tailoring",
                "title": "Tailor Your Summary / Objective",
                "detail": "Customize the first 3 lines of your resume to mirror the job title and top 2 key requirements mentioned in the posting."
            })

        return tips
