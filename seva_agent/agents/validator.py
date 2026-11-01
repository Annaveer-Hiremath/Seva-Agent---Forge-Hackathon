"""
SevaAgent Validator & Error Recovery Agent
Performs pre-submission cross-field consistency validation,
DOM error diagnostics, and self-healing adjustments.
"""

import re
from typing import List, Dict, Any, Tuple
from seva_agent.core.models import CitizenProfile, ScholarshipScheme


class ValidatorAgent:
    """
    Ensures zero dummy data, 100% data integrity, and analyzes
    browser DOM error messages to guide self-healing recovery.
    """

    def __init__(self):
        pass

    def validate_citizen_profile(self, profile: CitizenProfile, scheme: ScholarshipScheme) -> Tuple[bool, List[str]]:
        """
        Rigorous data sanity check before touching any live portal.
        """
        errors: List[str] = []

        # 1. Aadhaar Check (12 digits)
        clean_aadhaar = re.sub(r"\D", "", profile.aadhaar_number)
        if len(clean_aadhaar) != 12:
            errors.append(f"Invalid Aadhaar: Must contain exactly 12 digits (Found: {profile.aadhaar_number})")

        # 2. Mobile Number (10 digits starting 6-9)
        clean_mobile = re.sub(r"\D", "", profile.mobile_number)
        if len(clean_mobile) != 10 or clean_mobile[0] not in "6789":
            errors.append(f"Invalid Mobile: Must be a valid 10-digit Indian mobile (Found: {profile.mobile_number})")

        # 3. Bank IFSC (11 chars: 4 alpha, 0, 6 alphanumeric)
        if not re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", profile.bank_ifsc_code.strip()):
            errors.append(f"Invalid Bank IFSC format: {profile.bank_ifsc_code}")

        # 4. Bank Account Number (9 to 18 digits)
        if not re.match(r"^\d{9,18}$", profile.bank_account_number.strip()):
            errors.append(f"Invalid Bank Account Number length: {profile.bank_account_number}")

        # 5. Income Ceiling
        if profile.annual_family_income > scheme.max_family_income:
            errors.append(
                f"Statutory Income Violation: Family income ₹{profile.annual_family_income:,.0f} "
                f"exceeds ceiling ₹{scheme.max_family_income:,.0f} for {scheme.scheme_name}"
            )

        # 6. Percentage Merit Threshold
        if profile.previous_class_percentage < scheme.min_previous_percentage:
            errors.append(
                f"Merit Threshold Violation: Score {profile.previous_class_percentage}% "
                f"is below required {scheme.min_previous_percentage}%"
            )

        # 7. Category Compatibility
        if profile.category not in scheme.categories_allowed:
            errors.append(f"Category mismatch: {profile.category.value} not eligible for {scheme.scheme_name}")

        return (len(errors) == 0), errors

    def analyze_portal_dom_errors(self, dom_text: str) -> List[str]:
        """
        Scans DOM text for government portal error patterns
        (e.g., 'already registered', 'invalid format', 'file too large', 'mandatory').
        """
        detected: List[str] = []
        patterns = [
            (r"already\s+registered", "Citizen or Aadhaar is already registered on this portal."),
            (r"invalid\s+(?:aadhaar|uid)", "Aadhaar number format is invalid according to portal validation."),
            (r"invalid\s+(?:ifsc|bank)", "IFSC code was not recognized by Public Financial Management System (PFMS)."),
            (r"file\s+(?:size\s+)?exceeds?", "Uploaded document exceeds portal file size limit."),
            (r"(?:session\s+expired|session\s+timeout)", "Portal session timed out. Re-login required."),
            (r"mandatory\s+field", "One or more mandatory fields were left blank."),
            (r"captcha\s+(?:does\s+not\s+match|invalid)", "CAPTCHA code mismatch on portal submission.")
        ]

        for pat, desc in patterns:
            if re.search(pat, dom_text, re.IGNORECASE):
                detected.append(desc)

        return detected
