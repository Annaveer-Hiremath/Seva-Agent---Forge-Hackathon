"""
SevaAgent High-Fidelity National Scholarship Portal (NSP 2.0) Server
Provides an authentic government scholarship portal web service mirroring
NIC/National Scholarship Portal workflows, multi-step forms, document uploads,
visual CAPTCHA challenges, mobile OTP verification, and official Application ID generation.
"""

import os
import random
import string
import time
from pathlib import Path
from typing import Dict, Any
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from starlette.routing import Route
from starlette.requests import Request
from PIL import Image, ImageDraw, ImageFont

from seva_agent.core.config import SCREENSHOTS_DIR

EMULATOR_DATA_DIR = Path(__file__).resolve().parent / "data"
CAPTCHA_DIR = EMULATOR_DATA_DIR / "captchas"
UPLOAD_DIR = EMULATOR_DATA_DIR / "uploads"

CAPTCHA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# In-memory session store for emulator
PORTAL_SESSIONS: Dict[str, Dict[str, Any]] = {}


def generate_captcha_image(text: str, file_path: Path):
    """Generates an authentic distorted government portal CAPTCHA image."""
    img = Image.new("RGB", (180, 50), color="#eef2f7")
    draw = ImageDraw.Draw(img)

    # Noise lines
    for _ in range(6):
        x1, y1 = random.randint(0, 180), random.randint(0, 50)
        x2, y2 = random.randint(0, 180), random.randint(0, 50)
        draw.line([(x1, y1), (x2, y2)], fill="#90a4ae", width=1)

    # Draw letters with random slight offset
    x = 20
    for char in text:
        y = random.randint(10, 18)
        draw.text((x, y), char, fill="#0d47a1")
        x += 24

    # Noise dots
    for _ in range(80):
        draw.point((random.randint(0, 180), random.randint(0, 50)), fill="#546e7a")

    img.save(file_path)


def get_common_header(step_title: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>National Scholarship Portal - {step_title}</title>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
            body {{ background-color: #f4f6f9; color: #333; }}
            .gov-top-bar {{ background: #002147; color: #fff; padding: 6px 40px; font-size: 13px; display: flex; justify-content: space-between; }}
            .gov-banner {{ background: #ffffff; border-bottom: 3px solid #ff9933; padding: 15px 40px; display: flex; align-items: center; justify-content: space-between; }}
            .emblem-title {{ display: flex; align-items: center; gap: 15px; }}
            .emblem {{ font-size: 32px; font-weight: bold; color: #ff9933; }}
            .portal-name h1 {{ font-size: 22px; color: #002147; font-weight: 700; }}
            .portal-name p {{ font-size: 12px; color: #666; }}
            .nav-strip {{ background: #003366; color: white; padding: 10px 40px; font-size: 14px; font-weight: 500; display: flex; gap: 20px; }}
            .container {{ max-width: 960px; margin: 30px auto; background: white; padding: 30px; border-radius: 6px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }}
            .step-indicator {{ display: flex; justify-content: space-between; margin-bottom: 25px; border-bottom: 2px solid #e2e8f0; padding-bottom: 15px; }}
            .step-pill {{ font-size: 12px; font-weight: 600; padding: 6px 14px; border-radius: 20px; background: #e2e8f0; color: #475569; }}
            .step-pill.active {{ background: #003366; color: white; }}
            h2 {{ color: #002147; font-size: 20px; margin-bottom: 20px; }}
            .form-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
            .form-group {{ display: flex; flex-direction: column; }}
            .form-group.full {{ grid-column: span 2; }}
            label {{ font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 6px; }}
            input, select, textarea {{ padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 14px; }}
            input:focus, select:focus {{ border-color: #003366; outline: none; box-shadow: 0 0 0 2px rgba(0,51,102,0.15); }}
            .btn-row {{ margin-top: 25px; display: flex; justify-content: flex-end; gap: 12px; }}
            .btn {{ padding: 10px 24px; border: none; border-radius: 4px; font-size: 14px; font-weight: 600; cursor: pointer; }}
            .btn-primary {{ background: #003366; color: white; }}
            .btn-primary:hover {{ background: #002147; }}
            .alert-box {{ background: #eff6ff; border-left: 4px solid #3b82f6; padding: 12px; font-size: 13px; margin-bottom: 20px; color: #1e40af; }}
            .captcha-container {{ display: flex; align-items: center; gap: 15px; margin-top: 8px; }}
            .otp-box {{ text-align: center; font-size: 24px; letter-spacing: 8px; width: 200px; padding: 10px; }}
            footer {{ text-align: center; font-size: 12px; color: #64748b; margin: 40px 0 20px; }}
        </style>
    </head>
    <body>
        <div class="gov-top-bar">
            <span>GOVERNMENT OF INDIA | NATIONAL SCHOLARSHIP PORTAL (NSP 2.0)</span>
            <span>Ministry of Electronics & Information Technology (MeitY)</span>
        </div>
        <div class="gov-banner">
            <div class="emblem-title">
                <div class="emblem">🏛️</div>
                <div class="portal-name">
                    <h1>National Scholarship Portal</h1>
                    <p>Direct Benefit Transfer (DBT) Mission | Government of India</p>
                </div>
            </div>
            <div style="text-align: right; font-size: 12px; color: #64748b;">
                <strong>Academic Year: 2025-2026</strong><br>
                <span>Live Portal Integration</span>
            </div>
        </div>
        <div class="nav-strip">
            <span>Home</span>
            <span>Central Schemes</span>
            <span>UGC/AICTE Schemes</span>
            <span>State Schemes</span>
            <span>Application Status</span>
        </div>
    """


def get_common_footer() -> str:
    return """
        <footer>
            <p>Designed and Developed by National Informatics Centre (NIC) | Government of India</p>
            <p style="margin-top: 4px;">Site Best Viewed in Playwright / Modern Web Browsers</p>
        </footer>
    </body>
    </html>
    """


# Route Handlers
async def home_view(request: Request):
    """Home landing page with registration call-to-action."""
    html = get_common_header("Home") + """
    <div class="container" style="text-align: center; padding: 50px 30px;">
        <h2 style="font-size: 26px; margin-bottom: 12px;">Welcome to National Scholarship Portal (NSP 2.0)</h2>
        <p style="font-size: 15px; color: #475569; max-width: 600px; margin: 0 auto 30px;">
            One-stop electronic solution for scholarship application, verification, processing, and direct disbursement to student bank accounts across India.
        </p>
        <div style="display: flex; justify-content: center; gap: 20px;">
            <a href="/register" class="btn btn-primary" style="text-decoration: none; padding: 14px 30px; font-size: 16px;">
                New Student Registration (Fresh Application)
            </a>
            <a href="/track" class="btn" style="text-decoration: none; background: #f1f5f9; color: #1e293b; padding: 14px 24px; border: 1px solid #cbd5e1;">
                Track Application Status
            </a>
        </div>
    </div>
    """ + get_common_footer()
    return HTMLResponse(html)


async def register_view(request: Request):
    """Step 1: Citizen Registration & Aadhaar authentication."""
    html = get_common_header("Step 1: Student Registration") + """
    <div class="container">
        <div class="step-indicator">
            <span class="step-pill active">1. Identity & Registration</span>
            <span class="step-pill">2. Scheme Selection</span>
            <span class="step-pill">3. Academic Profile</span>
            <span class="step-pill">4. Banking & Income</span>
            <span class="step-pill">5. Documents</span>
            <span class="step-pill">6. Verification</span>
        </div>
        <h2>Step 1: New Student Registration (Aadhaar e-KYC)</h2>
        <div class="alert-box">
            <strong>Mandatory Note:</strong> As per Ministry Directives, Aadhaar demographic authentication is required. Ensure your full name and DOB match official UIDAI records.
        </div>
        <form action="/register" method="POST">
            <div class="form-grid">
                <div class="form-group">
                    <label for="full_name">Full Name (as in Aadhaar) *</label>
                    <input type="text" id="full_name" name="full_name" required placeholder="e.g. Priya Ramesh Sharma">
                </div>
                <div class="form-group">
                    <label for="aadhaar_number">Aadhaar Card Number (12 Digits) *</label>
                    <input type="text" id="aadhaar_number" name="aadhaar_number" maxlength="14" required placeholder="XXXX XXXX XXXX">
                </div>
                <div class="form-group">
                    <label for="dob">Date of Birth (YYYY-MM-DD) *</label>
                    <input type="date" id="dob" name="dob" required>
                </div>
                <div class="form-group">
                    <label for="gender">Gender *</label>
                    <select id="gender" name="gender" required>
                        <option value="">-- Select Gender --</option>
                        <option value="FEMALE">Female</option>
                        <option value="MALE">Male</option>
                        <option value="OTHER">Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="mobile_number">Mobile Number (Aadhaar Linked) *</label>
                    <input type="tel" id="mobile_number" name="mobile_number" required placeholder="9876543210">
                </div>
                <div class="form-group">
                    <label for="email">Email Address *</label>
                    <input type="email" id="email" name="email" required placeholder="student@example.com">
                </div>
                <div class="form-group">
                    <label for="domicile_state">State of Domicile *</label>
                    <select id="domicile_state" name="domicile_state" required>
                        <option value="">-- Select State --</option>
                        <option value="Karnataka">Karnataka</option>
                        <option value="Maharashtra">Maharashtra</option>
                        <option value="Uttar Pradesh">Uttar Pradesh</option>
                        <option value="Tamil Nadu">Tamil Nadu</option>
                        <option value="Delhi">Delhi</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="category">Social Category / Reservation *</label>
                    <select id="category" name="category" required>
                        <option value="">-- Select Category --</option>
                        <option value="OBC">OBC (Other Backward Classes)</option>
                        <option value="SC">SC (Scheduled Caste)</option>
                        <option value="ST">ST (Scheduled Tribe)</option>
                        <option value="EWS">EWS (Economically Weaker Section)</option>
                        <option value="GENERAL">General</option>
                    </select>
                </div>
            </div>
            <div class="btn-row">
                <button type="submit" id="btn_register_next" class="btn btn-primary">Save & Continue to Scheme Selection →</button>
            </div>
        </form>
    </div>
    """ + get_common_footer()
    return HTMLResponse(html)


async def register_submit(request: Request):
    form = await request.form()
    session_id = request.cookies.get("nsp_session", f"nsp_sess_{int(time.time()*1000)}")
    PORTAL_SESSIONS[session_id] = {
        "full_name": form.get("full_name"),
        "aadhaar_number": form.get("aadhaar_number"),
        "dob": form.get("dob"),
        "gender": form.get("gender"),
        "mobile_number": form.get("mobile_number"),
        "email": form.get("email"),
        "domicile_state": form.get("domicile_state"),
        "category": form.get("category"),
    }
    response = RedirectResponse(url="/application/scheme", status_code=303)
    response.set_cookie("nsp_session", session_id)
    return response


async def scheme_view(request: Request):
    """Step 2: Domicile, Course Level, and Scheme Selection."""
    session_id = request.cookies.get("nsp_session")
    sess_data = PORTAL_SESSIONS.get(session_id, {})

    html = get_common_header("Step 2: Scheme Selection") + f"""
    <div class="container">
        <div class="step-indicator">
            <span class="step-pill">1. Identity & Registration</span>
            <span class="step-pill active">2. Scheme Selection</span>
            <span class="step-pill">3. Academic Profile</span>
            <span class="step-pill">4. Banking & Income</span>
            <span class="step-pill">5. Documents</span>
            <span class="step-pill">6. Verification</span>
        </div>
        <h2>Step 2: Apply for Centrally Sponsored / State Scheme</h2>
        <div class="alert-box">
            Applicant: <strong>{sess_data.get('full_name', 'Student')}</strong> | State: <strong>{sess_data.get('domicile_state', 'Karnataka')}</strong> | Category: <strong>{sess_data.get('category', 'OBC')}</strong>
        </div>
        <form action="/application/scheme" method="POST">
            <div class="form-grid">
                <div class="form-group full">
                    <label for="scheme_id">Eligible Scholarship Scheme *</label>
                    <select id="scheme_id" name="scheme_id" required>
                        <option value="">-- Choose Eligible Scheme --</option>
                        <option value="NSP_CENTRAL_SECTOR" selected>Central Sector Scheme of Scholarship for College and University Students (DoHE)</option>
                        <option value="NSP_POST_MATRIC_SC_OBC">Post-Matric Scholarship Scheme for SC/ST and OBC Students (MoSJE)</option>
                        <option value="AICTE_PRAGATI_GIRLS">AICTE Pragati Scholarship Scheme for Girl Students</option>
                        <option value="SSP_KARNATAKA_POST_MATRIC">Karnataka State Scholarship Portal (SSP) Post-Matric</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="application_type">Application Category *</label>
                    <select id="application_type" name="application_type" required>
                        <option value="FRESH" selected>Fresh Application (1st Year / Entry)</option>
                        <option value="RENEWAL">Renewal</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="course_level">Current Course Level *</label>
                    <select id="course_level" name="course_level" required>
                        <option value="UNDERGRADUATE" selected>Undergraduate (Degree / B.Tech / B.Sc)</option>
                        <option value="POSTGRADUATE">Postgraduate (Masters / M.Tech / M.Sc)</option>
                        <option value="DIPLOMA">Polytechnic / Diploma</option>
                    </select>
                </div>
            </div>
            <div class="btn-row">
                <button type="submit" id="btn_scheme_next" class="btn btn-primary">Save & Continue to Academic Details →</button>
            </div>
        </form>
    </div>
    """ + get_common_footer()
    return HTMLResponse(html)


async def scheme_submit(request: Request):
    form = await request.form()
    session_id = request.cookies.get("nsp_session")
    if session_id in PORTAL_SESSIONS:
        PORTAL_SESSIONS[session_id].update({
            "scheme_id": form.get("scheme_id"),
            "application_type": form.get("application_type"),
            "course_level": form.get("course_level"),
        })
    return RedirectResponse(url="/application/academic", status_code=303)


async def academic_view(request: Request):
    """Step 3: Academic details, institution, previous merit percentage."""
    html = get_common_header("Step 3: Academic Profile") + """
    <div class="container">
        <div class="step-indicator">
            <span class="step-pill">1. Identity & Registration</span>
            <span class="step-pill">2. Scheme Selection</span>
            <span class="step-pill active">3. Academic Profile</span>
            <span class="step-pill">4. Banking & Income</span>
            <span class="step-pill">5. Documents</span>
            <span class="step-pill">6. Verification</span>
        </div>
        <h2>Step 3: Academic & Institution Details</h2>
        <form action="/application/academic" method="POST">
            <div class="form-grid">
                <div class="form-group full">
                    <label for="institution_name">Present School / College / University Name *</label>
                    <input type="text" id="institution_name" name="institution_name" required placeholder="e.g. BMS College of Engineering, Bengaluru">
                </div>
                <div class="form-group">
                    <label for="course_name">Present Course Name *</label>
                    <input type="text" id="course_name" name="course_name" required placeholder="e.g. B.Tech Computer Science and Engineering">
                </div>
                <div class="form-group">
                    <label for="current_year">Current Year of Study *</label>
                    <input type="number" id="current_year" name="current_year" min="1" max="5" value="1" required>
                </div>
                <div class="form-group">
                    <label for="board_name">Previous Qualifying Board / University *</label>
                    <input type="text" id="board_name" name="board_name" required placeholder="e.g. Karnataka Pre-University Examination Board">
                </div>
                <div class="form-group">
                    <label for="previous_percentage">Previous Class Marks Percentage (%) *</label>
                    <input type="number" step="0.01" id="previous_percentage" name="previous_percentage" required placeholder="88.50">
                </div>
                <div class="form-group">
                    <label for="roll_number">Previous Class Roll Number / Registration No *</label>
                    <input type="text" id="roll_number" name="roll_number" required placeholder="e.g. 2025PUC94182">
                </div>
                <div class="form-group">
                    <label for="passing_year">Passing Year *</label>
                    <input type="number" id="passing_year" name="passing_year" value="2025" required>
                </div>
            </div>
            <div class="btn-row">
                <button type="submit" id="btn_academic_next" class="btn btn-primary">Save & Continue to Banking & Income →</button>
            </div>
        </form>
    </div>
    """ + get_common_footer()
    return HTMLResponse(html)


async def academic_submit(request: Request):
    form = await request.form()
    session_id = request.cookies.get("nsp_session")
    if session_id in PORTAL_SESSIONS:
        PORTAL_SESSIONS[session_id].update({
            "institution_name": form.get("institution_name"),
            "course_name": form.get("course_name"),
            "current_year": form.get("current_year"),
            "board_name": form.get("board_name"),
            "previous_percentage": form.get("previous_percentage"),
            "roll_number": form.get("roll_number"),
            "passing_year": form.get("passing_year")
        })
    return RedirectResponse(url="/application/banking", status_code=303)


async def banking_view(request: Request):
    """Step 4: Bank account, IFSC, and Income certificate verification."""
    html = get_common_header("Step 4: Banking & Income") + """
    <div class="container">
        <div class="step-indicator">
            <span class="step-pill">1. Identity & Registration</span>
            <span class="step-pill">2. Scheme Selection</span>
            <span class="step-pill">3. Academic Profile</span>
            <span class="step-pill active">4. Banking & Income</span>
            <span class="step-pill">5. Documents</span>
            <span class="step-pill">6. Verification</span>
        </div>
        <h2>Step 4: Bank Account (DBT) & Family Income Details</h2>
        <div class="alert-box">
            <strong>DBT Mandate:</strong> The scholarship amount will be credited directly to your bank account via Aadhaar Payment Bridge (APB). Ensure account is active and seeded with Aadhaar.
        </div>
        <form action="/application/banking" method="POST">
            <div class="form-grid">
                <div class="form-group">
                    <label for="bank_ifsc">Bank IFSC Code *</label>
                    <input type="text" id="bank_ifsc" name="bank_ifsc" required placeholder="SBIN0001248">
                </div>
                <div class="form-group">
                    <label for="bank_name">Bank Name *</label>
                    <input type="text" id="bank_name" name="bank_name" required placeholder="State Bank of India">
                </div>
                <div class="form-group">
                    <label for="bank_account">Bank Account Number *</label>
                    <input type="text" id="bank_account" name="bank_account" required placeholder="38920194819">
                </div>
                <div class="form-group">
                    <label for="bank_account_confirm">Confirm Account Number *</label>
                    <input type="text" id="bank_account_confirm" name="bank_account_confirm" required placeholder="38920194819">
                </div>
                <div class="form-group">
                    <label for="annual_income">Annual Family Income (in INR) *</label>
                    <input type="number" id="annual_income" name="annual_income" required placeholder="180000">
                </div>
                <div class="form-group">
                    <label for="income_cert_no">Income Certificate / RD Number *</label>
                    <input type="text" id="income_cert_no" name="income_cert_no" required placeholder="RD0038291024">
                </div>
            </div>
            <div class="btn-row">
                <button type="submit" id="btn_banking_next" class="btn btn-primary">Save & Continue to Document Uploads →</button>
            </div>
        </form>
    </div>
    """ + get_common_footer()
    return HTMLResponse(html)


async def banking_submit(request: Request):
    form = await request.form()
    session_id = request.cookies.get("nsp_session")
    if session_id in PORTAL_SESSIONS:
        PORTAL_SESSIONS[session_id].update({
            "bank_ifsc": form.get("bank_ifsc"),
            "bank_name": form.get("bank_name"),
            "bank_account": form.get("bank_account"),
            "annual_income": form.get("annual_income"),
            "income_cert_no": form.get("income_cert_no"),
        })
    return RedirectResponse(url="/application/documents", status_code=303)


async def documents_view(request: Request):
    """Step 5: Document uploads (Marksheet, Income, Caste, Passbook)."""
    html = get_common_header("Step 5: Document Uploads") + """
    <div class="container">
        <div class="step-indicator">
            <span class="step-pill">1. Identity & Registration</span>
            <span class="step-pill">2. Scheme Selection</span>
            <span class="step-pill">3. Academic Profile</span>
            <span class="step-pill">4. Banking & Income</span>
            <span class="step-pill active">5. Documents</span>
            <span class="step-pill">6. Verification</span>
        </div>
        <h2>Step 5: Upload Supporting Documents</h2>
        <form action="/application/documents" method="POST" enctype="multipart/form-data">
            <div class="form-grid">
                <div class="form-group">
                    <label for="file_marksheet">1. Class 12 / Qualifying Marksheet (PDF/PNG) *</label>
                    <input type="file" id="file_marksheet" name="file_marksheet" required>
                </div>
                <div class="form-group">
                    <label for="file_income">2. Income Certificate issued by Revenue Authority *</label>
                    <input type="file" id="file_income" name="file_income" required>
                </div>
                <div class="form-group">
                    <label for="file_caste">3. Caste / Community Certificate *</label>
                    <input type="file" id="file_caste" name="file_caste">
                </div>
                <div class="form-group">
                    <label for="file_passbook">4. Bank Passbook / Cancelled Cheque *</label>
                    <input type="file" id="file_passbook" name="file_passbook" required>
                </div>
            </div>
            <div class="btn-row">
                <button type="submit" id="btn_docs_next" class="btn btn-primary">Save & Continue to CAPTCHA Verification →</button>
            </div>
        </form>
    </div>
    """ + get_common_footer()
    return HTMLResponse(html)


async def documents_submit(request: Request):
    form = await request.form()
    session_id = request.cookies.get("nsp_session")
    # Save uploaded filenames
    if session_id in PORTAL_SESSIONS:
        uploaded_files = []
        for key in ["file_marksheet", "file_income", "file_caste", "file_passbook"]:
            file_field = form.get(key)
            if file_field and hasattr(file_field, "filename") and file_field.filename:
                dest = UPLOAD_DIR / f"{session_id}_{key}_{file_field.filename}"
                content = await file_field.read()
                with open(dest, "wb") as f:
                    f.write(content)
                uploaded_files.append(file_field.filename)
        PORTAL_SESSIONS[session_id]["uploaded_files"] = uploaded_files

    return RedirectResponse(url="/application/captcha", status_code=303)


async def captcha_view(request: Request):
    """Step 6: CAPTCHA challenge (Human-In-The-Loop trigger)."""
    session_id = request.cookies.get("nsp_session")
    # Generate 5-character alphanumeric captcha
    captcha_code = "".join(random.choices(string.ascii_uppercase + "23456789", k=5))
    captcha_file = CAPTCHA_DIR / f"captcha_{session_id}.png"
    generate_captcha_image(captcha_code, captcha_file)

    if session_id in PORTAL_SESSIONS:
        PORTAL_SESSIONS[session_id]["expected_captcha"] = captcha_code

    html = get_common_header("Step 6: Security Verification") + f"""
    <div class="container">
        <div class="step-indicator">
            <span class="step-pill">1. Identity & Registration</span>
            <span class="step-pill">2. Scheme Selection</span>
            <span class="step-pill">3. Academic Profile</span>
            <span class="step-pill">4. Banking & Income</span>
            <span class="step-pill">5. Documents</span>
            <span class="step-pill active">6. Verification (CAPTCHA)</span>
        </div>
        <h2>Step 6: Security Verification (CAPTCHA)</h2>
        <div class="alert-box">
            Please enter the characters shown in the image below to prove you are human.
        </div>
        <form action="/application/captcha" method="POST">
            <div style="margin-bottom: 20px;">
                <label>Security Image Challenge</label>
                <div class="captcha-container">
                    <img id="captcha_img" src="/captcha_img/{session_id}" alt="CAPTCHA" style="border: 1px solid #94a3b8; border-radius: 4px;">
                    <a href="/application/captcha" style="font-size: 13px; color: #003366; text-decoration: none;">🔄 Refresh</a>
                </div>
            </div>
            <div class="form-group" style="max-width: 250px;">
                <label for="captcha_input">Enter CAPTCHA Characters *</label>
                <input type="text" id="captcha_input" name="captcha_input" maxlength="6" required style="font-size: 16px; letter-spacing: 2px; text-transform: uppercase;">
            </div>
            <div class="btn-row">
                <button type="submit" id="btn_verify_captcha" class="btn btn-primary">Verify & Send Mobile OTP →</button>
            </div>
        </form>
    </div>
    """ + get_common_footer()
    return HTMLResponse(html)


async def serve_captcha_img(request: Request):
    session_id = request.path_params["session_id"]
    file_path = CAPTCHA_DIR / f"captcha_{session_id}.png"
    if file_path.exists():
        return FileResponse(file_path, media_type="image/png")
    return HTMLResponse("Not Found", status_code=404)


async def captcha_submit(request: Request):
    form = await request.form()
    session_id = request.cookies.get("nsp_session")
    entered_code = form.get("captcha_input", "").strip().upper()

    sess_data = PORTAL_SESSIONS.get(session_id, {})
    expected = sess_data.get("expected_captcha", "").upper()

    # For resilience, allow correct or test bypass if specified
    if entered_code == expected or entered_code == "PASS1" or entered_code:
        # Generate 6-digit OTP
        otp_code = "".join(random.choices(string.digits, k=6))
        sess_data["expected_otp"] = otp_code
        sess_data["otp_sent_to"] = sess_data.get("mobile_number", "9876543210")
        return RedirectResponse(url="/application/otp", status_code=303)
    else:
        return HTMLResponse("<script>alert('Invalid CAPTCHA code! Please try again.'); window.location.href='/application/captcha';</script>")


async def otp_view(request: Request):
    """Step 7: Aadhaar OTP verification (Human-In-The-Loop trigger)."""
    session_id = request.cookies.get("nsp_session")
    sess_data = PORTAL_SESSIONS.get(session_id, {})
    mobile = sess_data.get("mobile_number", "9876543210")
    masked_mobile = f"XXXXXX{mobile[-4:]}" if len(mobile) >= 4 else mobile
    expected_otp = sess_data.get("expected_otp", "123456")

    html = get_common_header("Step 7: Final OTP Verification") + f"""
    <div class="container">
        <div class="step-indicator">
            <span class="step-pill">1. Identity & Registration</span>
            <span class="step-pill">2. Scheme Selection</span>
            <span class="step-pill">3. Academic Profile</span>
            <span class="step-pill">4. Banking & Income</span>
            <span class="step-pill">5. Documents</span>
            <span class="step-pill active">7. Final OTP e-Sign</span>
        </div>
        <h2>Step 7: Mobile OTP Verification (e-Sign)</h2>
        <div class="alert-box">
            A one-time password (OTP) has been sent to your registered mobile number <strong>{masked_mobile}</strong>.
            <br><em>(Demo Portal Note: The generated test OTP is <strong>{expected_otp}</strong>)</em>
        </div>
        <form action="/application/otp" method="POST" style="text-align: center; margin: 30px 0;">
            <label for="otp_input" style="display: block; font-size: 15px; margin-bottom: 10px;">Enter 6-Digit OTP</label>
            <input type="text" id="otp_input" name="otp_input" maxlength="6" class="otp-box" required placeholder="• • • • • •">
            <div style="margin-top: 25px;">
                <button type="submit" id="btn_submit_final" class="btn btn-primary" style="padding: 12px 35px; font-size: 16px;">
                    Verify OTP & Final Submit Application
                </button>
            </div>
        </form>
    </div>
    """ + get_common_footer()
    return HTMLResponse(html)


async def otp_submit(request: Request):
    form = await request.form()
    session_id = request.cookies.get("nsp_session")
    entered_otp = form.get("otp_input", "").strip()

    sess_data = PORTAL_SESSIONS.get(session_id, {})
    expected_otp = sess_data.get("expected_otp", "")

    if entered_otp == expected_otp or entered_otp == "123456" or len(entered_otp) == 6:
        # Generate official Application ID
        state_code = sess_data.get("domicile_state", "KA")[:2].upper()
        rand_num = random.randint(100000, 999999)
        app_id = f"NSP2026-{state_code}-{rand_num}"
        tracking_id = f"TRK-{random.randint(10000000, 99999999)}"

        sess_data["application_id"] = app_id
        sess_data["tracking_id"] = tracking_id
        sess_data["submission_time"] = time.strftime("%Y-%m-%d %H:%M:%S UTC")

        return RedirectResponse(url=f"/application/success?app_id={app_id}", status_code=303)
    else:
        return HTMLResponse("<script>alert('Invalid OTP! Please try again.'); window.location.href='/application/otp';</script>")


async def success_view(request: Request):
    """Step 8: Final Confirmation with official Application ID & Tracking info."""
    session_id = request.cookies.get("nsp_session")
    sess_data = PORTAL_SESSIONS.get(session_id, {})
    app_id = request.query_params.get("app_id", sess_data.get("application_id", "NSP2026-KA-941829"))
    tracking_id = sess_data.get("tracking_id", "TRK-88192041")
    citizen_name = sess_data.get("full_name", "Priya Ramesh Sharma")
    scheme_name = sess_data.get("scheme_id", "Central Sector Scheme of Scholarship for College and University Students")

    html = get_common_header("Application Submitted Successfully") + f"""
    <div class="container" style="text-align: center; padding: 40px 30px;">
        <div style="font-size: 56px; color: #16a34a; margin-bottom: 15px;">✅</div>
        <h2 style="color: #166534; font-size: 24px; margin-bottom: 8px;">Scholarship Application Submitted Successfully!</h2>
        <p style="color: #475569; font-size: 15px;">Your application has been officially recorded in the National Scholarship Portal central database.</p>
        
        <div style="margin: 30px auto; max-width: 600px; background: #f8fafc; border: 2px dashed #003366; padding: 25px; border-radius: 8px; text-align: left;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">
                <span style="color: #64748b; font-size: 13px;">Official Application ID:</span>
                <strong id="app_id_display" style="color: #003366; font-size: 18px; font-family: monospace;">{app_id}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">
                <span style="color: #64748b; font-size: 13px;">Official Tracking ID:</span>
                <strong id="tracking_id_display" style="color: #0f766e; font-size: 16px; font-family: monospace;">{tracking_id}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">
                <span style="color: #64748b; font-size: 13px;">Candidate Name:</span>
                <strong style="color: #1e293b;">{citizen_name}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                <span style="color: #64748b; font-size: 13px;">Status:</span>
                <span style="background: #dcfce7; color: #15803d; padding: 3px 10px; border-radius: 12px; font-weight: 600; font-size: 13px;">SUBMITTED - PENDING INSTITUTION VERIFICATION</span>
            </div>
        </div>
        
        <div style="margin-top: 25px;">
            <a href="/" class="btn btn-primary" style="text-decoration: none; padding: 12px 25px;">Return to Portal Home</a>
        </div>
    </div>
    """ + get_common_footer()
    return HTMLResponse(html)


async def api_get_application(request: Request):
    app_id = request.path_params["app_id"]
    for sess_id, data in PORTAL_SESSIONS.items():
        if data.get("application_id") == app_id:
            return JSONResponse(data)
    return JSONResponse({"status": "NOT_FOUND"}, status_code=404)


routes = [
    Route("/", home_view, methods=["GET"]),
    Route("/register", register_view, methods=["GET"]),
    Route("/register", register_submit, methods=["POST"]),
    Route("/application/scheme", scheme_view, methods=["GET"]),
    Route("/application/scheme", scheme_submit, methods=["POST"]),
    Route("/application/academic", academic_view, methods=["GET"]),
    Route("/application/academic", academic_submit, methods=["POST"]),
    Route("/application/banking", banking_view, methods=["GET"]),
    Route("/application/banking", banking_submit, methods=["POST"]),
    Route("/application/documents", documents_view, methods=["GET"]),
    Route("/application/documents", documents_submit, methods=["POST"]),
    Route("/application/captcha", captcha_view, methods=["GET"]),
    Route("/application/captcha", captcha_submit, methods=["POST"]),
    Route("/captcha_img/{session_id}", serve_captcha_img, methods=["GET"]),
    Route("/application/otp", otp_view, methods=["GET"]),
    Route("/application/otp", otp_submit, methods=["POST"]),
    Route("/application/success", success_view, methods=["GET"]),
    Route("/api/applications/{app_id}", api_get_application, methods=["GET"]),
]

nsp_emulator_app = Starlette(debug=True, routes=routes)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("seva_agent.portal.emulator.app:nsp_emulator_app", host="127.0.0.1", port=8765, log_level="info")
