"""
SevaAgent Orchestration State
Defines the explicit workflow state machine and typed shared state container.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum

from seva_agent.core.models import (
    CitizenProfile,
    ScholarshipScheme,
    EligibilityAssessment,
    ExtractedDocumentData,
    AgentActionDecision,
    AgentActionRecord,
    ApplicationReadinessScore,
    DocumentDiscrepancy
)


class WorkflowState(str, Enum):
    APPLICANT_ONBOARDING = "APPLICANT_ONBOARDING"
    DOCUMENT_ANALYSIS = "DOCUMENT_ANALYSIS"
    ELIGIBILITY_CHECK = "ELIGIBILITY_CHECK"
    APPLICATION_PLANNING = "APPLICATION_PLANNING"
    PORTAL_NAVIGATION = "PORTAL_NAVIGATION"
    PAGE_OBSERVATION = "PAGE_OBSERVATION"
    AI_REASONING = "AI_REASONING"
    ACTION_VALIDATION = "ACTION_VALIDATION"
    ACTION_EXECUTION = "ACTION_EXECUTION"
    RESULT_VERIFICATION = "RESULT_VERIFICATION"
    REPLANNING = "REPLANNING"
    HUMAN_INTERVENTION = "HUMAN_INTERVENTION"
    FINAL_REVIEW = "FINAL_REVIEW"
    SUBMITTED = "SUBMITTED"
    FAILED = "FAILED"


class ExecutionMode(str, Enum):
    TEST_EMULATOR = "TEST_EMULATOR"  # Local high-fidelity mirror (http://127.0.0.1:8765)
    LIVE_OFFICIAL_PORTAL = "LIVE_OFFICIAL_PORTAL"  # Official portal (https://scholarships.gov.in)


class PageObservation(BaseModel):
    timestamp_utc: str
    url: str
    title: str
    heading_text: str = ""
    visible_text_snippet: str = ""
    discovered_inputs: List[Dict[str, Any]] = Field(default_factory=list)
    discovered_buttons: List[Dict[str, Any]] = Field(default_factory=list)
    detected_alerts: List[str] = Field(default_factory=list)
    has_captcha_challenge: bool = False
    has_otp_prompt: bool = False
    screenshot_path: Optional[str] = None


class OrchestrationState(BaseModel):
    session_id: str
    execution_mode: ExecutionMode = ExecutionMode.TEST_EMULATOR
    current_workflow_state: WorkflowState = WorkflowState.APPLICANT_ONBOARDING
    current_agent: str = "PlannerAgent"

    # Profile & Ingestion Data
    citizen_profile: Optional[CitizenProfile] = None
    extracted_documents: Dict[str, ExtractedDocumentData] = Field(default_factory=dict)
    discrepancies: List[DocumentDiscrepancy] = Field(default_factory=list)
    readiness_score: Optional[ApplicationReadinessScore] = None

    # Scholarship Assessment
    discovered_schemes: List[ScholarshipScheme] = Field(default_factory=list)
    eligibility_assessments: List[EligibilityAssessment] = Field(default_factory=list)
    selected_scheme: Optional[ScholarshipScheme] = None

    # High-Level Planner Steps & Dynamic Re-planning
    plan_steps: List[str] = Field(default_factory=list)
    current_step_index: int = 0
    replan_count: int = 0
    replan_history: List[str] = Field(default_factory=list)

    # Adaptive Browser Agent State
    portal_target_url: Optional[str] = None
    current_observation: Optional[PageObservation] = None
    observation_history: List[PageObservation] = Field(default_factory=list)
    current_decision: Optional[AgentActionDecision] = None
    action_history: List[AgentActionRecord] = Field(default_factory=list)
    last_screenshot_path: Optional[str] = None
    form_filling_progress: float = 0.0

    # Human-In-The-Loop (CAPTCHA / OTP only)
    hitl_pending: bool = False
    auto_solve_hitl: bool = False
    hitl_challenge_type: Optional[str] = None  # "CAPTCHA" or "OTP"
    hitl_prompt: Optional[str] = None
    hitl_payload: Optional[Dict[str, Any]] = None  # e.g., {"captcha_image": path}
    hitl_response: Optional[str] = None

    # Official Submission Outcome
    application_id: Optional[str] = None
    tracking_id: Optional[str] = None
    submission_timestamp: Optional[str] = None
    submission_status_summary: str = "IN_PROGRESS"
    is_live_production_run: bool = False
    security_boundary_reason: Optional[str] = None

    # Logging & Traceability
    logs: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    validation_flags: List[str] = Field(default_factory=list)

    def set_callback(self, cb):
        object.__setattr__(self, "_callback", cb)

    @property
    def status(self) -> str:
        if self.current_workflow_state in [WorkflowState.SUBMITTED, WorkflowState.FINAL_REVIEW]:
            return "COMPLETED"
        if self.current_workflow_state == WorkflowState.FAILED:
            return "FAILED"
        return "IN_PROGRESS"

    def log(self, agent_name: str, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{agent_name}] {message}"
        self.logs.append(entry)
        cb = getattr(self, "_callback", None)
        if cb:
            try:
                cb(self, entry)
            except Exception:
                pass
