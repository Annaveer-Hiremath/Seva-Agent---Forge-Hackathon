"""
SevaAgent SQLite Persistence Layer
Stores citizen applications, profiles, scheme metadata, and audit records.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from seva_agent.core.config import DB_PATH


class SevaDatabase:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Applications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    application_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    citizen_name TEXT NOT NULL,
                    aadhaar_masked TEXT NOT NULL,
                    scheme_id TEXT NOT NULL,
                    scheme_name TEXT NOT NULL,
                    portal_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    tracking_id TEXT,
                    audit_root_hash TEXT,
                    submission_date TEXT NOT NULL,
                    details_json TEXT NOT NULL
                )
            """)

            # Saved profiles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    profile_id TEXT PRIMARY KEY,
                    citizen_name TEXT NOT NULL,
                    mobile_number TEXT NOT NULL,
                    category TEXT NOT NULL,
                    state TEXT NOT NULL,
                    profile_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Audit checkpoint summary
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_checkpoints (
                    session_id TEXT PRIMARY KEY,
                    total_blocks INTEGER NOT NULL,
                    latest_hash TEXT NOT NULL,
                    verified INTEGER NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_application(
        self,
        application_id: str,
        session_id: str,
        citizen_name: str,
        aadhaar_masked: str,
        scheme_id: str,
        scheme_name: str,
        portal_type: str,
        status: str,
        tracking_id: Optional[str],
        audit_root_hash: str,
        submission_date: str,
        details: Dict[str, Any]
    ):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO applications (
                    application_id, session_id, citizen_name, aadhaar_masked,
                    scheme_id, scheme_name, portal_type, status, tracking_id,
                    audit_root_hash, submission_date, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                application_id, session_id, citizen_name, aadhaar_masked,
                scheme_id, scheme_name, portal_type, status, tracking_id or application_id,
                audit_root_hash, submission_date, json.dumps(details)
            ))
            conn.commit()

    def get_application(self, application_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM applications WHERE application_id = ?", (application_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d["details"] = json.loads(d["details_json"])
                return d
        return None

    def list_applications(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM applications ORDER BY submission_date DESC")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def save_profile(self, profile_id: str, citizen_name: str, mobile: str, category: str, state: str, profile_dict: dict):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO profiles (profile_id, citizen_name, mobile_number, category, state, profile_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (profile_id, citizen_name, mobile, category, state, json.dumps(profile_dict)))
            conn.commit()

    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles WHERE profile_id = ?", (profile_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row["profile_json"])
        return None
