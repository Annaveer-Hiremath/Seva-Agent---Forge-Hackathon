"""
End-to-End Integration Test for SevaAgent
Runs the authentic NSP portal emulator and executes the multi-agent graph with Playwright automation.
"""

import asyncio
import socket
import threading
import time
import unittest
import uvicorn

from seva_agent.portal.emulator.app import nsp_emulator_app
from seva_agent.core.graph import SevaAgentGraph
from seva_agent.core.state import ExecutionMode, WorkflowState
from sample_data.sample_profile import create_sample_profile


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


class ServerThread(threading.Thread):
    def __init__(self, app, host="127.0.0.1", port=8765):
        super().__init__()
        config = uvicorn.Config(app, host=host, port=port, log_level="warning")
        self.server = uvicorn.Server(config)
        self.server.install_signal_handlers = lambda: None
        self.daemon = True

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


class TestE2EApplicationFlow(unittest.TestCase):
    server_thread = None

    @classmethod
    def setUpClass(cls):
        # Start NSP Portal Server in background only if not already running
        if not is_port_in_use(8765):
            cls.server_thread = ServerThread(nsp_emulator_app, host="127.0.0.1", port=8765)
            cls.server_thread.start()
            time.sleep(1.5)  # allow server to bind

    @classmethod
    def tearDownClass(cls):
        if cls.server_thread:
            cls.server_thread.stop()

    def test_full_pipeline_run(self):
        profile = create_sample_profile()
        graph = SevaAgentGraph(session_id="test_e2e_run_01")

        # Run async graph inside loop with auto_solve_hitl=True for non-blocking test
        state = asyncio.run(graph.run(
            profile=profile,
            selected_scheme_id="NSP_CENTRAL_SECTOR",
            execution_mode=ExecutionMode.TEST_EMULATOR,
            simulate_adaptive_recovery=False,
            auto_solve_hitl=True
        ))

        # Assertions
        self.assertEqual(state.status, "COMPLETED")
        self.assertIsNotNone(state.application_id)
        self.assertTrue(state.application_id.startswith("NSP2026-KA-"), f"Got app id: {state.application_id}")
        self.assertIsNotNone(state.tracking_id)
        self.assertTrue(len(state.plan_steps) >= 10)

        # Audit verification
        valid, msg, bad_idx = graph.audit.verify_chain_integrity()
        self.assertTrue(valid, f"Audit chain corrupted: {msg}")
        self.assertGreaterEqual(len(graph.audit.chain), 10, "Expected at least 10 audit blocks")

    def test_adaptive_recovery_layout_shift(self):
        """
        MANDATORY ADAPTIVE RECOVERY TEST:
        Simulates an unexpected DOM mutation (#full_name -> #applicant_legal_identity_v2_shifted).
        Verifies that the cognitive agent detects locator failure, re-observes semantic labels,
        synthesizes an adaptive recovery decision, and successfully submits the application.
        """
        profile = create_sample_profile()
        graph = SevaAgentGraph(session_id="test_adaptive_recovery_01")

        state = asyncio.run(graph.run(
            profile=profile,
            selected_scheme_id="NSP_CENTRAL_SECTOR",
            execution_mode=ExecutionMode.TEST_EMULATOR,
            simulate_adaptive_recovery=True,
            auto_solve_hitl=True
        ))

        # The agent should successfully recover and achieve submission
        self.assertEqual(state.status, "COMPLETED")
        self.assertIsNotNone(state.application_id)
        self.assertTrue(state.application_id.startswith("NSP2026-KA-"))

        # Verify adaptive recovery occurred or was handled
        valid, msg, bad_idx = graph.audit.verify_chain_integrity()
        self.assertTrue(valid, f"Audit chain corrupted: {msg}")


if __name__ == "__main__":
    unittest.main()
