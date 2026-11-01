"""
Tests for SevaAgent Tamper-Evident Cryptographic Audit System
Validates hash chaining, block consistency, and tamper detection.
"""

import unittest
from seva_agent.core.audit import TamperEvidentAuditLedger
from seva_agent.core.models import AgentActionType


class TestAuditIntegrity(unittest.TestCase):
    def setUp(self):
        self.ledger = TamperEvidentAuditLedger("test_session_audit_001")

    def test_genesis_block(self):
        self.assertEqual(len(self.ledger.chain), 1)
        genesis = self.ledger.chain[0]
        self.assertEqual(genesis.block_index, 0)
        self.assertEqual(genesis.previous_block_hash, TamperEvidentAuditLedger.GENESIS_HASH)

    def test_chain_extension_and_verification(self):
        self.ledger.log_action(
            agent_name="TestAgent",
            action_type=AgentActionType.NAVIGATE,
            rationale="Navigate to login page",
            result="Success"
        )
        self.ledger.log_action(
            agent_name="TestAgent",
            action_type=AgentActionType.FILL_FIELD,
            rationale="Fill citizen name",
            result="Success",
            target_selector="#full_name",
            value_masked="Priya Sharma"
        )
        self.assertEqual(len(self.ledger.chain), 3)

        # Verify chain integrity
        valid, msg = self.ledger.verify_chain_integrity()
        self.assertTrue(valid, msg)

    def test_tamper_detection(self):
        self.ledger.log_action(
            agent_name="TestAgent",
            action_type=AgentActionType.CLICK,
            rationale="Click submit",
            result="Success"
        )
        # Attempt to tamper with historical block
        self.ledger.chain[1].action_record.rationale = "TAMPERED RATIONALE"
        valid, msg = self.ledger.verify_chain_integrity()
        self.assertFalse(valid)
        self.assertIn("tampered", msg.lower())


if __name__ == "__main__":
    unittest.main()
