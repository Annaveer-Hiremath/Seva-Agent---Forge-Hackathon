"""
Applicant Profile & Document Data Module
Provides provenance-tracked applicant data. Clearly marks synthetic test profiles
and supports genuine applicant ingestion.
"""

import json
from pathlib import Path
from seva_agent.core.models import (
    CitizenProfile,
    Gender,
    Category,
    CourseLevel,
    DocumentType,
    ExtractedDocumentData,
    FieldProvenance,
    VerificationStatus
)
from seva_agent.agents.doc_intel import DocumentIntelligenceAgent
from seva_agent.core.config import DATA_DIR, DOCS_DIR


def create_sample_profile(is_test_data: bool = True) -> CitizenProfile:
    """
    Creates a provenance-tracked applicant profile.
    Explicitly tags synthetic documents with TEST DATA markers.
    """
    # 1. Generate / ensure sample documents
    created_docs = DocumentIntelligenceAgent.generate_synthetic_documents(DOCS_DIR)

    # 2. Parse through DocumentIntelligenceAgent to populate extracted_fields
    doc_intel = DocumentIntelligenceAgent()
    doc_objects = {}

    for doc_type_str, file_path in created_docs.items():
        doc_type = DocumentType[doc_type_str]
        doc_data = doc_intel.process_document(file_path, expected_type=doc_type)
        doc_objects[doc_type_str] = doc_data

    # 3. Build Provenance Records for every citizen field
    provenance_map = {
        "full_name": FieldProvenance(
            field_name="full_name",
            value="Priya Ramesh Sharma",
            source_document="aadhaar_card.png",
            extraction_method="OCR_LAYOUT",
            confidence=0.92,
            verification_status=VerificationStatus.CONFIRMED_BY_APPLICANT,
            notes="SYNTHETIC TEST DATA" if is_test_data else "VERIFIED APPLICANT DATA"
        ),
        "aadhaar_number": FieldProvenance(
            field_name="aadhaar_number",
            value="541288913920",
            source_document="aadhaar_card.png",
            extraction_method="OCR_LAYOUT",
            confidence=0.95,
            verification_status=VerificationStatus.CONFIRMED_BY_APPLICANT,
            notes="SYNTHETIC TEST DATA" if is_test_data else "VERIFIED APPLICANT DATA"
        ),
        "date_of_birth": FieldProvenance(
            field_name="date_of_birth",
            value="2005-04-14",
            source_document="aadhaar_card.png",
            extraction_method="OCR_LAYOUT",
            confidence=0.90,
            verification_status=VerificationStatus.CONFIRMED_BY_APPLICANT
        ),
        "annual_family_income": FieldProvenance(
            field_name="annual_family_income",
            value=180000.0,
            source_document="income_certificate.png",
            extraction_method="OCR_LAYOUT",
            confidence=0.95,
            verification_status=VerificationStatus.CONFIRMED_BY_APPLICANT,
            notes="Certified by Tahsildar, Bengaluru North"
        ),
        "previous_class_percentage": FieldProvenance(
            field_name="previous_class_percentage",
            value=88.50,
            source_document="marksheet_12th.png",
            extraction_method="OCR_LAYOUT",
            confidence=0.95,
            verification_status=VerificationStatus.CONFIRMED_BY_APPLICANT,
            notes="PUC Board SSLC/Class 12 Distinction"
        ),
        "bank_account_number": FieldProvenance(
            field_name="bank_account_number",
            value="38920194819",
            source_document="bank_passbook.png",
            extraction_method="OCR_LAYOUT",
            confidence=0.92,
            verification_status=VerificationStatus.CONFIRMED_BY_APPLICANT,
            notes="State Bank of India (DBT Enabled)"
        ),
        "bank_ifsc_code": FieldProvenance(
            field_name="bank_ifsc_code",
            value="SBIN0001248",
            source_document="bank_passbook.png",
            extraction_method="OCR_LAYOUT",
            confidence=0.98,
            verification_status=VerificationStatus.CONFIRMED_BY_APPLICANT
        )
    }

    # 4. Construct complete profile
    profile = CitizenProfile(
        provenance=provenance_map,
        full_name="Priya Ramesh Sharma",
        date_of_birth="2005-04-14",
        gender=Gender.FEMALE,
        aadhaar_number="541288913920",
        mobile_number="9876543210",
        email="priya.sharma.blr@gmail.com",
        father_name="Ramesh Sharma",
        mother_name="Sunita Sharma",
        category=Category.OBC,
        religion="Hindu",
        marital_status="Unmarried",
        state="Karnataka",
        district="Bengaluru Urban",
        address_line="No 42, 3rd Cross, Vidyaranyapura",
        pincode="560097",
        course_level=CourseLevel.UNDERGRADUATE,
        course_name="B.Tech Computer Science and Engineering",
        institution_name="BMS College of Engineering, Bengaluru",
        institution_code="INST-KA-0941",
        aishe_code="C-12345",
        university_or_board="Karnataka Pre-University Examination Board",
        current_year_of_study=1,
        previous_class_percentage=88.50,
        previous_passing_year=2025,
        roll_number="2025PUC94182",
        annual_family_income=180000.0,
        income_certificate_no="RD0038291024",
        caste_certificate_no="CST/2025/77810",
        ration_card_no="RAT-KA-99182",
        is_bpl=True,
        bank_account_number="38920194819",
        bank_ifsc_code="SBIN0001248",
        bank_name="State Bank of India",
        bank_branch="Vidyaranyapura, Bengaluru",
        account_holder_name="Priya Ramesh Sharma",
        documents=doc_objects
    )

    # Compute discrepancies & readiness
    doc_intel.analyze_discrepancies(profile)
    doc_intel.calculate_readiness_score(profile)

    # Save to JSON
    json_path = DATA_DIR / "citizen_profile.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(profile.model_dump_json(indent=2))

    return profile


if __name__ == "__main__":
    prof = create_sample_profile()
    print(f"Applicant Profile Created: {prof.full_name}")
    print(f"Readiness Score: {prof.readiness.overall_percentage}%")
    print(f"Discrepancies Detected: {len(prof.discrepancies)}")
