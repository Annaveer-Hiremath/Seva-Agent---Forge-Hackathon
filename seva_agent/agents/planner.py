"""
SevaAgent Planner Agent
Formulates high-level execution strategy, tracks task milestones,
and performs dynamic re-planning on unexpected DOM states, validation errors, or portal shifts.
"""

from typing import List, Dict, Any, Optional
from seva_agent.core.state import OrchestrationState


class PlannerAgent:
    """
    Strategic multi-agent planner responsible for breaking complex scholarship
    application workflows into atomic stages and handling dynamic re-planning.
    """

    DEFAULT_PLAN = [
        "1. Intake & parse citizen profile and supporting official documents",
        "2. Evaluate statutory eligibility across Central and State scholarship schemes",
        "3. Cross-validate OCR records against declared data and verify document integrity",
        "4. Initialize Playwright browser and navigate to target portal",
        "5. Complete Step 1: Aadhaar e-KYC and student registration",
        "6. Complete Step 2: Domicile, category, and scholarship scheme selection",
        "7. Complete Step 3: Academic qualifications and merit percentage entry",
        "8. Complete Step 4: DBT bank account and annual family income declaration",
        "9. Complete Step 5: Multi-document upload (Marksheet, Income, Caste, Passbook)",
        "10. Trigger Human-In-The-Loop CAPTCHA challenge resolution",
        "11. Trigger Human-In-The-Loop Mobile OTP verification",
        "12. Verify official submission, extract Application ID & seal tamper-evident audit ledger"
    ]

    def __init__(self):
        pass

    def initialize_plan(self, state: OrchestrationState) -> List[str]:
        """Initializes the standard milestone plan."""
        state.plan_steps = list(self.DEFAULT_PLAN)
        state.current_step_index = 0
        state.log("PlannerAgent", f"Formulated {len(state.plan_steps)}-stage autonomous execution plan.")
        return state.plan_steps

    def advance_step(self, state: OrchestrationState, step_name: str):
        """Marks current step as accomplished and advances pointer."""
        state.log("PlannerAgent", f"Milestone accomplished: {step_name}")
        if state.current_step_index < len(state.plan_steps) - 1:
            state.current_step_index += 1
            state.form_filling_progress = (state.current_step_index / len(state.plan_steps)) * 100.0

    def replan_on_failure(self, state: OrchestrationState, failure_reason: str, failed_stage: str) -> Dict[str, Any]:
        """
        Dynamic Re-planning Engine:
        Diagnoses error type and synthesizes compensatory sub-steps.
        """
        state.replan_count += 1
        replan_msg = (
            f"Dynamic Re-plan #{state.replan_count} triggered at stage '{failed_stage}'. "
            f"Reason: {failure_reason}"
        )
        state.replan_history.append(replan_msg)
        state.log("PlannerAgent", replan_msg)

        strategy = {
            "action": "RETRY_WITH_COMPENSATION",
            "compensatory_steps": []
        }

        if "timeout" in failure_reason.lower() or "not found" in failure_reason.lower():
            strategy["compensatory_steps"] = [
                "1. Scroll viewport into center",
                "2. Wait 2000ms for dynamic DOM rendering / AJAX completion",
                "3. Try secondary CSS/XPath selector fallback",
                "4. Dispatch native JavaScript focus and click events"
            ]
        elif "captcha" in failure_reason.lower():
            strategy["compensatory_steps"] = [
                "1. Refresh CAPTCHA image challenge on portal",
                "2. Capture new screenshot of challenge",
                "3. Request HITL re-entry"
            ]
        elif "otp" in failure_reason.lower():
            strategy["compensatory_steps"] = [
                "1. Clear OTP input boxes",
                "2. Request fresh OTP verification from user"
            ]
        elif "validation" in failure_reason.lower() or "discrepancy" in failure_reason.lower():
            strategy["compensatory_steps"] = [
                "1. Inspect portal inline error messages",
                "2. Align input formatting with portal specification (e.g., remove dashes/spaces from Aadhaar)",
                "3. Re-fill affected fields and re-verify"
            ]
        else:
            strategy["compensatory_steps"] = [
                "1. Capture diagnostic snapshot",
                "2. Reload current stage page",
                "3. Resume execution from last verified checkpoint"
            ]

        return strategy
