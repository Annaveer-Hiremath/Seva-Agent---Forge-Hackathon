"""
End-to-End Integration Test for SevaAgent
Runs the authentic NSP portal emulator and executes the multi-agent graph with Playwright automation.
"""

import asyncio
import threading
import time
import unittest
import uvicorn

from seva_agent.portal.emulator.app import nsp_emulator_app
from seva_agent.core.graph import SevaAgentGraph
from sample_data.sample_profile import create_sample_profile


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
    @classmethod
    def setUpClass(cls):
        # Start NSP Portal Server in background
        cls.server_thread = ServerThread(nsp_emulator_app, host="127.0.0.1", port=8765)
        cls.server_thread.start()
        time.sleep(1.5)  # allow server to bind

    @classmethod
    def tearDownClass(cls):
        cls.server_thread.stop()

    def test_full_pipeline_run(self):
        profile = create_sample_profile()
        graph = SevaAgentGraph(session_id="test_e2e_run_01")

        # Run async graph inside loop
        state = asyncio.run(graph.run(
            profile=profile,
            selected_scheme_id="NSP_CENTRAL_SECTOR",
            auto_solve_hitl=True
        ))

        # Assertions
        self.assertEqual(state.status, "COMPLETED")
        self.assertIsNotNone(state.application_id)
        self.assertTrue(state.application_id.startswith("NSP2026-KA-"), f"Got app id: {state.application_id}")
        self.assertIsNotNone(state.tracking_id)
        self.assertTrue(len(state.plan_steps) >= 10)

        # Audit verification
        valid, msg = graph.audit.verify_chain_integrity()
        self.assertTrue(valid, f"Audit chain corrupted: {msg}")
        self.assertGreaterEqual(len(graph.audit.chain), 10, "Expected at least 10 audit blocks")

        print("\n=== E2E Integration Test Succeeded ===")
        print(f"Generated Official Application ID: {state.application_id}")
        print(f"Tracking Reference: {state.tracking_id}")
        print(f"Audit Trail Integrity: {msg}")


if __name__ == "__main__":
    unittest.main()
