"""
Tests for SevaAgent Scholarship Discovery & Statutory Eligibility Agent
"""

import unittest
from seva_agent.agents.discovery import ScholarshipDiscoveryAgent
from sample_data.sample_profile import create_sample_profile
from seva_agent.core.models import Category, CourseLevel


class TestDiscoveryAgent(unittest.TestCase):
    def setUp(self):
        self.discovery = ScholarshipDiscoveryAgent()
        self.profile = create_sample_profile()

    def test_catalog_loaded(self):
        self.assertGreater(len(self.discovery.scheme_catalog), 3)

    def test_eligible_evaluation(self):
        assessments = self.discovery.evaluate_profile(self.profile)
        self.assertTrue(len(assessments) > 0)

        # Priya has 88.5% and income 1.8 Lakhs and OBC -> eligible for Central Sector Scheme
        top_scheme = next((a for a in assessments if a.scheme.scheme_id == "NSP_CENTRAL_SECTOR"), None)
        self.assertIsNotNone(top_scheme)
        self.assertTrue(top_scheme.is_eligible)
        self.assertEqual(top_scheme.eligibility_score, 100.0)
        self.assertIn("DoHE Scheme Guidelines", top_scheme.scheme.official_guideline_citation)

    def test_income_ceiling_rejection(self):
        rich_profile = self.profile.model_copy()
        rich_profile.annual_family_income = 1200000.0  # 12 Lakhs (exceeds all caps)
        assessments = self.discovery.evaluate_profile(rich_profile)
        central_sector = next((a for a in assessments if a.scheme.scheme_id == "NSP_CENTRAL_SECTOR"), None)
        self.assertFalse(central_sector.is_eligible)
        self.assertLess(central_sector.eligibility_score, 100.0)


if __name__ == "__main__":
    unittest.main()
