"""
SevaAgent National Scholarship Portal (NSP 2.0) Emulator Adapter
Interacts with the high-fidelity local Starlette government portal mirror on port 8765.
Supports normal mode and adversarial layout-morphing mode for proving agent adaptability.
"""

from typing import Dict, Any, Optional
from playwright.async_api import Page
from seva_agent.portal.base_adapter import BasePortalAdapter
from seva_agent.core.config import EMULATOR_BASE_URL


class NSPEmulatorAdapter(BasePortalAdapter):
    def __init__(self, port: int = 8765, simulate_layout_shift: bool = False):
        self._base_url = f"http://127.0.0.1:{port}"
        self.simulate_layout_shift = simulate_layout_shift

    @property
    def portal_name(self) -> str:
        return "National Scholarship Portal (NSP 2.0 - Simulated Emulator)"

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def is_live_production(self) -> bool:
        return False

    async def navigate_to_entry_point(self, page: Page) -> Dict[str, Any]:
        """Navigates to emulator student registration with resilient page loading."""
        url = f"{self._base_url}/register"
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=10000)
        except Exception:
            await page.goto(url, timeout=5000)

        try:
            title = await page.title()
        except Exception:
            title = "National Scholarship Portal - Registration"

        # If layout shift scenario is active, dynamically mutate an input ID in the DOM
        if self.simulate_layout_shift:
            await page.evaluate("""() => {
                const nameInput = document.getElementById('full_name');
                if (nameInput) {
                    nameInput.id = 'applicant_legal_identity_v2';
                    nameInput.name = 'candidate_full_name_shifted';
                    // Label remains semantically 'Full Name (as in Aadhaar)'
                }
            }""")

        return {
            "navigated_url": url,
            "page_title": title,
            "mode": "TEST_EMULATOR",
            "layout_shifted": self.simulate_layout_shift
        }

    async def detect_page_stage(self, page: Page) -> str:
        url = page.url
        content = await page.content()
        if "/register" in url:
            return "STEP_1_REGISTRATION"
        elif "/application/scheme" in url:
            return "STEP_2_SCHEME"
        elif "/application/academic" in url:
            return "STEP_3_ACADEMIC"
        elif "/application/banking" in url:
            return "STEP_4_BANKING"
        elif "/application/documents" in url:
            return "STEP_5_DOCUMENTS"
        elif "/application/captcha" in url:
            return "STEP_6_CAPTCHA"
        elif "/application/otp" in url:
            return "STEP_7_OTP"
        elif "/application/success" in url:
            return "STEP_8_CONFIRMATION"
        return "UNKNOWN_PAGE"

    async def detect_security_challenge(self, page: Page) -> Optional[Dict[str, Any]]:
        url = page.url
        if "/application/captcha" in url:
            img = await page.query_selector("#captcha_img")
            return {
                "type": "CAPTCHA",
                "element_found": img is not None,
                "prompt": "Visual Security CAPTCHA Challenge"
            }
        elif "/application/otp" in url:
            inp = await page.query_selector("#otp_input")
            return {
                "type": "OTP",
                "element_found": inp is not None,
                "prompt": "Mobile OTP Verification Challenge"
            }
        return None
