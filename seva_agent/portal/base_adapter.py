"""
SevaAgent Government Portal Abstract Interface
Base contract for all portal adapters (Live and Simulated).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from playwright.async_api import Page


class BasePortalAdapter(ABC):
    @property
    @abstractmethod
    def portal_name(self) -> str:
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    @property
    @abstractmethod
    def is_live_production(self) -> bool:
        """True if operating against a real government portal, False if simulated emulator."""
        pass

    @abstractmethod
    async def navigate_to_entry_point(self, page: Page) -> Dict[str, Any]:
        """Navigates to portal entry point and dismisses any public notices/popups."""
        pass

    @abstractmethod
    async def detect_page_stage(self, page: Page) -> str:
        """Identifies which application stage is currently open on the page."""
        pass

    @abstractmethod
    async def detect_security_challenge(self, page: Page) -> Optional[Dict[str, Any]]:
        """Detects whether a visual CAPTCHA or mobile OTP challenge is present."""
        pass
