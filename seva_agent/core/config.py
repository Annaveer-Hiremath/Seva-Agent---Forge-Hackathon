"""
SevaAgent Configuration Module
Handles project paths, runtime configuration, timeouts, and storage setup.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "sample_data"
DOCS_DIR = DATA_DIR / "documents"
SCREENSHOTS_DIR = BASE_DIR / "storage" / "screenshots"
AUDIT_LOG_DIR = BASE_DIR / "storage" / "audit_logs"
DB_PATH = BASE_DIR / "storage" / "seva_agent.db"

# Create directories if they do not exist
try:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
except (OSError, PermissionError):
    import tempfile
    TMP_DIR = Path(tempfile.gettempdir()) / "seva_agent"
    SCREENSHOTS_DIR = TMP_DIR / "screenshots"
    AUDIT_LOG_DIR = TMP_DIR / "audit_logs"
    DOCS_DIR = TMP_DIR / "documents"
    DB_PATH = TMP_DIR / "seva_agent.db"
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Portal & Automation Configuration
EMULATOR_HOST = "127.0.0.1"
EMULATOR_PORT = 8765
EMULATOR_BASE_URL = f"http://{EMULATOR_HOST}:{EMULATOR_PORT}"

# Real Official Portals Supported
LIVE_PORTALS = {
    "NSP": {
        "name": "National Scholarship Portal (Govt. of India)",
        "url": "https://scholarships.gov.in",
        "reg_url": "https://scholarships.gov.in/fresh/newstdRegfrmInstruction",
    },
    "SSP_KA": {
        "name": "State Scholarship Portal (Karnataka)",
        "url": "https://ssp.postmatric.karnataka.gov.in",
    },
    "MAHADBT": {
        "name": "MahaDBT Scholarship Portal (Maharashtra)",
        "url": "https://mahadbt.maharashtra.gov.in",
    }
}

# Browser Settings
DEFAULT_HEADLESS = True
BROWSER_TIMEOUT_MS = 15000
ACTION_DELAY_MS = 300  # realistic human typing delay
MAX_REPLAN_ATTEMPTS = 3

# LLM Fallback & Extraction Settings
DEFAULT_MODEL = os.getenv("SEVA_MODEL", "gemini-1.5-flash")
