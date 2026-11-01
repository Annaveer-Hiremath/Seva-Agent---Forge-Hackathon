"""
SevaAgent Government Portal Abstract Interface
Base contract for government scholarship portal adapters.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class GovernmentPortalAdapter(ABC):
    @property
    @abstractmethod
    def portal_name(self) -> str:
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    @abstractmethod
    def get_registration_selectors(self) -> Dict[str, str]:
        """Returns mapping of field names to primary and fallback CSS selectors."""
        pass

    @abstractmethod
    def get_scheme_selectors(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_academic_selectors(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_banking_selectors(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_document_selectors(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_captcha_selectors(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_otp_selectors(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_success_selectors(self) -> Dict[str, str]:
        pass
