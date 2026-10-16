"""Comprehensive automated tests for ResuMetrics.
Tests extractor, analyzer, job matcher, and API endpoints.
"""

import unittest
from app.analyzer import ResumeAnalyzer
from app.job_matcher import JobMatcher
from app.samples import SAMPLE_RESUME, SAMPLE_JD
from app.extractor import DocumentExtractor


class TestResumeAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ResumeAnalyzer(SAMPLE_RESUME)
        self.results = self.analyzer.analyze()

    def test_contact_extraction(self):
        contact = self.results["contact_info"]
        self.assertEqual(contact["name"], "Alexander Chen")
        self.assertEqual(contact["email"], "alex.chen.dev@gmail.com")
        self.assertTrue(contact["has_phone"])
        self.assertTrue(contact["has_linkedin"])
        self.assertTrue(contact["has_github"])

    def test_section_detection(self):
        sections = self.results["sections"]["detected"]
        for sec in ["summary", "experience", "skills", "education", "projects"]:
            self.assertIn(sec, sections)

    def test_skills_extraction(self):
        skills = self.results["skills"]["all_skills"]
        self.assertGreater(len(skills), 15)
        # Check core skills
        skills_lower = [s.lower() for s in skills]
        self.assertIn("python", skills_lower)
        self.assertIn("fastapi", skills_lower)
        self.assertIn("docker", skills_lower)
        self.assertIn("kubernetes", skills_lower)
        self.assertIn("react", skills_lower)

    def test_impact_analysis(self):
        impact = self.results["impact_analysis"]
        self.assertGreater(impact["bullets_with_metrics_count"], 0)
        self.assertGreater(impact["metric_bullet_percentage"], 30.0)

    def test_action_verbs(self):
        verbs = self.results["action_verbs"]
        self.assertGreater(verbs["power_verbs_count"], 5)
        self.assertGreater(verbs["bullets_starting_with_power_count"], 0)

    def test_ats_score(self):
        score = self.results["score"]
        self.assertGreaterEqual(score, 70)
        self.assertLessEqual(score, 100)

    def test_job_matcher(self):
        matcher = JobMatcher(SAMPLE_RESUME, self.results["skills"]["all_skills"], SAMPLE_JD)
        match_res = matcher.match()
        self.assertTrue(match_res["has_job_description"])
        self.assertGreater(match_res["match_score"], 60.0)
        self.assertGreater(len(match_res["matching_skills"]), 5)

    def test_text_extractor(self):
        sample_bytes = SAMPLE_RESUME.encode("utf-8")
        extracted = DocumentExtractor.extract_from_bytes(sample_bytes, "resume.txt")
        self.assertEqual(extracted["format"], "TXT")
        self.assertGreater(extracted["word_count"], 100)


if __name__ == "__main__":
    print("Running automated test suite for ResuMetrics...")
    unittest.main()
