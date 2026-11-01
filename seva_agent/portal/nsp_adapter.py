"""
SevaAgent National Scholarship Portal (NSP) Adapter
Implements selectors and interactions for live NSP 2.0 and local NSP server.
"""

from typing import Dict
from seva_agent.portal.base import GovernmentPortalAdapter
from seva_agent.core.config import EMULATOR_BASE_URL


class NSPAdapter(GovernmentPortalAdapter):
    def __init__(self, use_emulator: bool = True):
        self._use_emulator = use_emulator
        self._base_url = EMULATOR_BASE_URL if use_emulator else "https://scholarships.gov.in"

    @property
    def portal_name(self) -> str:
        return "National Scholarship Portal (NSP 2.0)"

    @property
    def base_url(self) -> str:
        return self._base_url

    def get_registration_selectors(self) -> Dict[str, str]:
        return {
            "full_name": "#full_name, input[name='full_name'], input[placeholder*='Name']",
            "aadhaar_number": "#aadhaar_number, input[name='aadhaar_number'], input[placeholder*='Aadhaar']",
            "dob": "#dob, input[name='dob'], input[type='date']",
            "gender": "#gender, select[name='gender']",
            "mobile_number": "#mobile_number, input[name='mobile_number'], input[type='tel']",
            "email": "#email, input[name='email'], input[type='email']",
            "domicile_state": "#domicile_state, select[name='domicile_state']",
            "category": "#category, select[name='category']",
            "submit_button": "#btn_register_next, button[type='submit'], input[type='submit']"
        }

    def get_scheme_selectors(self) -> Dict[str, str]:
        return {
            "scheme_id": "#scheme_id, select[name='scheme_id']",
            "application_type": "#application_type, select[name='application_type']",
            "course_level": "#course_level, select[name='course_level']",
            "submit_button": "#btn_scheme_next, button[type='submit']"
        }

    def get_academic_selectors(self) -> Dict[str, str]:
        return {
            "institution_name": "#institution_name, input[name='institution_name']",
            "course_name": "#course_name, input[name='course_name']",
            "current_year": "#current_year, input[name='current_year']",
            "board_name": "#board_name, input[name='board_name']",
            "previous_percentage": "#previous_percentage, input[name='previous_percentage']",
            "roll_number": "#roll_number, input[name='roll_number']",
            "passing_year": "#passing_year, input[name='passing_year']",
            "submit_button": "#btn_academic_next, button[type='submit']"
        }

    def get_banking_selectors(self) -> Dict[str, str]:
        return {
            "bank_ifsc": "#bank_ifsc, input[name='bank_ifsc']",
            "bank_name": "#bank_name, input[name='bank_name']",
            "bank_account": "#bank_account, input[name='bank_account']",
            "bank_account_confirm": "#bank_account_confirm, input[name='bank_account_confirm']",
            "annual_income": "#annual_income, input[name='annual_income']",
            "income_cert_no": "#income_cert_no, input[name='income_cert_no']",
            "submit_button": "#btn_banking_next, button[type='submit']"
        }

    def get_document_selectors(self) -> Dict[str, str]:
        return {
            "file_marksheet": "#file_marksheet, input[name='file_marksheet']",
            "file_income": "#file_income, input[name='file_income']",
            "file_caste": "#file_caste, input[name='file_caste']",
            "file_passbook": "#file_passbook, input[name='file_passbook']",
            "submit_button": "#btn_docs_next, button[type='submit']"
        }

    def get_captcha_selectors(self) -> Dict[str, str]:
        return {
            "captcha_image": "#captcha_img, img[src*='captcha']",
            "captcha_input": "#captcha_input, input[name='captcha_input']",
            "submit_button": "#btn_verify_captcha, button[type='submit']"
        }

    def get_otp_selectors(self) -> Dict[str, str]:
        return {
            "otp_input": "#otp_input, input[name='otp_input']",
            "submit_button": "#btn_submit_final, button[type='submit']"
        }

    def get_success_selectors(self) -> Dict[str, str]:
        return {
            "application_id": "#app_id_display",
            "tracking_id": "#tracking_id_display"
        }
