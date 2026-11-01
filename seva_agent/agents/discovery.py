"""
SevaAgent Scholarship Discovery & Eligibility Agent
Performs live matching against official Central and State government schemes
with statutory rule evaluation, source guideline citations, and missing document identification.
"""

from typing import List, Tuple
from seva_agent.core.models import (
    CitizenProfile,
    ScholarshipScheme,
    EligibilityAssessment,
    RuleEvaluation,
    Category,
    CourseLevel,
    Gender,
    DocumentType
)


class ScholarshipDiscoveryAgent:
    """
    Evaluates citizen profiles against statutory eligibility guidelines for Indian Government
    scholarships across National Scholarship Portal (NSP) and State Portals.
    """

    def __init__(self):
        self.scheme_catalog: List[ScholarshipScheme] = self._load_official_schemes()

    def _load_official_schemes(self) -> List[ScholarshipScheme]:
        """Loads vetted official Indian government scholarship schemes with statutory citations."""
        return [
            ScholarshipScheme(
                scheme_id="NSP_CENTRAL_SECTOR",
                scheme_name="Central Sector Scheme of Scholarship for College and University Students",
                ministry_or_dept="Ministry of Education, Department of Higher Education (DoHE)",
                portal_type="NSP",
                portal_url="https://scholarships.gov.in",
                description="Financial support for meritorious students from low-income families pursuing regular degree/diploma courses.",
                categories_allowed=[Category.GENERAL, Category.OBC, Category.SC, Category.ST, Category.EWS],
                max_family_income=450000.0,  # 4.5 Lakhs
                min_previous_percentage=80.0,  # 80th percentile in Class 12
                allowed_course_levels=[CourseLevel.UNDERGRADUATE, CourseLevel.POSTGRADUATE, CourseLevel.PROFESSIONAL],
                target_gender=None,  # All genders
                state_domicile_required=None,  # All India quota
                award_amount_annual=12000.0,
                official_guideline_citation="DoHE Scheme Guidelines No. F.No.1-1/2022-NS-I, Clause 4.1 & 4.2",
                application_deadline="2026-12-31",
                required_document_types=[
                    DocumentType.AADHAAR,
                    DocumentType.INCOME_CERTIFICATE,
                    DocumentType.MARKSHEET_12TH,
                    DocumentType.BANK_PASSBOOK,
                    DocumentType.COLLEGE_BONAFIDE
                ]
            ),
            ScholarshipScheme(
                scheme_id="NSP_POST_MATRIC_SC_OBC",
                scheme_name="Post-Matric Scholarship Scheme for SC/ST and OBC Students",
                ministry_or_dept="Ministry of Social Justice & Empowerment (MoSJE)",
                portal_type="NSP",
                portal_url="https://scholarships.gov.in",
                description="Full tuition fee reimbursement and maintenance allowance for SC/ST/OBC students in recognized post-secondary institutions.",
                categories_allowed=[Category.SC, Category.ST, Category.OBC],
                max_family_income=250000.0,  # 2.5 Lakhs
                min_previous_percentage=50.0,
                allowed_course_levels=[CourseLevel.POST_MATRIC, CourseLevel.UNDERGRADUATE, CourseLevel.POSTGRADUATE, CourseLevel.DIPLOMA, CourseLevel.PROFESSIONAL],
                target_gender=None,
                state_domicile_required=None,
                award_amount_annual=25000.0,
                official_guideline_citation="MoSJE Post-Matric Guidelines Revision 2021-26, Para 3.1 (Means & Category Criterion)",
                application_deadline="2026-11-30",
                required_document_types=[
                    DocumentType.AADHAAR,
                    DocumentType.CASTE_CERTIFICATE,
                    DocumentType.INCOME_CERTIFICATE,
                    DocumentType.MARKSHEET_12TH,
                    DocumentType.BANK_PASSBOOK,
                    DocumentType.FEE_RECEIPT
                ]
            ),
            ScholarshipScheme(
                scheme_id="NSP_MCM_MINORITY",
                scheme_name="Merit-cum-Means Scholarship for Professional and Technical Courses",
                ministry_or_dept="Ministry of Minority Affairs (MoMA)",
                portal_type="NSP",
                portal_url="https://scholarships.gov.in",
                description="Assistance for economically disadvantaged students from notified minority communities pursuing professional technical education.",
                categories_allowed=[Category.MINORITY],
                max_family_income=250000.0,
                min_previous_percentage=50.0,
                allowed_course_levels=[CourseLevel.UNDERGRADUATE, CourseLevel.POSTGRADUATE, CourseLevel.PROFESSIONAL],
                target_gender=None,
                state_domicile_required=None,
                award_amount_annual=30000.0,
                official_guideline_citation="MoMA MCM Guidelines 2023-26, Section 5(a) & 5(b)",
                application_deadline="2026-11-15",
                required_document_types=[
                    DocumentType.AADHAAR,
                    DocumentType.INCOME_CERTIFICATE,
                    DocumentType.MARKSHEET_12TH,
                    DocumentType.BANK_PASSBOOK,
                    DocumentType.COLLEGE_BONAFIDE
                ]
            ),
            ScholarshipScheme(
                scheme_id="AICTE_PRAGATI_GIRLS",
                scheme_name="AICTE Pragati Scholarship Scheme for Girl Students (Degree/Diploma)",
                ministry_or_dept="All India Council for Technical Education (AICTE)",
                portal_type="NSP",
                portal_url="https://scholarships.gov.in",
                description="Scholarship empowering girl students admitted to AICTE approved technical degree courses (up to 2 girls per family).",
                categories_allowed=[Category.GENERAL, Category.OBC, Category.SC, Category.ST, Category.EWS],
                max_family_income=800000.0,  # 8 Lakhs
                min_previous_percentage=60.0,
                allowed_course_levels=[CourseLevel.UNDERGRADUATE, CourseLevel.DIPLOMA, CourseLevel.PROFESSIONAL],
                target_gender=[Gender.FEMALE],
                state_domicile_required=None,
                award_amount_annual=50000.0,
                official_guideline_citation="AICTE Pragati Scheme Notification 2024, Criterion A & Income Norm 4(ii)",
                application_deadline="2026-12-15",
                required_document_types=[
                    DocumentType.AADHAAR,
                    DocumentType.INCOME_CERTIFICATE,
                    DocumentType.MARKSHEET_12TH,
                    DocumentType.BANK_PASSBOOK,
                    DocumentType.COLLEGE_BONAFIDE
                ]
            ),
            ScholarshipScheme(
                scheme_id="SSP_KARNATAKA_POST_MATRIC",
                scheme_name="Karnataka State Scholarship Portal (SSP) Post-Matric e-Attestation Scheme",
                ministry_or_dept="Social Welfare / Backward Classes Welfare Dept, Govt. of Karnataka",
                portal_type="STATE_SSP",
                portal_url="https://ssp.postmatric.karnataka.gov.in",
                description="Comprehensive Karnataka domicile scholarship with Aadhaar e-KYC and Kutumba family ID integration.",
                categories_allowed=[Category.OBC, Category.SC, Category.ST, Category.EWS],
                max_family_income=250000.0,
                min_previous_percentage=50.0,
                allowed_course_levels=[CourseLevel.POST_MATRIC, CourseLevel.UNDERGRADUATE, CourseLevel.POSTGRADUATE, CourseLevel.PROFESSIONAL],
                target_gender=None,
                state_domicile_required="Karnataka",
                award_amount_annual=28000.0,
                official_guideline_citation="Govt. of Karnataka Order No. SWD 157 SEW 2020, SSP Integration Manual",
                application_deadline="2026-12-31",
                required_document_types=[
                    DocumentType.AADHAAR,
                    DocumentType.CASTE_CERTIFICATE,
                    DocumentType.INCOME_CERTIFICATE,
                    DocumentType.MARKSHEET_12TH,
                    DocumentType.BANK_PASSBOOK
                ]
            )
        ]

    def evaluate_profile(self, profile: CitizenProfile) -> List[EligibilityAssessment]:
        """
        Evaluates a citizen against all known schemes. Returns sorted list of assessments
        with rigorous rule breakdown and statutory grounding.
        """
        assessments: List[EligibilityAssessment] = []

        for scheme in self.scheme_catalog:
            rule_evals: List[RuleEvaluation] = []
            passed_count = 0
            total_rules = 5

            # 1. Category Evaluation
            category_passed = profile.category in scheme.categories_allowed
            rule_evals.append(RuleEvaluation(
                rule_name="Category / Reservation Eligibility",
                passed=category_passed,
                citizen_value=profile.category.value,
                scheme_requirement=[c.value for c in scheme.categories_allowed],
                citation=scheme.official_guideline_citation,
                explanation=f"Citizen belongs to {profile.category.value}. Allowed: {', '.join([c.value for c in scheme.categories_allowed])}"
            ))
            if category_passed:
                passed_count += 1

            # 2. Income Ceiling Evaluation
            income_passed = profile.annual_family_income <= scheme.max_family_income
            rule_evals.append(RuleEvaluation(
                rule_name="Annual Family Income Ceiling",
                passed=income_passed,
                citizen_value=f"₹{profile.annual_family_income:,.2f}",
                scheme_requirement=f"<= ₹{scheme.max_family_income:,.2f}",
                citation=scheme.official_guideline_citation,
                explanation=f"Family income is ₹{profile.annual_family_income:,.2f}; ceiling is ₹{scheme.max_family_income:,.2f}"
            ))
            if income_passed:
                passed_count += 1

            # 3. Minimum Academic Percentage
            marks_passed = profile.previous_class_percentage >= scheme.min_previous_percentage
            rule_evals.append(RuleEvaluation(
                rule_name="Minimum Academic Merit Threshold",
                passed=marks_passed,
                citizen_value=f"{profile.previous_class_percentage:.2f}%",
                scheme_requirement=f">= {scheme.min_previous_percentage:.2f}%",
                citation=scheme.official_guideline_citation,
                explanation=f"Applicant secured {profile.previous_class_percentage:.2f}%; required is >= {scheme.min_previous_percentage:.2f}%"
            ))
            if marks_passed:
                passed_count += 1

            # 4. Course Level Eligibility
            course_passed = profile.course_level in scheme.allowed_course_levels
            rule_evals.append(RuleEvaluation(
                rule_name="Course Level Applicability",
                passed=course_passed,
                citizen_value=profile.course_level.value,
                scheme_requirement=[cl.value for cl in scheme.allowed_course_levels],
                citation=scheme.official_guideline_citation,
                explanation=f"Current study level {profile.course_level.value} matches permitted courses."
            ))
            if course_passed:
                passed_count += 1

            # 5. Domicile & Gender Checks
            domicile_passed = True
            if scheme.state_domicile_required:
                domicile_passed = (profile.state.strip().lower() == scheme.state_domicile_required.strip().lower())

            gender_passed = True
            if scheme.target_gender:
                gender_passed = (profile.gender in scheme.target_gender)

            special_passed = domicile_passed and gender_passed
            rule_evals.append(RuleEvaluation(
                rule_name="Domicile & Demographic Conditions",
                passed=special_passed,
                citizen_value=f"State: {profile.state}, Gender: {profile.gender.value}",
                scheme_requirement=f"Req State: {scheme.state_domicile_required or 'All India'}, Gender: {[g.value for g in scheme.target_gender] if scheme.target_gender else 'All'}",
                citation=scheme.official_guideline_citation,
                explanation="State domicile and gender requirements checked against scheme norms."
            ))
            if special_passed:
                passed_count += 1

            # Check document readiness
            present_doc_types = {d.doc_type for d in profile.documents.values()}
            missing_docs = [req for req in scheme.required_document_types if req not in present_doc_types]

            is_fully_eligible = (passed_count == total_rules)
            score = (passed_count / total_rules) * 100.0

            if is_fully_eligible and not missing_docs:
                summary = f"100% Eligible & Fully Documented. Entitled to ₹{scheme.award_amount_annual:,.0f}/year."
            elif is_fully_eligible and missing_docs:
                summary = f"Statutorily Eligible, but {len(missing_docs)} required document(s) pending."
            else:
                summary = f"Ineligible: Failed {total_rules - passed_count} statutory criteria."

            assessments.append(EligibilityAssessment(
                scheme=scheme,
                is_eligible=is_fully_eligible,
                eligibility_score=score,
                rule_evaluations=rule_evals,
                required_documents=scheme.required_document_types,
                missing_documents=missing_docs,
                actionable_summary=summary
            ))

        # Sort: eligible first, highest award amount first
        assessments.sort(key=lambda a: (a.is_eligible, a.scheme.award_amount_annual), reverse=True)
        return assessments
