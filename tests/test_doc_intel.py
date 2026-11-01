"""
Tests for SevaAgent Document Intelligence Agent
"""

import unittest
from pathlib import Path
from seva_agent.agents.doc_intel import DocumentIntelligenceAgent
from seva_agent.core.models import DocumentType
from seva_agent.core.config import DOCS_DIR
from sample_data.sample_profile import create_sample_profile


class TestDocIntel(unittest.TestCase):
    def setUp(self):
        self.doc_intel = DocumentIntelligenceAgent()
        self.profile = create_sample_profile()

    def test_aadhaar_extraction(self):
        aadhaar_file = DOCS_DIR / "aadhaar_card.txt"
        extracted = self.doc_intel.process_document(str(aadhaar_file), expected_type=DocumentType.AADHAAR)
        self.assertEqual(extracted.doc_type, DocumentType.AADHAAR)
        self.assertEqual(extracted.extracted_fields.get("aadhaar_number"), "541288913920")
        self.assertGreaterEqual(extracted.confidence_score, 0.85)

    def test_income_certificate_extraction(self):
        income_file = DOCS_DIR / "income_certificate.txt"
        extracted = self.doc_intel.process_document(str(income_file), expected_type=DocumentType.INCOME_CERTIFICATE)
        self.assertEqual(extracted.extracted_fields.get("annual_income"), 180000.0)
        self.assertEqual(extracted.extracted_fields.get("certificate_number"), "RD0038291024")

    def test_cross_validation_detection(self):
        # Alter profile to cause mismatch
        tampered_profile = self.profile.model_copy()
        tampered_profile.annual_family_income = 50000.0  # Claims 50k, but cert says 180k
        flags = self.doc_intel.cross_validate_profile(tampered_profile)
        self.assertTrue(len(flags) > 0)
        self.assertIn("Income Discrepancy", flags[0])

    def test_analyze_discrepancies(self):
        # Clean profile should have zero discrepancies
        discrepancies = self.doc_intel.analyze_discrepancies(self.profile)
        self.assertEqual(len(discrepancies), 0)

        # Alter profile name to test discrepancy
        mismatch_profile = self.profile.model_copy()
        mismatch_profile.full_name = "Priya R Sharma"  # aadhaar says Priya Ramesh Sharma
        discrepancies_found = self.doc_intel.analyze_discrepancies(mismatch_profile)
        self.assertTrue(len(discrepancies_found) > 0)
        self.assertTrue(any(d.field_name == "full_name" for d in discrepancies_found))

    def test_readiness_score_calculation(self):
        from seva_agent.agents.discovery import ScholarshipDiscoveryAgent
        scheme = ScholarshipDiscoveryAgent().scheme_catalog[0]
        readiness = self.doc_intel.calculate_readiness_score(self.profile, scheme)
        self.assertGreaterEqual(readiness.overall_percentage, 85.0)
        self.assertTrue(readiness.is_ready_to_apply)
        self.assertEqual(len(readiness.missing_critical_documents), 0)


if __name__ == "__main__":
    unittest.main()
