"""
SevaAgent Vercel Serverless Entrypoint
Exposes FastAPI REST endpoints for SevaAgent civic scholarship intelligence.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from seva_agent.agents.discovery import ScholarshipDiscoveryAgent
from seva_agent.core.models import CitizenProfile, Gender, Category, CourseLevel

app = FastAPI(
    title="🏛️ SevaAgent Civic Scholarship API",
    description="Autonomous Civic AI Agent for Statutory Scholarship Discovery and Portal Execution",
    version="2.0.0"
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    return JSONResponse(
        status_code=500,
        content={
            "status": "ERROR",
            "error_type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc()
        }
    )

discovery_agent = ScholarshipDiscoveryAgent()


@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SevaAgent — Autonomous Civic AI Platform</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background: linear-gradient(135deg, #07101e 0%, #0c1c38 100%);
                color: #ffffff;
                margin: 0;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 90vh;
            }
            .card {
                max-width: 820px;
                background: #112240;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.5);
            }
            .badge {
                background: #0056b3;
                color: #ffffff;
                padding: 5px 14px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                display: inline-block;
            }
            h1 {
                font-size: 32px;
                margin: 16px 0 12px;
                color: #38bdf8;
            }
            p {
                color: #cbd5e1;
                line-height: 1.6;
                font-size: 16px;
            }
            .grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
                margin: 24px 0;
            }
            .box {
                background: #1e3a5f;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #38bdf8;
            }
            .box h3 { margin: 0 0 8px; font-size: 18px; color: #f8fafc; }
            .box p { margin: 0; font-size: 14px; color: #94a3b8; }
            a { color: #38bdf8; text-decoration: none; font-weight: 600; }
            a:hover { text-decoration: underline; }
            .btn {
                display: inline-block;
                background: #0284c7;
                color: #ffffff;
                padding: 12px 28px;
                border-radius: 8px;
                font-weight: 700;
                text-decoration: none;
                margin-top: 10px;
                margin-right: 12px;
                transition: background 0.2s ease;
            }
            .btn:hover { background: #0369a1; text-decoration: none; }
            .btn-alt {
                background: #1e293b;
                border: 1px solid #475569;
            }
            .btn-alt:hover { background: #334155; }
        </style>
    </head>
    <body>
        <div class="card">
            <span class="badge">Official Civic Tech Engine</span>
            <h1>🏛️ SevaAgent Platform Gateway</h1>
            <p>SevaAgent is an autonomous civic intelligence agent built for the Forge Hackathon. It performs real-time statutory scholarship discovery, cross-document verification, and autonomous browser navigation on government portals.</p>
            
            <div class="grid">
                <div class="box">
                    <h3>📚 Interactive API Docs</h3>
                    <p>Test the Statutory Scheme Discovery engine and evaluation endpoints live with OpenAPI Swagger UI.</p>
                    <p style="margin-top: 10px;"><a href="/docs">Open Swagger Docs →</a></p>
                </div>
                <div class="box">
                    <h3>🎯 Scholarship Catalog</h3>
                    <p>Explore official Central and State statutory schemes with eligibility criteria and Gazette citations.</p>
                    <p style="margin-top: 10px;"><a href="/api/schemes">View Schemes API →</a></p>
                </div>
            </div>

            <div style="background: rgba(14, 165, 233, 0.1); border-left: 4px solid #0ea5e9; padding: 16px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0; font-size: 14px; color: #e0f2fe;">
                    <b>💻 Full Streamlit Visual Dashboard Note:</b><br>
                    SevaAgent's complete 5-tab user interface (with Playwright live portal automation and DBT tracker) runs on Streamlit.
                    You can launch it locally with <code>python run_web.py</code> or on <a href="https://share.streamlit.io" target="_blank" style="color: #7dd3fc;">Streamlit Community Cloud</a>.
                </p>
            </div>

            <div>
                <a class="btn" href="/docs">Launch Interactive API Explorer</a>
                <a class="btn btn-alt" href="/api/health">Check System Health</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/api/health")
def health():
    return {
        "status": "HEALTHY",
        "service": "SevaAgent Civic API",
        "version": "2.0.0",
        "architecture": "Multi-Agent StateGraph with Cryptographic Audit Ledger",
        "compliance": "Zero Dummy Data Compliant"
    }


@app.get("/api/schemes")
def list_schemes():
    schemes = [
        {
            "scheme_id": s.scheme_id,
            "scheme_name": s.scheme_name,
            "ministry": s.ministry_or_dept,
            "portal": s.portal_type,
            "max_income_inr": s.max_family_income,
            "min_percentage": s.min_previous_percentage,
            "annual_award_inr": s.award_amount_annual,
            "citation": s.official_guideline_citation,
            "deadline": s.application_deadline
        }
        for s in discovery_agent.scheme_catalog
    ]
    return {
        "total": len(schemes),
        "source": "Official Gazette & Ministry Guidelines (Central + State)",
        "schemes": schemes
    }


class QuickAssessmentRequest(BaseModel):
    category: str = "OBC"
    state: str = "Karnataka"
    annual_family_income: float = 180000.0
    previous_class_percentage: float = 85.0
    course_level: str = "UNDERGRADUATE"


@app.post("/api/assess")
def assess_eligibility(req: QuickAssessmentRequest):
    try:
        cat = Category(req.category.upper())
    except Exception:
        cat = Category.GENERAL

    try:
        cl = CourseLevel(req.course_level.upper())
    except Exception:
        cl = CourseLevel.UNDERGRADUATE

    temp_profile = CitizenProfile(
        full_name="Assessment Applicant",
        state=req.state,
        category=cat,
        annual_family_income=req.annual_family_income,
        previous_class_percentage=req.previous_class_percentage,
        course_level=cl
    )

    assessments = discovery_agent.evaluate_profile(temp_profile)
    return {
        "applicant_profile": {
            "state": req.state,
            "category": cat.value,
            "income": req.annual_family_income,
            "percentage": req.previous_class_percentage
        },
        "results": [
            {
                "scheme_id": a.scheme.scheme_id,
                "scheme_name": a.scheme.scheme_name,
                "is_eligible": a.is_eligible,
                "eligibility_score": a.eligibility_score,
                "actionable_summary": a.actionable_summary,
                "missing_documents": [d.value for d in a.missing_documents],
                "rule_evaluations": [
                    {"rule": r.rule_name, "passed": r.passed, "explanation": r.explanation, "citation": r.citation}
                    for r in a.rule_evaluations
                ]
            }
            for a in assessments
        ]
    }
