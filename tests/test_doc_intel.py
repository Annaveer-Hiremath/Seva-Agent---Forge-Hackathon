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


if __name__ == "__main__":
    unittest.main()
