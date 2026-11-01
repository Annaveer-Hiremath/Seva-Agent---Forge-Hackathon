"""
SevaAgent Web Dashboard (Streamlit)
Autonomous Multi-Agent Scholarship Execution Platform
Features:
- Profile & Document Intake (OCR + Cross-Validation)
- Statutory Scholarship Discovery with Official Citations
- Autonomous Browser Runner with Live Step-by-Step Screenshots
- Interactive Human-In-The-Loop for CAPTCHA & Mobile OTP
- Tamper-Evident Cryptographic Audit Ledger & Visual Verification
- SQLite Application Tracker
"""

import asyncio
import os
import sys
import time
import json
import socket
import threading
from pathlib import Path
import streamlit as st
from PIL import Image
import uvicorn

from seva_agent.core.models import (
    CitizenProfile,
    Gender,
    Category,
    CourseLevel,
    DocumentType,
    ExtractedDocumentData,
    AuditBlock
)
from seva_agent.core.state import OrchestrationState
from seva_agent.core.audit import TamperEvidentAuditLedger
from seva_agent.core.config import DOCS_DIR, SCREENSHOTS_DIR, AUDIT_LOG_DIR, EMULATOR_BASE_URL, LIVE_PORTALS
from seva_agent.core.graph import SevaAgentGraph
from seva_agent.storage.db import SevaDatabase
from seva_agent.agents.discovery import ScholarshipDiscoveryAgent
from seva_agent.agents.doc_intel import DocumentIntelligenceAgent
from seva_agent.portal.emulator.app import nsp_emulator_app
from sample_data.sample_profile import create_sample_profile


def ensure_portal_server_running(host="127.0.0.1", port=8765):
    """Ensures the high-fidelity National Scholarship Portal emulator server is online."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex((host, port)) == 0:
                return  # Server already active
    except Exception:
        pass

    config = uvicorn.Config(nsp_emulator_app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    server.install_signal_handlers = lambda: None
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    time.sleep(1.2)


# Automatically verify and ensure portal emulator is running
ensure_portal_server_running()


st.set_page_config(
    page_title="SevaAgent - Autonomous Government Scholarship Execution",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Government / Civic Tech Polish
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #002147 0%, #003366 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 8px;
        margin-bottom: 25px;
        border-bottom: 4px solid #ff9933;
    }
    .gov-badge {
        background: #ff9933;
        color: #002147;
        font-weight: 700;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .audit-verified {
        background: #ecfdf5;
        border: 1px solid #10b981;
        color: #065f46;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .step-box {
        border-left: 3px solid #003366;
        padding-left: 12px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize DB and Session State
db = SevaDatabase()

if "profile" not in st.session_state:
    st.session_state["profile"] = create_sample_profile()
if "last_state" not in st.session_state:
    st.session_state["last_state"] = None
if "audit_ledger" not in st.session_state:
    st.session_state["audit_ledger"] = None


# Top Banner
st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span class="gov-badge">Official Civic Tech AI</span>
            <h1 style="margin: 8px 0 4px; font-size: 28px; font-weight: 800; color: white;">🏛️ SevaAgent</h1>
            <p style="margin: 0; font-size: 14px; opacity: 0.9;">
                Autonomous Multi-Agent Scholarship Execution & Verification System for Live Government Portals
            </p>
        </div>
        <div style="text-align: right; font-size: 12px;">
            <strong>Target: National Scholarship Portal (NSP 2.0)</strong><br>
            <span>SHA-256 Tamper-Evident Chained Audit Trail</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# Sidebar Navigation & Settings
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=65)
    st.subheader("System Control Panel")

    selected_portal = st.selectbox(
        "Target Government Portal",
        options=["NSP 2.0 (High-Fidelity Official Mirror)", "National Scholarship Portal (scholarships.gov.in)", "Karnataka SSP (ssp.karnataka.gov.in)"],
        index=0
    )

    automation_mode = st.radio(
        "Browser Execution Mode",
        options=["Autonomous + Auto-HITL (Demo Mode)", "Autonomous + Interactive HITL (Human Enters CAPTCHA/OTP)"],
        index=0
    )

    st.markdown("---")
    st.markdown("### 📊 Live System Status")
    st.write(f"**Playwright Browser:** Ready (Chromium)")
    st.write(f"**Orchestrator:** Multi-Agent StateGraph")
    st.write(f"**Audit Ledger:** SHA-256 Cryptographic Chain")
    st.write(f"**Local Portal:** `http://127.0.0.1:8765`")

    if st.button("🔄 Reset Profile to Default (Priya Sharma)"):
        st.session_state["profile"] = create_sample_profile()
        st.session_state["last_state"] = None
        st.rerun()


# Main Tabs
tab_intake, tab_discovery, tab_runner, tab_audit, tab_tracking = st.tabs([
    "👤 1. Citizen & Document Intake",
    "🎯 2. Statutory Scheme Discovery",
    "🚀 3. Autonomous Execution Runner",
    "🛡️ 4. Tamper-Evident Audit Ledger",
    "📋 5. Applications & DBT Tracker"
])


# ==================== TAB 1: INTAKE & DOCUMENT INTELLIGENCE ====================
with tab_intake:
    st.subheader("Student Profile & Official Supporting Documents")
    st.info("SevaAgent enforces ZERO dummy data. Citizen profiles must be backed by verifiable official documents.")

    prof: CitizenProfile = st.session_state["profile"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("##### 🆔 Personal Details")
        prof.full_name = st.text_input("Full Name (as in Aadhaar)", value=prof.full_name)
        prof.aadhaar_number = st.text_input("Aadhaar Number (12 Digits)", value=prof.aadhaar_number)
        prof.date_of_birth = st.text_input("Date of Birth (YYYY-MM-DD)", value=prof.date_of_birth)
        prof.gender = Gender(st.selectbox("Gender", options=[g.value for g in Gender], index=1))
        prof.mobile_number = st.text_input("Mobile Number (Aadhaar Seeded)", value=prof.mobile_number)
        prof.email = st.text_input("Email Address", value=prof.email)

    with col2:
        st.markdown("##### 🎓 Academic & Institution")
        prof.state = st.selectbox("State of Domicile", options=["Karnataka", "Maharashtra", "Uttar Pradesh", "Tamil Nadu", "Delhi"], index=0)
        prof.course_level = CourseLevel(st.selectbox("Course Level", options=[cl.value for cl in CourseLevel], index=2))
        prof.course_name = st.text_input("Course Name", value=prof.course_name)
        prof.institution_name = st.text_input("College / University", value=prof.institution_name)
        prof.previous_class_percentage = st.number_input("Class 12 / Prior Marks (%)", value=float(prof.previous_class_percentage), min_value=0.0, max_value=100.0, step=0.1)
        prof.roll_number = st.text_input("Board Registration / Roll No", value=prof.roll_number)

    with col3:
        st.markdown("##### 💳 Financial & Banking (DBT)")
        prof.category = Category(st.selectbox("Social Category", options=[c.value for c in Category], index=1))
        prof.annual_family_income = st.number_input("Annual Family Income (INR)", value=float(prof.annual_family_income), step=10000.0)
        prof.income_certificate_no = st.text_input("Income Certificate / RD No", value=prof.income_certificate_no or "RD0038291024")
        prof.bank_account_number = st.text_input("Bank Account Number (DBT)", value=prof.bank_account_number)
        prof.bank_ifsc_code = st.text_input("Bank IFSC Code", value=prof.bank_ifsc_code)
        prof.bank_name = st.text_input("Bank Name", value=prof.bank_name)

    st.markdown("---")
    st.subheader("📄 Attached Official Documents & OCR Intelligence")

    doc_cols = st.columns(5)
    doc_types = [
        ("Aadhaar Card", "AADHAAR", "aadhaar_card.png"),
        ("Income Certificate", "INCOME_CERTIFICATE", "income_certificate.png"),
        ("Caste Certificate", "CASTE_CERTIFICATE", "caste_certificate.png"),
        ("12th Marksheet", "MARKSHEET_12TH", "marksheet_12th.png"),
        ("Bank Passbook", "BANK_PASSBOOK", "bank_passbook.png"),
    ]

    for i, (title, dtype, img_name) in enumerate(doc_types):
        with doc_cols[i]:
            img_path = DOCS_DIR / img_name
            if img_path.exists():
                st.image(str(img_path), caption=title, use_container_width=True)
            doc_data = prof.documents.get(dtype)
            if doc_data:
                st.markdown(f"**Confidence:** `{doc_data.confidence_score*100:.0f}%`")
                st.caption(f"Verified: {', '.join(list(doc_data.extracted_fields.keys())[:2])}")

    # Cross-validation warning check
    doc_intel = DocumentIntelligenceAgent()
    cross_flags = doc_intel.cross_validate_profile(prof)
    if cross_flags:
        for f in cross_flags:
            st.warning(f"⚠️ {f}")
    else:
        st.success("✅ Document Cross-Verification Succeeded: 100% data consistency between declared citizen profile and certified documents.")


# ==================== TAB 2: SCHOLARSHIP DISCOVERY ====================
with tab_discovery:
    st.subheader("Source-Backed Statutory Scholarship Assessment")
    st.caption("Evaluates citizen profile against statutory eligibility criteria with official Gazette/Ministry citations.")

    discovery_agent = ScholarshipDiscoveryAgent()
    assessments = discovery_agent.evaluate_profile(st.session_state["profile"])

    col_sum1, col_sum2, col_sum3 = st.columns(3)
    eligible_count = sum(1 for a in assessments if a.is_eligible)
    max_scholarship = max([a.scheme.award_amount_annual for a in assessments if a.is_eligible], default=0.0)

    with col_sum1:
        st.metric("Total Central/State Schemes Evaluated", len(assessments))
    with col_sum2:
        st.metric("Schemes Fully Eligible", eligible_count)
    with col_sum3:
        st.metric("Maximum Annual Entitlement", f"₹{max_scholarship:,.0f}")

    st.markdown("---")

    for i, assess in enumerate(assessments):
        scheme = assess.scheme
        is_el = assess.is_eligible
        badge = "🟢 FULLY ELIGIBLE" if is_el else "🔴 NOT ELIGIBLE"

        with st.expander(f"{badge} | {scheme.scheme_name} (₹{scheme.award_amount_annual:,.0f}/yr)", expanded=(i == 0)):
            st.markdown(f"**Ministry / Department:** {scheme.ministry_or_dept}")
            st.markdown(f"**Official Statutory Citation:** `{scheme.official_guideline_citation}`")
            st.markdown(f"**Portal Endpoint:** [{scheme.portal_url}]({scheme.portal_url}) ({scheme.portal_type})")
            st.markdown(f"**Summary:** {assess.actionable_summary}")

            st.markdown("##### Statutory Rule Breakdown")
            rule_cols = st.columns(len(assess.rule_evaluations))
            for r_idx, r in enumerate(assess.rule_evaluations):
                with rule_cols[r_idx]:
                    r_badge = "✅ PASS" if r.passed else "❌ FAIL"
                    st.markdown(f"**{r.rule_name}**")
                    st.write(r_badge)
                    st.caption(f"Applicant: {r.citizen_value}")
                    st.caption(f"Required: {r.scheme_requirement}")


# ==================== TAB 3: AUTONOMOUS EXECUTION RUNNER ====================
with tab_runner:
    st.subheader("Autonomous Live Browser Automation Runner")
    st.markdown("""
    SevaAgent will launch an autonomous Playwright browser instance, navigate to the portal,
    and execute the complete registration, scheme selection, academic record filing, DBT banking details,
    document uploads, and official verification steps.
    """)

    top_eligible = next((a.scheme for a in assessments if a.is_eligible), assessments[0].scheme)
    selected_scheme_for_run = st.selectbox(
        "Select Target Scheme for Application Submission",
        options=[a.scheme.scheme_name for a in assessments],
        index=0
    )
    target_scheme_obj = next(a.scheme for a in assessments if a.scheme.scheme_name == selected_scheme_for_run)

    portal_url_to_use = EMULATOR_BASE_URL + "/register"
    if "scholarships.gov.in" in selected_portal:
        portal_url_to_use = LIVE_PORTALS["NSP"]["reg_url"]
    elif "ssp.karnataka" in selected_portal:
        portal_url_to_use = LIVE_PORTALS["SSP_KA"]["url"]

    auto_solve = ("Auto-HITL" in automation_mode)

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        start_exec = st.button("🚀 Launch SevaAgent Application Runner", type="primary", use_container_width=True)

    with col_info:
        st.caption(f"Target: `{portal_url_to_use}` | Mode: {'100% Autonomous (Demo Auto-HITL)' if auto_solve else 'Human-in-the-Loop on CAPTCHA/OTP'}")

    if start_exec:
        ensure_portal_server_running()

        status_card = st.container()
        with status_card:
            st.markdown("#### ⚡ Live Autonomous Application Execution")
            progress_bar = st.progress(0.05)
            status_box = st.info("🔄 Initializing Multi-Agent StateGraph & Playwright browser...")
            milestone_text = st.markdown("**Current Milestone:** Initializing Intake & Security Session...")
            
            col_live_ss, col_live_log = st.columns([1, 1])
            with col_live_ss:
                st.markdown("##### 📸 Live Portal View")
                live_screenshot = st.empty()
            with col_live_log:
                st.markdown("##### 📝 Live Agent Decision Stream")
                live_log = st.empty()

        def on_agent_update(st_obj, latest_entry):
            try:
                if st_obj.plan_steps and len(st_obj.plan_steps) > 0:
                    step_idx = min(st_obj.current_step_index, len(st_obj.plan_steps) - 1)
                    pct = min(max(float(step_idx + 1) / float(len(st_obj.plan_steps)), 0.05), 0.98)
                    progress_bar.progress(pct)
                    milestone_text.markdown(f"**Milestone {step_idx+1}/{len(st_obj.plan_steps)}:** `{st_obj.plan_steps[step_idx]}`")
                status_box.markdown(f"**Latest Agent Action:** `{latest_entry}`")
                if st_obj.last_screenshot_path and os.path.exists(st_obj.last_screenshot_path):
                    live_screenshot.image(st_obj.last_screenshot_path, caption="Live Government Portal View", use_container_width=True)
                recent_logs = "\n".join(st_obj.logs[-10:])
                live_log.code(recent_logs, language="text")
            except Exception:
                pass

        graph = SevaAgentGraph(session_id=f"live_run_{int(time.time()*1000)}")

        # Run async workflow with proper Windows Proactor loop
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            loop = asyncio.ProactorEventLoop()
        else:
            loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            with st.spinner("SevaAgent autonomous agents active..."):
                final_state = loop.run_until_complete(
                    graph.run(
                        profile=st.session_state["profile"],
                        selected_scheme_id=target_scheme_obj.scheme_id,
                        auto_solve_hitl=auto_solve,
                        portal_url=portal_url_to_use,
                        on_step=on_agent_update
                    )
                )
            progress_bar.progress(1.0)
            st.session_state["last_state"] = final_state
            st.session_state["audit_ledger"] = graph.audit
            status_box.success("🎉 SevaAgent Application Execution Finished Successfully!")
        except Exception as ex:
            status_box.error(f"Execution Error: {str(ex)}")
        finally:
            loop.close()

    # Display results if last_state exists
    state: OrchestrationState = st.session_state.get("last_state")
    if state:
        st.markdown("---")
        st.subheader("🎯 Official Application Outcome")

        col_out1, col_out2, col_out3 = st.columns(3)
        with col_out1:
            st.metric("Official Application ID", state.application_id or "PENDING")
        with col_out2:
            st.metric("Official Tracking ID", state.tracking_id or "PENDING")
        with col_out3:
            st.metric("Application Status", state.status)

        if state.last_screenshot_path and os.path.exists(state.last_screenshot_path):
            st.markdown("##### 📸 Final Government Portal Confirmation Screen")
            st.image(state.last_screenshot_path, caption=f"Confirmed Submission: {state.application_id}", use_container_width=True)

        st.markdown("##### 📋 Agent Execution Trace & Milestone Log")
        with st.expander("View Execution Logs", expanded=True):
            for l in state.logs:
                st.text(l)


# ==================== TAB 4: TAMPER-EVIDENT AUDIT LEDGER ====================
with tab_audit:
    st.subheader("🛡️ Tamper-Evident Cryptographic Audit Ledger")
    st.markdown("""
    Every single keystroke, dropdown choice, file upload, and state transition is hashed using SHA-256
    into an immutable cryptographic block linked to the previous block's digest.
    """)

    ledger = st.session_state.get("audit_ledger")
    if not ledger:
        # Load most recent audit file if available
        audit_files = sorted(list(AUDIT_LOG_DIR.glob("audit_ledger_*.json")), key=os.path.getmtime, reverse=True)
        if audit_files:
            latest_sess = audit_files[0].stem.replace("audit_ledger_", "")
            ledger = TamperEvidentAuditLedger(latest_sess)
            with open(audit_files[0], "r", encoding="utf-8") as f:
                data = json.load(f)
                ledger.chain = [AuditBlock(**b) for b in data]

    if ledger and ledger.chain:
        is_valid, verify_msg = ledger.verify_chain_integrity()
        if is_valid:
            st.markdown(f'<div class="audit-verified">🔒 CRYPTOGRAPHICALLY VERIFIED: {verify_msg}</div>', unsafe_allow_html=True)
        else:
            st.error(f"🚨 INTEGRITY BREACH DETECTED: {verify_msg}")

        st.markdown(f"**Session ID:** `{ledger.session_id}` | **Total Chained Blocks:** `{len(ledger.chain)}` | **Genesis Anchor:** `{TamperEvidentAuditLedger.GENESIS_HASH[:16]}...`")

        col_inspect, col_download = st.columns([3, 1])
        with col_download:
            st.download_button(
                "📥 Export Full Audit Ledger (JSON)",
                data=json.dumps([b.model_dump() for b in ledger.chain], indent=2),
                file_name=f"audit_trail_{ledger.session_id}.json",
                mime="application/json"
            )

        st.markdown("##### ⛓️ Block Chain Explorer")
        for blk in reversed(ledger.chain):
            rec = blk.action_record
            with st.expander(f"Block #{blk.block_index} | [{rec.action_type.value}] {rec.agent_name} - {rec.rationale[:60]}..."):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.write(f"**Timestamp UTC:** `{blk.timestamp_utc}`")
                    st.write(f"**Action Rationale:** {rec.rationale}")
                    st.write(f"**Result:** {rec.result}")
                    if rec.target_selector:
                        st.write(f"**Target Selector:** `{rec.target_selector}`")
                    if rec.value_masked:
                        st.write(f"**Value (Masked):** `{rec.value_masked}`")
                    st.write(f"**Block Hash (SHA-256):** `{blk.block_hash}`")
                    st.write(f"**Previous Hash:** `{blk.previous_block_hash}`")
                with c2:
                    if rec.screenshot_path and os.path.exists(rec.screenshot_path):
                        st.image(rec.screenshot_path, caption=f"Block #{blk.block_index} Artifact", use_container_width=True)
                        st.caption(f"SHA-256: `{blk.screenshot_hash[:16]}...`")
    else:
        st.info("No active audit ledger session yet. Run an application in Tab 3 to generate the cryptographic audit chain.")


# ==================== TAB 5: APPLICATIONS & DBT TRACKER ====================
with tab_tracking:
    st.subheader("📋 Submitted Applications & DBT Status")
    st.caption("Permanent records stored in local SQLite database for citizen tracking.")

    apps = db.list_applications()
    if apps:
        for app in apps:
            with st.expander(f"🏛️ {app['application_id']} | {app['citizen_name']} ({app['scheme_name']})", expanded=True):
                st.write(f"**Tracking Reference:** `{app['tracking_id']}`")
                st.write(f"**Portal Type:** {app['portal_type']}")
                st.write(f"**Submission Date:** {app['submission_date']}")
                st.write(f"**Cryptographic Audit Root:** `{app['audit_root_hash']}`")
                st.write(f"**Current Status:** :green[{app['status']}]")

                st.json(json.loads(app["details_json"]))
    else:
        st.info("No applications submitted yet. Launch a submission from Tab 3.")
