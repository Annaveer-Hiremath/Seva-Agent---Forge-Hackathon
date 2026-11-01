"""
Tests for SevaAgent Validator & Error Recovery Agent
"""

import unittest
from seva_agent.agents.validator import ValidatorAgent
from sample_data.sample_profile import create_sample_profile
from seva_agent.agents.discovery import ScholarshipDiscoveryAgent


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.validator = ValidatorAgent()
        self.profile = create_sample_profile()
        self.scheme = ScholarshipDiscoveryAgent().scheme_catalog[0]

    def test_valid_profile(self):
        valid, errors = self.validator.validate_citizen_profile(self.profile, self.scheme)
        self.assertTrue(valid, f"Validation failed with: {errors}")
        self.assertEqual(len(errors), 0)

    def test_invalid_aadhaar(self):
        bad_profile = self.profile.model_copy()
        bad_profile.aadhaar_number = "12345"  # Short Aadhaar
        valid, errors = self.validator.validate_citizen_profile(bad_profile, self.scheme)
        self.assertFalse(valid)
        self.assertTrue(any("Aadhaar" in e for e in errors))

    def test_invalid_ifsc(self):
        bad_profile = self.profile.model_copy()
        bad_profile.bank_ifsc_code = "INVALID_IFSC_123"
        valid, errors = self.validator.validate_citizen_profile(bad_profile, self.scheme)
        self.assertFalse(valid)
        self.assertTrue(any("IFSC" in e for e in errors))

    def test_dom_error_analysis(self):
        html_error = "<div class='error'>Aadhaar number is already registered with another applicant.</div>"
        errors = self.validator.analyze_portal_dom_errors(html_error)
        self.assertTrue(len(errors) > 0)
        self.assertIn("already registered", errors[0].lower())


if __name__ == "__main__":
    unittest.main()
