"""Core Resume Analysis and ATS Engine.

Performs contact extraction, section segmentation, skill extraction,
quantifiable metrics analysis, action verb assessment, and overall ATS scoring.
"""

import re
from typing import Dict, List, Any, Optional
from app.taxonomy import (
    SKILLS_TAXONOMY,
    POWER_ACTION_VERBS,
    WEAK_WORDS,
    CLICHE_BUZZWORDS,
    STANDARD_SECTIONS
)


class ResumeAnalyzer:
    """Analyzes resume text for ATS compatibility, impact, and completeness."""

    def __init__(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        self.raw_text = text or ""
        self.clean_text = self._clean_text(self.raw_text)
        self.lines = [line.strip() for line in self.raw_text.splitlines() if line.strip()]
        self.metadata = metadata or {}
        self.words = re.findall(r'\b[a-zA-Z0-9+#.-]+\b', self.clean_text.lower())
        self.word_count = len(self.words)

    @staticmethod
    def _clean_text(text: str) -> str:
        """Normalize whitespace and control characters."""
        text = re.sub(r'[\r\t]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive resume analysis."""
        if not self.raw_text.strip():
            return self._empty_result()

        contact_info = self._extract_contact_info()
        sections_found, missing_sections = self._detect_sections()
        detected_skills, skills_by_category = self._extract_skills()
        impact_metrics = self._analyze_impact_metrics()
        action_verb_stats = self._analyze_action_verbs()
        cliche_matches = self._detect_cliches()
        readability = self._analyze_readability()
        bullet_suggestions = self._generate_bullet_suggestions()

        scoring = self._calculate_ats_score(
            contact_info=contact_info,
            sections_found=sections_found,
            skills_count=len(detected_skills),
            impact_stats=impact_metrics,
            verb_stats=action_verb_stats,
            cliche_count=len(cliche_matches),
            word_count=self.word_count,
            is_scanned=self.metadata.get("is_scanned", False)
        )

        recommendations = self._generate_recommendations(
            scoring=scoring,
            contact_info=contact_info,
            missing_sections=missing_sections,
            impact_stats=impact_metrics,
            verb_stats=action_verb_stats,
            cliche_matches=cliche_matches,
            skills_count=len(detected_skills)
        )

        return {
            "score": scoring["total_score"],
            "grade": scoring["grade"],
            "score_breakdown": scoring["breakdown"],
            "overview": {
                "word_count": self.word_count,
                "character_count": len(self.raw_text),
                "estimated_pages": self.metadata.get("page_count", max(1, round(self.word_count / 450))),
                "format": self.metadata.get("format", "TXT"),
                "is_scanned": self.metadata.get("is_scanned", False)
            },
            "contact_info": contact_info,
            "sections": {
                "detected": list(sections_found.keys()),
                "missing": missing_sections
            },
            "skills": {
                "total_count": len(detected_skills),
                "all_skills": sorted(detected_skills),
                "by_category": skills_by_category
            },
            "impact_analysis": impact_metrics,
            "action_verbs": action_verb_stats,
            "cliches_detected": cliche_matches,
            "readability": readability,
            "bullet_suggestions": bullet_suggestions,
            "recommendations": recommendations
        }

    def _extract_contact_info(self) -> Dict[str, Any]:
        """Extract candidate contact details and links."""
        # Email
        email_match = re.search(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', self.raw_text)
        email = email_match.group(0) if email_match else None

        # Phone
        phone_match = re.search(
            r'(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?',
            self.raw_text
        )
        phone = phone_match.group(0).strip() if phone_match else None
        if not phone:
            # Fallback international phone pattern
            alt_phone = re.search(r'\+?\d{1,4}[-.\s]?\(?\d{2,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}', self.raw_text)
            phone = alt_phone.group(0).strip() if alt_phone else None

        # LinkedIn
        linkedin_match = re.search(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|company)\/([a-zA-Z0-9_\-\/%]+)', self.raw_text, re.IGNORECASE)
        linkedin = linkedin_match.group(0) if linkedin_match else None

        # GitHub
        github_match = re.search(r'(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_\-]+)', self.raw_text, re.IGNORECASE)
        github = github_match.group(0) if github_match else None

        # Portfolio / Personal Website
        portfolio_match = re.search(r'(?:https?:\/\/)(?!linkedin|github)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?', self.raw_text, re.IGNORECASE)
        portfolio = portfolio_match.group(0) if portfolio_match else None

        # Candidate Name heuristic (first clean line near the top)
        candidate_name = None
        for line in self.lines[:6]:
            clean_line = re.sub(r'[^a-zA-Z\s]', '', line).strip()
            # Must look like a name (2 to 4 words, reasonable length, not containing generic resume keywords)
            words = clean_line.split()
            lower = line.lower()
            if 2 <= len(words) <= 4 and 4 <= len(clean_line) <= 40:
                if not any(k in lower for k in ["resume", "curriculum", "vitae", "summary", "profile", "contact", "developer", "engineer", "designer", "page"]):
                    candidate_name = clean_line.title()
                    break

        return {
            "name": candidate_name or "Not explicitly identified",
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "portfolio": portfolio,
            "has_email": email is not None,
            "has_phone": phone is not None,
            "has_linkedin": linkedin is not None,
            "has_github": github is not None
        }

    def _detect_sections(self) -> tuple[Dict[str, str], List[str]]:
        """Detect standard sections in the resume."""
        detected = {}
        text_lower = self.raw_text.lower()

        for section_name, synonyms in STANDARD_SECTIONS.items():
            for synonym in synonyms:
                pattern = rf'(?:^|\n)\s*{re.escape(synonym)}\s*(?::|\n|\r|$)'
                if re.search(pattern, text_lower, re.MULTILINE):
                    detected[section_name] = synonym
                    break

        core_sections = ["experience", "education", "skills"]
        missing = [sec for sec in core_sections if sec not in detected]
        # Also check optional but valuable sections
        optional_valuable = ["summary", "projects"]
        for sec in optional_valuable:
            if sec not in detected and sec not in missing:
                missing.append(sec)

        return detected, missing

    def _extract_skills(self) -> tuple[List[str], Dict[str, List[str]]]:
        """Extract and categorize skills using regex word boundaries."""
        all_detected = set()
        by_category = {}
        text_lower = f" {self.clean_text.lower()} "

        for category, skill_list in SKILLS_TAXONOMY.items():
            category_matches = []
            for skill in skill_list:
                # Skill matching with boundaries
                # Handle special chars like c++, c#, .net, node.js
                escaped = re.escape(skill)
                # If skill starts/ends with alphanumeric, use \b boundary
                pattern = rf'(?<![a-zA-Z0-9_#+.-]){escaped}(?![a-zA-Z0-9_#+.-])'
                if re.search(pattern, text_lower):
                    display_name = skill.capitalize() if len(skill) > 3 else skill.upper()
                    if skill in ["javascript", "typescript"]:
                        display_name = skill[:4].capitalize() + skill[4:].capitalize()
                    elif skill in ["react", "next.js", "vue", "angular", "fastapi", "django", "postgresql", "docker", "kubernetes", "mongodb"]:
                        display_name = skill.title()
                    category_matches.append(display_name)
                    all_detected.add(display_name)

            if category_matches:
                by_category[category] = sorted(list(set(category_matches)))

        return list(all_detected), by_category

    def _analyze_impact_metrics(self) -> Dict[str, Any]:
        """Identify quantifiable metrics, numbers, percentages, and dollar values."""
        bullets = self._extract_bullet_points()
        bullets_with_metrics = []

        metric_patterns = [
            r'\b\d+[\d,.]*\s*(?:%|percent)',
            r'\$\s*\d+[\d,.]*(?:\s*(?:k|m|b|million|billion))?',
            r'\b\d+[\d,.]*\s*(?:x)\b',
            r'\b\d+[\d,.]*(?:k|m|b|\+)\b',
            r'\b(?:reduced|increased|improved|boosted|cut|saved|generated|scaled|grown)\s+(?:by\s+)?\d+[\d,.]*',
            r'\b\d+[\d,.]*\s*(?:users|clients|customers|requests|transactions|engineers|team members|developers|services|endpoints|uptime|stars|seconds|minutes|hours)\b'
        ]
        combined_metric_regex = re.compile(r'(?:' + '|'.join(metric_patterns) + r')', re.IGNORECASE)

        for bullet in bullets:
            matches = [m.group(0).strip() for m in combined_metric_regex.finditer(bullet)]
            if matches:
                bullets_with_metrics.append({
                    "text": bullet[:180] + ("..." if len(bullet) > 180 else ""),
                    "metrics_found": matches[:3]
                })

        total_bullets = len(bullets)
        metric_bullet_count = len(bullets_with_metrics)
        metric_ratio = round((metric_bullet_count / total_bullets * 100), 1) if total_bullets > 0 else 0

        return {
            "total_bullets": total_bullets,
            "bullets_with_metrics_count": metric_bullet_count,
            "metric_bullet_percentage": metric_ratio,
            "samples": bullets_with_metrics[:5]
        }

    def _analyze_action_verbs(self) -> Dict[str, Any]:
        """Assess the use of strong power action verbs vs weak/passive verbs."""
        text_lower = self.clean_text.lower()
        bullets = self._extract_bullet_points()

        power_found = set()
        for verb in POWER_ACTION_VERBS:
            if re.search(rf'\b{re.escape(verb)}\b', text_lower):
                power_found.add(verb.capitalize())

        weak_found = []
        for weak in WEAK_WORDS:
            matches = list(re.finditer(rf'\b{re.escape(weak)}\b', text_lower))
            if matches:
                weak_found.append({
                    "phrase": weak,
                    "count": len(matches)
                })

        # Calculate bullets starting with power verbs
        bullets_starting_with_power = 0
        for b in bullets:
            first_word = re.sub(r'[^a-zA-Z]', '', b.split()[0]).lower() if b.split() else ""
            if first_word in POWER_ACTION_VERBS:
                bullets_starting_with_power += 1

        power_ratio = round((bullets_starting_with_power / len(bullets) * 100), 1) if bullets else 0

        return {
            "power_verbs_count": len(power_found),
            "power_verbs_list": sorted(list(power_found))[:20],
            "weak_phrases_detected": weak_found,
            "bullets_starting_with_power_count": bullets_starting_with_power,
            "bullets_starting_with_power_ratio": power_ratio
        }

    def _detect_cliches(self) -> List[str]:
        """Detect overused buzzwords and clichés."""
        text_lower = self.clean_text.lower()
        found = []
        for cliche in CLICHE_BUZZWORDS:
            if re.search(rf'\b{re.escape(cliche)}\b', text_lower):
                found.append(cliche.title())
        return found

    def _analyze_readability(self) -> Dict[str, Any]:
        """Estimate text readability and sentence structure."""
        sentences = [s.strip() for s in re.split(r'[.!?]+', self.raw_text) if len(s.strip()) > 3]
        sentence_count = max(1, len(sentences))
        avg_sentence_len = round(self.word_count / sentence_count, 1)

        # Flesch-Kincaid ease estimate
        syllables = sum(self._count_syllables(w) for w in self.words)
        asl = self.word_count / sentence_count
        asw = (syllables / max(1, self.word_count))
        flesch_score = round(206.835 - (1.015 * asl) - (84.6 * asw), 1)
        flesch_score = max(0.0, min(100.0, flesch_score))

        if flesch_score >= 60:
            level = "Easy to read & clear"
        elif flesch_score >= 40:
            level = "Standard professional"
        else:
            level = "Dense / Complex phrasing"

        return {
            "sentence_count": sentence_count,
            "avg_sentence_length_words": avg_sentence_len,
            "flesch_reading_ease": flesch_score,
            "reading_level": level
        }

    def _extract_bullet_points(self) -> List[str]:
        """Extract individual bullet points or experience action lines."""
        bullets = []
        skip_headers = [
            "programming languages:", "web & frameworks:", "cloud & devops:",
            "databases:", "tools & practices:", "technical skills:", "technologies:",
            "education", "certifications", "professional summary"
        ]
        for line in self.lines:
            cleaned = re.sub(r'^[\s•\-\*▪►\d+.)]+\s*', '', line).strip()
            lower_clean = cleaned.lower()
            if any(lower_clean.startswith(sh) for sh in skip_headers):
                continue

            # If line has bullet indicator or looks like an action description
            if (line.startswith(('•', '-', '*', '▪', '►')) or re.match(r'^\d+\.', line)) and len(cleaned) > 15:
                bullets.append(cleaned)
            elif 25 <= len(cleaned) <= 280 and any(lower_clean.startswith(v) for v in POWER_ACTION_VERBS):
                bullets.append(cleaned)
        return bullets

    def _generate_bullet_suggestions(self) -> List[Dict[str, str]]:
        """Find bullets that can be enhanced with the STAR / XYZ formula."""
        suggestions = []
        bullets = self._extract_bullet_points()

        for b in bullets:
            lower_b = b.lower()
            # If it uses weak phrases or has zero numbers
            has_weak = any(w in lower_b for w in ["responsible for", "helped", "worked on", "handled"])
            has_numbers = bool(re.search(r'\d+', b))

            if has_weak or (not has_numbers and len(b) > 40):
                # Suggest improved version
                verb = "Engineered" if "code" in lower_b or "software" in lower_b else "Spearheaded"
                suggestions.append({
                    "original": b,
                    "critique": "Lacks measurable impact or uses passive language.",
                    "suggestion": f"{verb} [project/feature], resulting in [X% improvement / Y hours saved] by implementing [specific technology/methodology]."
                })
                if len(suggestions) >= 3:
                    break

        return suggestions

    def _calculate_ats_score(
        self,
        contact_info: Dict[str, Any],
        sections_found: Dict[str, str],
        skills_count: int,
        impact_stats: Dict[str, Any],
        verb_stats: Dict[str, Any],
        cliche_count: int,
        word_count: int,
        is_scanned: bool
    ) -> Dict[str, Any]:
        """Compute holistic ATS readiness score (0-100)."""
        if is_scanned:
            return {
                "total_score": 10,
                "grade": "Needs Improvement",
                "breakdown": {
                    "contact": 0, "sections": 0, "skills": 0,
                    "impact": 0, "action_verbs": 0, "formatting": 10
                }
            }

        # 1. Contact Info (Max 15)
        contact_score = 0
        if contact_info.get("has_email"):
            contact_score += 5
        if contact_info.get("has_phone"):
            contact_score += 4
        if contact_info.get("has_linkedin") or contact_info.get("has_github"):
            contact_score += 4
        if contact_info.get("name") and contact_info["name"] != "Not explicitly identified":
            contact_score += 2

        # 2. Section Headers (Max 20)
        section_score = 0
        if "experience" in sections_found:
            section_score += 7
        if "education" in sections_found:
            section_score += 5
        if "skills" in sections_found:
            section_score += 5
        if "summary" in sections_found or "projects" in sections_found:
            section_score += 3

        # 3. Skills Diversity (Max 15)
        skill_score = min(15, round((skills_count / 12) * 15))

        # 4. Quantifiable Impact & Metrics (Max 20)
        # Based on bullet metric ratio (e.g., 40%+ bullets having numbers is top tier)
        metric_ratio = impact_stats.get("metric_bullet_percentage", 0)
        impact_score = min(20, round((metric_ratio / 40.0) * 20))

        # 5. Action Verbs & Language Strength (Max 15)
        power_count = verb_stats.get("power_verbs_count", 0)
        weak_count = len(verb_stats.get("weak_phrases_detected", []))
        verb_score = min(15, max(0, round((power_count / 8) * 15) - (weak_count * 2)))

        # 6. Formatting, Length & ATS Cleanliness (Max 15)
        fmt_score = 15
        if word_count < 300:
            fmt_score -= 8
        elif word_count < 450:
            fmt_score -= 4
        elif word_count > 1800:
            fmt_score -= 5

        # Penalty for cliches
        fmt_score = max(3, fmt_score - (cliche_count * 2))

        total = contact_score + section_score + skill_score + impact_score + verb_score + fmt_score
        total = max(10, min(100, total))

        if total >= 85:
            grade = "Excellent (ATS Ready)"
        elif total >= 70:
            grade = "Competitive (Good)"
        elif total >= 55:
            grade = "Fair (Needs Polish)"
        else:
            grade = "Needs Improvement"

        return {
            "total_score": total,
            "grade": grade,
            "breakdown": {
                "contact": {"score": contact_score, "max": 15},
                "sections": {"score": section_score, "max": 20},
                "skills": {"score": skill_score, "max": 15},
                "impact": {"score": impact_score, "max": 20},
                "action_verbs": {"score": verb_score, "max": 15},
                "formatting": {"score": fmt_score, "max": 15}
            }
        }

    def _generate_recommendations(
        self,
        scoring: Dict[str, Any],
        contact_info: Dict[str, Any],
        missing_sections: List[str],
        impact_stats: Dict[str, Any],
        verb_stats: Dict[str, Any],
        cliche_matches: List[str],
        skills_count: int
    ) -> List[Dict[str, Any]]:
        """Generate categorized, actionable improvement steps."""
        recs = []

        # Scanned PDF warning
        if self.metadata.get("is_scanned"):
            recs.append({
                "severity": "critical",
                "category": "File Format",
                "title": "Unreadable / Scanned Image Detected",
                "message": "The PDF contains very little machine-readable text. Most ATS scanners will fail to parse this resume. Export directly from Microsoft Word, Google Docs, or LaTeX to PDF with selectable text.",
                "fix": "Re-export resume as text-based PDF."
            })
            return recs

        # Contact Info
        if not contact_info.get("has_email"):
            recs.append({
                "severity": "critical",
                "category": "Contact Information",
                "title": "Missing Email Address",
                "message": "ATS parsers look for an email to create your applicant profile. Ensure your professional email is clearly listed at the top.",
                "fix": "Add a professional email (e.g., name@gmail.com) in the header."
            })

        if not contact_info.get("has_phone"):
            recs.append({
                "severity": "warning",
                "category": "Contact Information",
                "title": "Missing Phone Number",
                "message": "Recruiters and automated schedulers often send interview links or screen by phone.",
                "fix": "Add a standard telephone number with country code."
            })

        if not contact_info.get("has_linkedin") and not contact_info.get("has_github"):
            recs.append({
                "severity": "warning",
                "category": "Online Presence",
                "title": "No LinkedIn or GitHub Profile Found",
                "message": "Over 87% of technical recruiters review LinkedIn or GitHub profiles. Adding clean hyperlinks significantly boosts credibility.",
                "fix": "Include your customized LinkedIn URL or GitHub username."
            })

        # Missing Sections
        if missing_sections:
            for sec in missing_sections:
                recs.append({
                    "severity": "critical" if sec in ["experience", "education", "skills"] else "warning",
                    "category": "ATS Structure",
                    "title": f"Missing Standard Section: {sec.title()}",
                    "message": f"ATS algorithms search for standard headers like '{sec.title()}'. Without it, your achievements might be skipped or miscategorized.",
                    "fix": f"Add a dedicated '{sec.title()}' header in your resume."
                })

        # Quantifiable Impact
        metric_pct = impact_stats.get("metric_bullet_percentage", 0)
        if metric_pct < 25:
            recs.append({
                "severity": "high",
                "category": "Impact & Metrics",
                "title": f"Low Quantifiable Results ({metric_pct}% of bullets)",
                "message": "Top-tier resumes quantify impact with numbers, percentages, dollar amounts, or team sizes (e.g., 'Reduced API latency by 45%', 'Handled 2M+ daily requests').",
                "fix": "Use the Google XYZ formula: 'Accomplished [X] as measured by [Y] by doing [Z]'."
            })

        # Action Verbs & Weak phrases
        weak_list = verb_stats.get("weak_phrases_detected", [])
        if weak_list:
            phrases_str = ", ".join([f'"{w["phrase"]}"' for w in weak_list[:3]])
            recs.append({
                "severity": "medium",
                "category": "Language & Tone",
                "title": f"Passive or Weak Language Detected ({phrases_str})",
                "message": "Phrases like 'responsible for' or 'helped with' describe passive duties rather than your proactive accomplishments.",
                "fix": "Replace with power action verbs like 'Architected', 'Spearheaded', 'Optimized', or 'Automated'."
            })

        # Cliches
        if cliche_matches:
            recs.append({
                "severity": "low",
                "category": "Word Choice",
                "title": f"Cliches & Buzzwords Found ({', '.join(cliche_matches[:3])})",
                "message": "Recruiters discount generic adjectives like 'hard worker' or 'team player'. Demonstrate these traits through your concrete achievements instead.",
                "fix": "Remove generic buzzwords and replace them with specific technical or project milestones."
            })

        # Word count check
        if self.word_count < 350:
            recs.append({
                "severity": "warning",
                "category": "Length & Density",
                "title": f"Resume Appears Too Brief ({self.word_count} words)",
                "message": "A standard 1-page technical resume typically has between 450 and 800 words with thorough detail on recent achievements.",
                "fix": "Elaborate on specific architectural decisions, technologies used, and business outcomes."
            })
        elif self.word_count > 1600:
            recs.append({
                "severity": "medium",
                "category": "Length & Density",
                "title": f"Resume May Be Too Verbose ({self.word_count} words)",
                "message": "Long resumes risk diluting your most impactful accomplishments. Aim for a tight 1-page (0-5 years) or 2-page (5+ years) format.",
                "fix": "Trim older roles or non-essential descriptions into concise bullet points."
            })

        # Skills count
        if skills_count < 6:
            recs.append({
                "severity": "high",
                "category": "Keywords & Skills",
                "title": f"Low Technical Keyword Density ({skills_count} skills detected)",
                "message": "ATS engines use keyword matching to rank candidates for technical roles. Your resume has very few recognized technical keywords.",
                "fix": "Add a categorized Technical Skills section listing your languages, frameworks, cloud tools, and databases."
            })

        # Positive highlights if score is high
        if scoring["total_score"] >= 80:
            recs.append({
                "severity": "positive",
                "category": "ATS Strength",
                "title": "Strong Overall Structure & Vocabulary",
                "message": "Great job! Your resume demonstrates clear section segmentation, diverse technical keywords, and strong action-oriented descriptions.",
                "fix": "Keep your numbers updated as your projects grow."
            })

        return recs

    @staticmethod
    def _count_syllables(word: str) -> int:
        """Estimate syllable count in a word."""
        word = word.lower()
        if len(word) <= 3:
            return 1
        word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
        word = re.sub(r'^y', '', word)
        matches = re.findall(r'[aeiouy]{1,2}', word)
        return max(1, len(matches))

    def _empty_result(self) -> Dict[str, Any]:
        """Return blank structured response for empty inputs."""
        return {
            "score": 0,
            "grade": "No Content",
            "score_breakdown": {},
            "overview": {"word_count": 0, "character_count": 0, "estimated_pages": 0, "format": "N/A", "is_scanned": False},
            "contact_info": {},
            "sections": {"detected": [], "missing": []},
            "skills": {"total_count": 0, "all_skills": [], "by_category": {}},
            "impact_analysis": {"total_bullets": 0, "bullets_with_metrics_count": 0, "metric_bullet_percentage": 0, "samples": []},
            "action_verbs": {"power_verbs_count": 0, "power_verbs_list": [], "weak_phrases_detected": []},
            "cliches_detected": [],
            "readability": {"sentence_count": 0, "avg_sentence_length_words": 0, "flesch_reading_ease": 0, "reading_level": "N/A"},
            "bullet_suggestions": [],
            "recommendations": []
        }
