"""
SevaAgent Live Official National Scholarship Portal Adapter
Interacts with the actual live Government of India National Scholarship Portal (NSP)
at https://scholarships.gov.in and https://scholarships.gov.in/otrapplication/#/
"""

import asyncio
from typing import Dict, Any, Optional
from playwright.async_api import Page
from seva_agent.portal.base_adapter import BasePortalAdapter


class NSPLiveAdapter(BasePortalAdapter):
    LIVE_PORTAL_URL = "https://scholarships.gov.in"
    LIVE_OTR_URL = "https://scholarships.gov.in/otrapplication/#/"

    def __init__(self):
        pass

    @property
    def portal_name(self) -> str:
        return "National Scholarship Portal (LIVE Official Portal - scholarships.gov.in)"

    @property
    def base_url(self) -> str:
        return self.LIVE_PORTAL_URL

    @property
    def is_live_production(self) -> bool:
        return True

    async def navigate_to_entry_point(self, page: Page) -> Dict[str, Any]:
        """
        Navigates to the live official NSP portal and closes any public advisories or modals.
        """
        await page.goto(self.LIVE_PORTAL_URL, wait_until="networkidle", timeout=30000)
        title = await page.title()

        # Handle any advisory dialogs if present on live portal
        try:
            close_btn = page.get_by_role("button", name="Close")
            if await close_btn.is_visible(timeout=2000):
                await close_btn.click()
        except Exception:
            pass

        return {
            "navigated_url": page.url,
            "page_title": title,
            "mode": "LIVE_OFFICIAL_PORTAL",
            "is_official_domain": "scholarships.gov.in" in page.url
        }

    async def navigate_to_otr_registration(self, page: Page) -> Dict[str, Any]:
        """
        Navigates into the One Time Registration (OTR) flow on the live official portal.
        """
        await page.goto(f"{self.LIVE_OTR_URL}login-page", wait_until="networkidle", timeout=30000)

        # Dismiss modal if present on OTR
        try:
            close_btn = page.locator("button:has-text('Close')")
            if await close_btn.is_visible(timeout=3000):
                await close_btn.click()
        except Exception:
            pass

        # Locate and click 'Register' tab or button
        try:
            register_link = page.locator("a:has-text('Register'), button:has-text('Register')").first
            if await register_link.is_visible(timeout=4000):
                await register_link.click()
                await asyncio.sleep(1.0)
        except Exception:
            pass

        return {
            "current_url": page.url,
            "page_title": await page.title()
        }

    async def detect_page_stage(self, page: Page) -> str:
        url = page.url
        content = await page.content()

        if "scholarships.gov.in" in url and "otrapplication" not in url:
            return "LIVE_NSP_HOMEPAGE"
        elif "login-page" in url or "otrapplication/#/login" in url:
            return "LIVE_OTR_LOGIN"
        elif "register" in url or "registration" in url or "guidelines" in content.lower():
            return "LIVE_OTR_REGISTRATION_GUIDELINES"
        elif "aadhar" in content.lower() or "mobile" in content.lower():
            return "LIVE_EKYC_VERIFICATION"
        return "LIVE_PORTAL_INTERACTION"

    async def detect_security_challenge(self, page: Page) -> Optional[Dict[str, Any]]:
        """Scans the live DOM for real visual CAPTCHA images or OTP inputs."""
        try:
            captcha_img = page.locator("img[src*='captcha'], img[id*='captcha'], canvas[id*='captcha']")
            if await captcha_img.count() > 0 and await captcha_img.first.is_visible():
                return {
                    "type": "CAPTCHA",
                    "element_found": True,
                    "prompt": "Official Government Visual CAPTCHA Detected"
                }

            otp_inp = page.locator("input[placeholder*='OTP'], input[id*='otp'], input[name*='otp']")
            if await otp_inp.count() > 0 and await otp_inp.first.is_visible():
                return {
                    "type": "OTP",
                    "element_found": True,
                    "prompt": "Official UIDAI / Aadhaar Mobile OTP Detected"
                }
        except Exception:
            pass
        return None
