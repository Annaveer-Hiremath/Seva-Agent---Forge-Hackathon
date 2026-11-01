"""
SevaAgent Core Data Models
Pydantic schemas for citizen profiles, scholarship schemes, application records, and audit events.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
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


class ExtractedDocumentData(BaseModel):
    doc_type: DocumentType
    file_path: str
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0)
    extracted_fields: Dict[str, Any] = Field(default_factory=dict)
    raw_text: str = ""
    is_verified: bool = False
    validation_notes: List[str] = Field(default_factory=list)


class CitizenProfile(BaseModel):
    # Personal Identification
    full_name: str
    date_of_birth: str  # YYYY-MM-DD
    gender: Gender
    aadhaar_number: str  # 12-digit Aadhaar or masked
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
    course_name: str  # e.g., "B.Tech Computer Science and Engineering"
    institution_name: str
    institution_code: str = "INST-KA-0941"
    aishe_code: str = "C-12345"
    university_or_board: str
    current_year_of_study: int = 1
    previous_class_percentage: float  # e.g., 88.5%
    previous_passing_year: int = 2025
    roll_number: str

    # Financial & Social Profile
    annual_family_income: float  # e.g., 180000 (INR)
    income_certificate_no: Optional[str] = None
    caste_certificate_no: Optional[str] = None
    ration_card_no: Optional[str] = None
    is_bpl: bool = True

    # Bank Account for DBT (Direct Benefit Transfer)
    bank_account_number: str
    bank_ifsc_code: str
    bank_name: str
    bank_branch: str
    account_holder_name: str

    # Attached documents (path -> ExtractedDocumentData)
    documents: Dict[str, ExtractedDocumentData] = Field(default_factory=dict)


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


class AgentActionType(str, Enum):
    NAVIGATE = "NAVIGATE"
    OBSERVE = "OBSERVE"
    FILL_FIELD = "FILL_FIELD"
    SELECT_OPTION = "SELECT_OPTION"
    CLICK = "CLICK"
    UPLOAD_DOCUMENT = "UPLOAD_DOCUMENT"
    REQUEST_HITL = "REQUEST_HITL"
    SUBMIT_FORM = "SUBMIT_FORM"
    VERIFY_STATE = "VERIFY_STATE"
    REPLAN = "REPLAN"
    ERROR_RECOVERY = "ERROR_RECOVERY"


class AgentActionRecord(BaseModel):
    action_id: str
    timestamp: str
    agent_name: str
    action_type: AgentActionType
    target_selector: Optional[str] = None
    value_masked: Optional[str] = None
    rationale: str
    result: str
    screenshot_path: Optional[str] = None
    execution_time_ms: float = 0.0
    status: str = "SUCCESS"  # SUCCESS, FAILED, RETRYING, WAITING_HITL


class AuditBlock(BaseModel):
    block_index: int
    timestamp_utc: str
    action_record: AgentActionRecord
    state_snapshot_summary: str
    screenshot_hash: Optional[str] = None
    previous_block_hash: str
    block_hash: str
