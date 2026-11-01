"""
SevaAgent Tamper-Evident Cryptographic Audit System
Implements append-only SHA-256 block chain ledger with screenshot hashing,
sensitive data masking, and mathematical tamper verification.
"""

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

from seva_agent.core.models import AgentActionRecord, AuditBlock, AgentActionDecision, ActionType
from seva_agent.core.config import AUDIT_LOG_DIR, SCREENSHOTS_DIR


class TamperEvidentAuditLedger:
    """
    Maintains a cryptographically chained SHA-256 audit trail.
    Detects bit flips, altered action fields, reordered blocks, deleted blocks,
    and post-hoc screenshot modifications.
    """

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.chain: List[AuditBlock] = []
        self.log_file = AUDIT_LOG_DIR / f"audit_ledger_{session_id}.json"
        self._init_genesis_block()

    def _init_genesis_block(self):
        """Creates the initial genesis block anchoring the session."""
        if not self.chain:
            timestamp = datetime.now(timezone.utc).isoformat()
            genesis_decision = AgentActionDecision(
                action_type=ActionType.OBSERVE,
                target_description="System Genesis Anchor",
                locator_strategy="text",
                locator_value="SYSTEM",
                rationale="SevaAgent Cryptographic Session Initialized",
                confidence=1.0,
                validation_status="APPROVED"
            )
            genesis_record = AgentActionRecord(
                action_id=f"act-0-{int(time.time()*1000)}",
                timestamp_utc=timestamp,
                agent_name="SystemSecurity",
                decision=genesis_decision,
                execution_result="Session initialized with SHA-256 genesis anchor",
                page_url="system://genesis",
                page_title="SevaAgent Genesis",
                status="SUCCESS"
            )
            raw_content = f"0|{self.session_id}|{timestamp}|GENESIS|{self.GENESIS_HASH}"
            block_hash = hashlib.sha256(raw_content.encode("utf-8")).hexdigest()

            genesis_block = AuditBlock(
                block_index=0,
                session_id=self.session_id,
                timestamp_utc=timestamp,
                agent_name="SystemSecurity",
                page_url="system://genesis",
                page_state_summary="Genesis initialized",
                action_record=genesis_record,
                screenshot_hash=None,
                previous_block_hash=self.GENESIS_HASH,
                block_hash=block_hash
            )
            self.chain.append(genesis_block)
            self._persist()

    def _compute_file_sha256(self, file_path: Optional[str]) -> Optional[str]:
        """Calculates SHA-256 checksum of an image or screenshot artifact."""
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
        decision: AgentActionDecision,
        execution_result: str,
        page_url: str,
        page_title: str,
        screenshot_path: Optional[str] = None,
        page_state_summary: str = "",
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
            timestamp_utc=timestamp,
            agent_name=agent_name,
            decision=decision,
            execution_result=execution_result,
            page_url=page_url,
            page_title=page_title,
            screenshot_path=screenshot_path,
            screenshot_hash=screenshot_hash,
            execution_time_ms=execution_time_ms,
            status=status
        )

        prev_hash = self.chain[-1].block_hash
        block_idx = len(self.chain)

        # Hash payload string linking all critical components
        block_payload = (
            f"{block_idx}|{self.session_id}|{timestamp}|{agent_name}|{page_url}|"
            f"{decision.action_type.value}|{decision.locator_value}|{decision.masked_value or decision.input_value or ''}|"
            f"{decision.rationale}|{execution_result}|{screenshot_hash or 'NO_IMG'}|{prev_hash}"
        )
        block_hash = hashlib.sha256(block_payload.encode("utf-8")).hexdigest()

        block = AuditBlock(
            block_index=block_idx,
            session_id=self.session_id,
            timestamp_utc=timestamp,
            agent_name=agent_name,
            page_url=page_url,
            page_state_summary=page_state_summary or f"State on {page_url}",
            action_record=action_record,
            screenshot_hash=screenshot_hash,
            previous_block_hash=prev_hash,
            block_hash=block_hash
        )

        self.chain.append(block)
        self._persist()
        return block

    def verify_chain_integrity(self) -> Tuple[bool, str, Optional[int]]:
        """
        Walks the entire cryptographic chain to detect:
        1. Bit flips in action data or payload
        2. Deleted blocks (index mismatch or broken prev_hash)
        3. Reordered blocks
        4. Tampered screenshot files
        Returns: (is_valid, status_message, compromised_block_index)
        """
        if not self.chain:
            return False, "Audit chain is empty", 0

        # Check genesis
        if self.chain[0].previous_block_hash != self.GENESIS_HASH:
            return False, "Genesis block previous hash corrupted", 0

        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            # 1. Check strict sequential index
            if curr.block_index != i:
                return False, f"Block index discontinuity at position {i}: found index {curr.block_index}", i

            # 2. Check parent cryptographic linkage
            if curr.previous_block_hash != prev.block_hash:
                return False, f"Broken chain link at block #{i}: prev_hash does not match block #{i-1} block_hash", i

            # 3. Check screenshot file integrity if file exists on disk
            if curr.action_record.screenshot_path and os.path.exists(curr.action_record.screenshot_path):
                recomputed_ss_hash = self._compute_file_sha256(curr.action_record.screenshot_path)
                if recomputed_ss_hash != curr.screenshot_hash:
                    return False, f"Screenshot file for block #{i} was altered post-execution", i

            # 4. Recompute block digest from ground-truth action payload
            expected_payload = (
                f"{curr.block_index}|{curr.session_id}|{curr.timestamp_utc}|{curr.agent_name}|{curr.page_url}|"
                f"{curr.action_record.decision.action_type.value}|{curr.action_record.decision.locator_value}|"
                f"{curr.action_record.decision.masked_value or curr.action_record.decision.input_value or ''}|"
                f"{curr.action_record.decision.rationale}|{curr.action_record.execution_result}|"
                f"{curr.screenshot_hash or 'NO_IMG'}|{curr.previous_block_hash}"
            )
            recalculated_hash = hashlib.sha256(expected_payload.encode("utf-8")).hexdigest()

            if recalculated_hash != curr.block_hash:
                return False, f"Block data payload tampered at block #{i}: digest mismatch", i

        return True, f"Cryptographic integrity verified ({len(self.chain)} blocks intact)", None

    def _persist(self):
        """Saves audit ledger to JSON file."""
        serialized = [block.model_dump() for block in self.chain]
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2)

    def export_summary(self) -> Dict[str, Any]:
        """Provides structured summary of audit trail."""
        valid, msg, bad_idx = self.verify_chain_integrity()
        return {
            "session_id": self.session_id,
            "total_actions": len(self.chain) - 1,
            "cryptographic_integrity": valid,
            "verification_status": msg,
            "compromised_block_index": bad_idx,
            "latest_block_hash": self.chain[-1].block_hash if self.chain else None,
            "blocks": [b.model_dump() for b in self.chain]
        }
