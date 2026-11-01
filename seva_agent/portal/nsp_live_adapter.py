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
        Navigates to the live official NSP portal with robust retries,
        bypassing slow tracking scripts and closing public advisories.
        """
        nav_success = False
        last_err = None

        # Try domcontentloaded first (fast and resilient to slow analytics), fallback to commit
        for wait_strategy in ["domcontentloaded", "commit"]:
            try:
                await page.goto(self.LIVE_PORTAL_URL, wait_until=wait_strategy, timeout=20000)
                nav_success = True
                break
            except Exception as e:
                last_err = e
                await asyncio.sleep(1.0)

        if not nav_success:
            # If both failed, try one more time without waiting
            try:
                await page.goto(self.LIVE_PORTAL_URL, timeout=15000)
            except Exception:
                pass

        try:
            title = await page.title()
        except Exception:
            title = "National Scholarship Portal"

        # Handle any advisory dialogs or overlay popups if present on live portal
        try:
            close_buttons = page.locator("button:has-text('Close'), .modal-header button.close, [aria-label='Close']")
            if await close_buttons.count() > 0:
                await close_buttons.first.click(timeout=1500)
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
        nav_success = False
        for wait_strategy in ["domcontentloaded", "commit"]:
            try:
                await page.goto(f"{self.LIVE_OTR_URL}login-page", wait_until=wait_strategy, timeout=25000)
                nav_success = True
                break
            except Exception:
                await asyncio.sleep(1.0)

        # Wait briefly for Angular SPA hydration
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass

        # Dismiss modal if present on OTR
        try:
            close_btn = page.locator("button:has-text('Close'), .close-btn, .btn-close")
            if await close_btn.count() > 0:
                await close_btn.first.click(timeout=2000)
        except Exception:
            pass

        # Locate and click 'Register' tab or button
        try:
            register_link = page.locator("a:has-text('Register'), button:has-text('Register'), [routerlink*='register']").first
            if await register_link.count() > 0:
                await register_link.click(timeout=3000)
                await asyncio.sleep(1.0)
        except Exception:
            pass

        try:
            title = await page.title()
        except Exception:
            title = "NSP OTR Application"

        return {
            "current_url": page.url,
            "page_title": title
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
