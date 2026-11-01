"""
SevaAgent Multi-Agent StateGraph Orchestrator
Coordinates Planner, Discovery, Document Intelligence, Validator,
Browser Automation, and HITL agents in a resilient state machine.
"""

import asyncio
import time
from typing import Dict, Any, Optional, Tuple

from seva_agent.core.models import (
    CitizenProfile,
    ScholarshipScheme,
    EligibilityAssessment
)
from seva_agent.core.state import OrchestrationState
from seva_agent.core.audit import TamperEvidentAuditLedger
from seva_agent.core.config import DOCS_DIR
from seva_agent.storage.db import SevaDatabase

from seva_agent.agents.planner import PlannerAgent
from seva_agent.agents.discovery import ScholarshipDiscoveryAgent
from seva_agent.agents.doc_intel import DocumentIntelligenceAgent
from seva_agent.agents.validator import ValidatorAgent
from seva_agent.agents.browser_agent import BrowserAutomationAgent
from seva_agent.agents.hitl import HITLController


class SevaAgentGraph:
    """
    Production-grade multi-agent orchestrator managing the full scholarship application pipeline.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"seva_{int(time.time()*1000)}"
        self.audit = TamperEvidentAuditLedger(self.session_id)
        self.db = SevaDatabase()

        # Agents
        self.planner = PlannerAgent()
        self.discovery = ScholarshipDiscoveryAgent()
        self.doc_intel = DocumentIntelligenceAgent()
        self.validator = ValidatorAgent()
        self.hitl = HITLController()

    async def run(
        self,
        profile: CitizenProfile,
        selected_scheme_id: Optional[str] = None,
        auto_solve_hitl: bool = True,
        portal_url: Optional[str] = None,
        on_step: Optional[Any] = None
    ) -> OrchestrationState:
        """
        Executes the end-to-end multi-agent workflow from intake to submission.
        """
        state = OrchestrationState(
            session_id=self.session_id,
            citizen_profile=profile
        )
        if on_step:
            state.set_callback(on_step)

        # ------------------- 1. PLANNING NODE -------------------
        state.current_agent = "PlannerAgent"
        state.status = "PLANNING"
        self.planner.initialize_plan(state)

        # ------------------- 2. DOCUMENT INTELLIGENCE NODE -------------------
        state.current_agent = "DocumentIntelligenceAgent"
        state.status = "DOC_PROCESSING"
        state.log("DocumentIntelligenceAgent", "Parsing and extracting entities from uploaded official certificates...")

        # Process attached documents
        for doc_key, doc_data in profile.documents.items():
            state.extracted_documents[doc_key] = doc_data
            state.log(
                "DocumentIntelligenceAgent",
                f"Processed {doc_data.doc_type.value} with confidence {doc_data.confidence_score*100:.1f}%. Fields: {list(doc_data.extracted_fields.keys())}"
            )

        # Cross-validate profile vs documents
        discrepancies = self.doc_intel.cross_validate_profile(profile)
        for disc in discrepancies:
            state.validation_flags.append(disc)
            state.log("DocumentIntelligenceAgent", f"Integrity Flag: {disc}")

        self.planner.advance_step(state, "Document Intelligence Processing")

        # ------------------- 3. SCHOLARSHIP DISCOVERY NODE -------------------
        state.current_agent = "ScholarshipDiscoveryAgent"
        state.status = "DISCOVERING"
        state.log("ScholarshipDiscoveryAgent", "Evaluating statutory eligibility against Central and State scholarship databases...")

        assessments = self.discovery.evaluate_profile(profile)
        state.eligibility_assessments = assessments

        # Select target scheme
        if selected_scheme_id:
            target = next((a.scheme for a in assessments if a.scheme.scheme_id == selected_scheme_id), None)
            if target:
                state.selected_scheme = target
        if not state.selected_scheme:
            # Default to top eligible scheme
            eligible = [a for a in assessments if a.is_eligible]
            if eligible:
                state.selected_scheme = eligible[0].scheme
            else:
                state.selected_scheme = assessments[0].scheme

        state.log(
            "ScholarshipDiscoveryAgent",
            f"Selected Scheme: '{state.selected_scheme.scheme_name}' (Award: ₹{state.selected_scheme.award_amount_annual:,.0f}/yr) | Citation: {state.selected_scheme.official_guideline_citation}"
        )
        self.planner.advance_step(state, "Scholarship Discovery & Statutory Matching")

        # ------------------- 4. PRE-SUBMISSION VALIDATION NODE -------------------
        state.current_agent = "ValidatorAgent"
        state.status = "VALIDATING"
        state.log("ValidatorAgent", f"Conducting statutory pre-validation against {state.selected_scheme.scheme_name} rules...")

        valid, validation_errors = self.validator.validate_citizen_profile(profile, state.selected_scheme)
        if not valid:
            state.errors.extend(validation_errors)
            for err in validation_errors:
                state.log("ValidatorAgent", f"Pre-validation error: {err}")
            # Self-healing re-plan
            replan_plan = self.planner.replan_on_failure(state, "Validation checks identified potential issues", "Pre-Validation")
            state.log("ValidatorAgent", f"Self-correction applied: {replan_plan['strategy']}")

        self.planner.advance_step(state, "Pre-Submission Data Validation")

        # ------------------- 5. BROWSER AUTOMATION NODE -------------------
        state.current_agent = "BrowserAutomationAgent"
        state.status = "EXECUTING_BROWSER"
        state.log("BrowserAutomationAgent", "Launching autonomous Playwright browser instance...")

        browser_agent = BrowserAutomationAgent(self.audit, headless=True)
        try:
            success, app_id, trk_id = await browser_agent.run_application_workflow(
                state=state,
                portal_url=portal_url,
                auto_solve_hitl=auto_solve_hitl
            )
            if success:
                state.application_id = app_id
                state.tracking_id = trk_id
                state.status = "COMPLETED"
                state.log("BrowserAutomationAgent", f"Official submission confirmed! Application ID: {app_id}")
            else:
                state.status = "FAILED"
                state.log("BrowserAutomationAgent", "Application flow did not complete successfully.")
        except Exception as e:
            state.status = "FAILED"
            state.errors.append(str(e))
            state.log("BrowserAutomationAgent", f"Execution error: {str(e)}")
            self.planner.replan_on_failure(state, str(e), "Browser Execution")
            await browser_agent.close()

        # ------------------- 6. AUDIT SEAL & DB PERSISTENCE NODE -------------------
        state.current_agent = "AuditAgent"
        audit_summary = self.audit.export_summary()
        state.log(
            "AuditAgent",
            f"Audit chain sealed with {audit_summary['total_actions']} actions. Cryptographic integrity: {audit_summary['cryptographic_integrity']}"
        )

        # Save to database
        if state.application_id:
            self.db.save_application(
                application_id=state.application_id,
                session_id=state.session_id,
                citizen_name=profile.full_name,
                aadhaar_masked=f"XXXX-XXXX-{profile.aadhaar_number[-4:]}",
                scheme_id=state.selected_scheme.scheme_id,
                scheme_name=state.selected_scheme.scheme_name,
                portal_type=state.selected_scheme.portal_type,
                status="SUBMITTED",
                tracking_id=state.tracking_id,
                audit_root_hash=audit_summary.get("latest_block_hash", ""),
                submission_date=time.strftime("%Y-%m-%d %H:%M:%S"),
                details={
                    "course": profile.course_name,
                    "institution": profile.institution_name,
                    "percentage": profile.previous_class_percentage,
                    "annual_income": profile.annual_family_income,
                    "bank_account": f"XXXXXX{profile.bank_account_number[-4:]}",
                    "ifsc": profile.bank_ifsc_code,
                    "plan_steps": state.plan_steps,
                    "replan_count": state.replan_count,
                    "audit_blocks_count": audit_summary["total_actions"]
                }
            )

        return state
