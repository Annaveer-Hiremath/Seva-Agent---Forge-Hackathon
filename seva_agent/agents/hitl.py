"""
SevaAgent Human-In-The-Loop (HITL) Controller
Enforces the strict hackathon constraint:
Human-in-the-loop is permitted ONLY for visual CAPTCHA and SMS/Mobile OTP.
All other application workflows execute fully autonomously.
"""

from typing import Optional, Dict, Any, Callable
from seva_agent.core.state import OrchestrationState


class HITLController:
    """
    Manages human hand-off and seamless resumption for CAPTCHA challenges
    and Mobile OTP verifications.
    """

    def __init__(self):
        self._pending_callbacks: Dict[str, Callable] = {}

    def request_captcha_resolution(
        self,
        state: OrchestrationState,
        captcha_image_path: str,
        portal_name: str
    ):
        """
        Pauses autonomous workflow and requests human CAPTCHA input.
        """
        state.hitl_pending = True
        state.hitl_challenge_type = "CAPTCHA"
        state.hitl_prompt = f"Please enter the visual CAPTCHA code shown on the {portal_name} screen."
        state.hitl_payload = {
            "image_path": captcha_image_path,
            "portal": portal_name
        }
        state.hitl_response = None
        state.log("HITLController", f"Autonomous flow paused: Awaiting human CAPTCHA resolution for {portal_name}.")

    def request_otp_verification(
        self,
        state: OrchestrationState,
        mobile_masked: str,
        portal_name: str,
        test_otp_hint: Optional[str] = None
    ):
        """
        Pauses autonomous workflow and requests human Mobile OTP entry.
        """
        state.hitl_pending = True
        state.hitl_challenge_type = "OTP"
        prompt = f"Enter the 6-digit OTP sent to your registered mobile {mobile_masked} to sign the application."
        if test_otp_hint:
            prompt += f" (Test Environment Code: {test_otp_hint})"

        state.hitl_prompt = prompt
        state.hitl_payload = {
            "mobile_masked": mobile_masked,
            "portal": portal_name,
            "test_otp_hint": test_otp_hint
        }
        state.hitl_response = None
        state.log("HITLController", f"Autonomous flow paused: Awaiting human OTP entry for {mobile_masked}.")

    def submit_human_input(self, state: OrchestrationState, response_value: str) -> bool:
        """
        Receives human input, updates state, and signals resumption.
        """
        if not state.hitl_pending:
            return False

        clean_val = response_value.strip()
        state.hitl_response = clean_val
        state.hitl_pending = False
        state.log("HITLController", f"Human input received for {state.hitl_challenge_type}. Resuming autonomous browser agent.")
        return True
