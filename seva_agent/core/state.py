"""
SevaAgent Orchestration State
Defines the shared typed state exchanged across agents in the multi-agent graph.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

from seva_agent.core.models import (
    CitizenProfile,
    ScholarshipScheme,
    EligibilityAssessment,
    ExtractedDocumentData,
    AgentActionRecord
)


class OrchestrationState(BaseModel):
    session_id: str
    status: str = "INITIALIZING"
    current_agent: str = "PlannerAgent"

    # Profile & Ingestion Data
    citizen_profile: Optional[CitizenProfile] = None
    extracted_documents: Dict[str, ExtractedDocumentData] = Field(default_factory=dict)

    # Scholarship Assessment
    discovered_schemes: List[ScholarshipScheme] = Field(default_factory=list)
    eligibility_assessments: List[EligibilityAssessment] = Field(default_factory=list)
    selected_scheme: Optional[ScholarshipScheme] = None

    # High-Level Planner Steps & Dynamic Re-planning
    plan_steps: List[str] = Field(default_factory=list)
    current_step_index: int = 0
    replan_count: int = 0
    replan_history: List[str] = Field(default_factory=list)

    # Human-In-The-Loop (CAPTCHA / OTP only)
    hitl_pending: bool = False
    hitl_challenge_type: Optional[str] = None  # "CAPTCHA" or "OTP"
    hitl_prompt: Optional[str] = None
    hitl_payload: Optional[Dict[str, Any]] = None  # e.g., {"captcha_image": path}
    hitl_response: Optional[str] = None  # e.g., user solved text or OTP code

    # Browser & Execution Status
    portal_target_url: Optional[str] = None
    current_page_title: Optional[str] = None
    last_screenshot_path: Optional[str] = None
    form_filling_progress: float = 0.0  # 0.0 to 100.0%

    # Submission & Official Verification
    application_id: Optional[str] = None
    tracking_id: Optional[str] = None
    submission_timestamp: Optional[str] = None
    acknowledgment_receipt_path: Optional[str] = None

    # Logging & Self-Correction
    logs: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    validation_flags: List[str] = Field(default_factory=list)

    def set_callback(self, cb):
        object.__setattr__(self, "_callback", cb)

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
