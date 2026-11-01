"""
Tests for SevaAgent Tamper-Evident Cryptographic Audit System
Validates hash chaining, block consistency, deletion detection, reorder detection, and content tamper detection.
"""

import unittest
from seva_agent.core.audit import TamperEvidentAuditLedger
from seva_agent.core.models import AgentActionDecision, ActionType, LocatorStrategy


class TestAuditIntegrity(unittest.TestCase):
    def setUp(self):
        self.ledger = TamperEvidentAuditLedger("test_session_audit_v2_001")

    def test_genesis_block(self):
        self.assertEqual(len(self.ledger.chain), 1)
        genesis = self.ledger.chain[0]
        self.assertEqual(genesis.block_index, 0)
        self.assertEqual(genesis.previous_block_hash, TamperEvidentAuditLedger.GENESIS_HASH)

    def test_chain_extension_and_verification(self):
        d1 = AgentActionDecision(
            action_type=ActionType.NAVIGATE,
            target_description="Portal Homepage",
            locator_strategy=LocatorStrategy.TEXT,
            locator_value="URL",
            rationale="Navigate to entry page",
            confidence=1.0
        )
        self.ledger.log_action(
            agent_name="BrowserAutomationAgent",
            decision=d1,
            execution_result="Success",
            page_url="https://scholarships.gov.in",
            page_title="NSP Portal"
        )

        d2 = AgentActionDecision(
            action_type=ActionType.FILL_FIELD,
            target_description="Applicant Name",
            locator_strategy=LocatorStrategy.LABEL,
            locator_value="Full Name",
            input_value="Priya Sharma",
            rationale="Populate verified applicant name",
            confidence=0.98
        )
        self.ledger.log_action(
            agent_name="BrowserAutomationAgent",
            decision=d2,
            execution_result="Field populated",
            page_url="https://scholarships.gov.in/register",
            page_title="NSP Registration"
        )
        self.assertEqual(len(self.ledger.chain), 3)

        # Verify chain integrity
        valid, msg, bad_idx = self.ledger.verify_chain_integrity()
        self.assertTrue(valid, msg)
        self.assertIsNone(bad_idx)

    def test_content_tamper_detection(self):
        d = AgentActionDecision(
            action_type=ActionType.CLICK_ELEMENT,
            target_description="Submit Button",
            locator_strategy=LocatorStrategy.ROLE,
            locator_value="Submit",
            rationale="Click submit",
            confidence=0.95
        )
        self.ledger.log_action(
            agent_name="BrowserAutomationAgent",
            decision=d,
            execution_result="Success",
            page_url="https://scholarships.gov.in/submit",
            page_title="NSP Submit"
        )
        # Attempt to tamper with historical action rationale
        self.ledger.chain[1].action_record.decision.rationale = "TAMPERED RATIONALE POST HOC"
        valid, msg, bad_idx = self.ledger.verify_chain_integrity()
        self.assertFalse(valid)
        self.assertEqual(bad_idx, 1)
        self.assertIn("tampered", msg.lower())

    def test_deletion_detection(self):
        # Add 3 blocks
        for i in range(3):
            dec = AgentActionDecision(
                action_type=ActionType.OBSERVE,
                target_description=f"Observation {i}",
                locator_strategy=LocatorStrategy.TEXT,
                locator_value="body",
                rationale=f"Observed step {i}"
            )
            self.ledger.log_action(
                agent_name="BrowserAutomationAgent",
                decision=dec,
                execution_result=f"Step {i} ok",
                page_url=f"https://scholarships.gov.in/step{i}",
                page_title=f"Step {i}"
            )

        self.assertEqual(len(self.ledger.chain), 4)  # genesis + 3
        # Delete middle block #2
        del self.ledger.chain[2]

        valid, msg, bad_idx = self.ledger.verify_chain_integrity()
        self.assertFalse(valid)
        self.assertTrue("discontinuity" in msg.lower() or "broken" in msg.lower())

    def test_reordering_detection(self):
        for i in range(3):
            dec = AgentActionDecision(
                action_type=ActionType.OBSERVE,
                target_description=f"Action {i}",
                locator_strategy=LocatorStrategy.TEXT,
                locator_value="body",
                rationale=f"Action {i}"
            )
            self.ledger.log_action(
                agent_name="BrowserAutomationAgent",
                decision=dec,
                execution_result=f"Done {i}",
                page_url=f"https://scholarships.gov.in/{i}",
                page_title=f"Page {i}"
            )
        # Swap block 1 and block 2
        self.ledger.chain[1], self.ledger.chain[2] = self.ledger.chain[2], self.ledger.chain[1]

        valid, msg, bad_idx = self.ledger.verify_chain_integrity()
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()
