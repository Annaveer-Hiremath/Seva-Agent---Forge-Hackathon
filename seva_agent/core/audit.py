"""
SevaAgent Tamper-Evident Cryptographic Audit System
Implements a cryptographically chained SHA-256 audit ledger with screenshot hashing,
tamper detection, verification, and human-readable export.
"""

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

from seva_agent.core.models import AgentActionRecord, AuditBlock, AgentActionType
from seva_agent.core.config import AUDIT_LOG_DIR, SCREENSHOTS_DIR


class TamperEvidentAuditLedger:
    """
    Maintains an immutable, append-only SHA-256 chained audit trail for SevaAgent.
    Each action taken by any agent (navigation, typing, clicking, uploading, HITL verification)
    is recorded in a cryptographic block linked to the previous block's hash.
    """

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.chain: List[AuditBlock] = []
        self.log_file = AUDIT_LOG_DIR / f"audit_ledger_{session_id}.json"
        self._init_genesis_block()

    def _init_genesis_block(self):
        """Creates the initial genesis block if the chain is empty."""
        if not self.chain:
            timestamp = datetime.now(timezone.utc).isoformat()
            genesis_action = AgentActionRecord(
                action_id="genesis-0",
                timestamp=timestamp,
                agent_name="SystemSecurity",
                action_type=AgentActionType.OBSERVE,
                rationale="SevaAgent Tamper-Evident Session Initialized",
                result="Session started securely",
                status="SUCCESS"
            )
            raw_content = f"0|{timestamp}|GENESIS|{self.GENESIS_HASH}"
            block_hash = hashlib.sha256(raw_content.encode("utf-8")).hexdigest()

            genesis_block = AuditBlock(
                block_index=0,
                timestamp_utc=timestamp,
                action_record=genesis_action,
                state_snapshot_summary="Session genesis initialized with cryptographic anchor",
                screenshot_hash=None,
                previous_block_hash=self.GENESIS_HASH,
                block_hash=block_hash
            )
            self.chain.append(genesis_block)
            self._persist()

    def _compute_file_sha256(self, file_path: Optional[str]) -> Optional[str]:
        """Calculates the SHA-256 checksum of an image or screenshot artifact."""
        if not file_path or not os.path.exists(file_path):
            return None
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha.update(chunk)
        return sha.hexdigest()

    def log_action(
        self,
        agent_name: str,
        action_type: AgentActionType,
        rationale: str,
        result: str,
        target_selector: Optional[str] = None,
        value_masked: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        state_summary: str = "",
        status: str = "SUCCESS",
        execution_time_ms: float = 0.0
    ) -> AuditBlock:
        """
        Creates and appends a new cryptographically chained audit block.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        action_id = f"act-{len(self.chain)}-{int(time.time() * 1000)}"

        screenshot_hash = self._compute_file_sha256(screenshot_path)

        action_record = AgentActionRecord(
            action_id=action_id,
            timestamp=timestamp,
            agent_name=agent_name,
            action_type=action_type,
            target_selector=target_selector,
            value_masked=value_masked,
            rationale=rationale,
            result=result,
            screenshot_path=screenshot_path,
            execution_time_ms=execution_time_ms,
            status=status
        )

        prev_hash = self.chain[-1].block_hash
        block_idx = len(self.chain)

        # Hash payload string linking all critical components
        block_payload = (
            f"{block_idx}|{timestamp}|{agent_name}|{action_type.value}|"
            f"{target_selector or ''}|{value_masked or ''}|{rationale}|"
            f"{result}|{screenshot_hash or 'NO_IMG'}|{prev_hash}"
        )
        block_hash = hashlib.sha256(block_payload.encode("utf-8")).hexdigest()

        block = AuditBlock(
            block_index=block_idx,
            timestamp_utc=timestamp,
            action_record=action_record,
            state_snapshot_summary=state_summary,
            screenshot_hash=screenshot_hash,
            previous_block_hash=prev_hash,
            block_hash=block_hash
        )

        self.chain.append(block)
        self._persist()
        return block

    def verify_chain_integrity(self) -> Tuple[bool, Optional[str]]:
        """
        Iterates through the entire cryptographic chain to detect any tampering,
        bit-flips, modified action attributes, or broken hash linkages.
        """
        if not self.chain:
            return False, "Audit chain is empty"

        # Check genesis
        if self.chain[0].previous_block_hash != self.GENESIS_HASH:
            return False, "Genesis block previous hash is corrupted"

        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            # 1. Check parent link
            if curr.previous_block_hash != prev.block_hash:
                return False, f"Broken chain link at block {i}: prev_hash does not match parent block {i-1}"

            # 2. Recalculate and verify screenshot hash if screenshot file exists
            if curr.action_record.screenshot_path and os.path.exists(curr.action_record.screenshot_path):
                expected_ss_hash = self._compute_file_sha256(curr.action_record.screenshot_path)
                if expected_ss_hash != curr.screenshot_hash:
                    return False, f"Screenshot file for block {i} was tampered with or modified post-execution"

            # 3. Recalculate and verify block hash
            expected_payload = (
                f"{curr.block_index}|{curr.timestamp_utc}|{curr.action_record.agent_name}|"
                f"{curr.action_record.action_type.value}|"
                f"{curr.action_record.target_selector or ''}|{curr.action_record.value_masked or ''}|"
                f"{curr.action_record.rationale}|{curr.action_record.result}|"
                f"{curr.screenshot_hash or 'NO_IMG'}|{curr.previous_block_hash}"
            )
            recalculated_hash = hashlib.sha256(expected_payload.encode("utf-8")).hexdigest()

            if recalculated_hash != curr.block_hash:
                return False, f"Block data tampered at block index {i}: hash mismatch"

        return True, f"Audit chain verified successfully ({len(self.chain)} blocks intact)"

    def _persist(self):
        """Saves audit ledger to JSON file."""
        serialized = [block.model_dump() for block in self.chain]
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2)

    def export_summary(self) -> Dict[str, Any]:
        """Provides a structured summary of the audit trail."""
        valid, msg = self.verify_chain_integrity()
        return {
            "session_id": self.session_id,
            "total_actions": len(self.chain) - 1,  # minus genesis
            "cryptographic_integrity": valid,
            "verification_status": msg,
            "latest_block_hash": self.chain[-1].block_hash if self.chain else None,
            "blocks": [b.model_dump() for b in self.chain]
        }
