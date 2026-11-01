"""
SevaAgent Core Data Models
Pydantic schemas for applicant provenance, scholarship schemes,
action decisions, audit blocks, and readiness metrics.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class Category(str, Enum):
    GENERAL = "GENERAL"
    OBC = "OBC"
    SC = "SC"
    ST = "ST"
    EWS = "EWS"
    MINORITY = "MINORITY"


class CourseLevel(str, Enum):
    PRE_MATRIC = "PRE_MATRIC"
    POST_MATRIC = "POST_MATRIC"
    UNDERGRADUATE = "UNDERGRADUATE"
    POSTGRADUATE = "POSTGRADUATE"
    DIPLOMA = "DIPLOMA"
    PROFESSIONAL = "PROFESSIONAL"


class DocumentType(str, Enum):
    AADHAAR = "AADHAAR"
    INCOME_CERTIFICATE = "INCOME_CERTIFICATE"
    CASTE_CERTIFICATE = "CASTE_CERTIFICATE"
    MARKSHEET_10TH = "MARKSHEET_10TH"
    MARKSHEET_12TH = "MARKSHEET_12TH"
    COLLEGE_BONAFIDE = "COLLEGE_BONAFIDE"
    BANK_PASSBOOK = "BANK_PASSBOOK"
    FEE_RECEIPT = "FEE_RECEIPT"


class VerificationStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED_BY_OCR = "VERIFIED_BY_OCR"
    CONFIRMED_BY_APPLICANT = "CONFIRMED_BY_APPLICANT"
    DISCREPANCY_FLAGGED = "DISCREPANCY_FLAGGED"


class FieldProvenance(BaseModel):
    """Tracks origin and trust score for every single citizen data point."""
    field_name: str
    value: Any
    source_document: Optional[str] = None  # e.g. "aadhaar_card.png" or "User Input"
    extraction_method: str = "OCR_LAYOUT"  # "OCR_LAYOUT", "MANUAL_INPUT", "DEFAULT"
    confidence: float = 1.0  # 0.0 to 1.0
    verification_status: VerificationStatus = VerificationStatus.CONFIRMED_BY_APPLICANT
    notes: Optional[str] = None


class ExtractedDocumentData(BaseModel):
    doc_type: DocumentType
    file_path: str
    confidence_score: float = Field(default=0.90, ge=0.0, le=1.0)
    extracted_fields: Dict[str, Any] = Field(default_factory=dict)
    raw_text: str = ""
    is_verified: bool = False
    validation_notes: List[str] = Field(default_factory=list)
    sha256_hash: Optional[str] = None


class DocumentDiscrepancy(BaseModel):
    field_name: str
    declared_value: Any
    extracted_value: Any
    source_document: str
    severity: str = "WARNING"  # "WARNING", "CRITICAL"
    explanation: str
    resolved_by_applicant: bool = False
    applicant_override_value: Optional[Any] = None


class ApplicationReadinessScore(BaseModel):
    overall_percentage: float = 0.0
    personal_details_complete: bool = False
    academic_details_complete: bool = False
    financial_details_complete: bool = False
    required_documents_uploaded: bool = False
    discrepancies_resolved: bool = True
    statutory_eligibility_passed: bool = False
    missing_critical_documents: List[str] = Field(default_factory=list)
    breakdown_notes: List[str] = Field(default_factory=list)

    @property
    def is_ready_to_apply(self) -> bool:
        return self.overall_percentage >= 70.0 and len(self.missing_critical_documents) == 0


class CitizenProfile(BaseModel):
    # Data Provenance Tracking per field
    provenance: Dict[str, FieldProvenance] = Field(default_factory=dict)

    # Personal Identification
    full_name: str
    date_of_birth: str  # YYYY-MM-DD
    gender: Gender
    aadhaar_number: str  # 12-digit Aadhaar
    mobile_number: str
    email: str
    father_name: str
    mother_name: str
    category: Category
    religion: str = "Hindu"
    marital_status: str = "Unmarried"
    is_disabled: bool = False
    disability_percentage: float = 0.0

    # Domicile & Location
    state: str  # e.g., "Karnataka"
    district: str
    address_line: str
    pincode: str

    # Academic Profile
    course_level: CourseLevel
    course_name: str
    institution_name: str
    institution_code: str = "INST-KA-0941"
    aishe_code: str = "C-12345"
    university_or_board: str
    current_year_of_study: int = 1
    previous_class_percentage: float
    previous_passing_year: int = 2025
    roll_number: str

    # Financial & Social Profile
    annual_family_income: float
    income_certificate_no: Optional[str] = None
    caste_certificate_no: Optional[str] = None
    ration_card_no: Optional[str] = None
    is_bpl: bool = True

    # Bank Account for DBT
    bank_account_number: str
    bank_ifsc_code: str
    bank_name: str
    bank_branch: str
    account_holder_name: str

    # Attached documents (path -> ExtractedDocumentData)
    documents: Dict[str, ExtractedDocumentData] = Field(default_factory=dict)
    discrepancies: List[DocumentDiscrepancy] = Field(default_factory=list)
    readiness: Optional[ApplicationReadinessScore] = None


class ScholarshipScheme(BaseModel):
    scheme_id: str
    scheme_name: str
    ministry_or_dept: str
    portal_type: str  # "NSP" or "STATE_SSP"
    portal_url: str
    description: str
    categories_allowed: List[Category]
    max_family_income: float
    min_previous_percentage: float
    allowed_course_levels: List[CourseLevel]
    target_gender: Optional[List[Gender]] = None
    state_domicile_required: Optional[str] = None
    award_amount_annual: float
    official_guideline_citation: str
    application_deadline: str
    required_document_types: List[DocumentType]


class RuleEvaluation(BaseModel):
    rule_name: str
    passed: bool
    citizen_value: Any
    scheme_requirement: Any
    citation: str
    explanation: str


class EligibilityAssessment(BaseModel):
    scheme: ScholarshipScheme
    is_eligible: bool
    eligibility_score: float  # 0 to 100
    rule_evaluations: List[RuleEvaluation]
    required_documents: List[DocumentType]
    missing_documents: List[DocumentType] = Field(default_factory=list)
    actionable_summary: str


class ActionType(str, Enum):
    NAVIGATE = "NAVIGATE"
    OBSERVE = "OBSERVE"
    FILL_FIELD = "FILL_FIELD"
    SELECT_OPTION = "SELECT_OPTION"
    CLICK_ELEMENT = "CLICK_ELEMENT"
    UPLOAD_FILE = "UPLOAD_FILE"
    DISMISS_MODAL = "DISMISS_MODAL"
    REQUEST_CAPTCHA_HITL = "REQUEST_CAPTCHA_HITL"
    REQUEST_OTP_HITL = "REQUEST_OTP_HITL"
    VERIFY_SUBMISSION = "VERIFY_SUBMISSION"
    REPLAN = "REPLAN"
    HALT_AT_SECURITY_BOUNDARY = "HALT_AT_SECURITY_BOUNDARY"


class LocatorStrategy(str, Enum):
    LABEL = "label"
    ROLE = "role"
    PLACEHOLDER = "placeholder"
    TEXT = "text"
    CSS = "css"
    XPATH = "xpath"


class AgentActionDecision(BaseModel):
    """Structured action output from AI reasoning engine."""
    action_type: ActionType
    target_description: str
    locator_strategy: LocatorStrategy
    locator_value: str
    attribute_name: Optional[str] = None
    field_id: Optional[str] = None
    input_value: Optional[str] = None
    masked_value: Optional[str] = None
    rationale: str
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    requires_human_approval: bool = False
    validation_status: str = "APPROVED"  # "APPROVED", "REJECTED"
    model_request_prompt: Optional[str] = None
    model_response_raw: Optional[str] = None


class AgentActionRecord(BaseModel):
    action_id: str
    timestamp_utc: str
    agent_name: str
    decision: AgentActionDecision
    execution_result: str
    page_url: str
    page_title: str
    screenshot_path: Optional[str] = None
    screenshot_hash: Optional[str] = None
    execution_time_ms: float = 0.0
    status: str = "SUCCESS"  # "SUCCESS", "FAILED", "RETRYING", "PAUSED_HITL"


class AuditBlock(BaseModel):
    block_index: int
    session_id: str
    timestamp_utc: str
    agent_name: str
    page_url: str
    page_state_summary: str
    action_record: AgentActionRecord
    screenshot_hash: Optional[str] = None
    previous_block_hash: str
    block_hash: str
