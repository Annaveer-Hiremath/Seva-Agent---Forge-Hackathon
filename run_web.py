"""
SevaAgent Web Dashboard & Government Portal Launcher
Starts the authentic NSP portal mirror on port 8765 and the Streamlit UI on port 8501.
"""

import os
import subprocess
import sys
import threading
import time
import uvicorn
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from seva_agent.portal.emulator.app import nsp_emulator_app


class PortalServerThread(threading.Thread):
    def __init__(self, host="127.0.0.1", port=8765):
        super().__init__()
        config = uvicorn.Config(nsp_emulator_app, host=host, port=port, log_level="warning")
        self.server = uvicorn.Server(config)
        self.server.install_signal_handlers = lambda: None
        self.daemon = True

    def run(self):
        self.server.run()


def main():
    print("=====================================================================")
    print("  Starting SevaAgent Web Dashboard & Government Portal Server")
    print("=====================================================================")
    
    # 1. Start Portal Server
    print("-> Starting National Scholarship Portal Server on http://127.0.0.1:8765 ...")
    server = PortalServerThread()
    server.start()
    time.sleep(1.5)
    print("   [OK] Government Portal Server is online.")

    # 2. Launch Streamlit UI
    ui_script = BASE_DIR / "seva_agent" / "ui" / "app.py"
    print(f"-> Launching Streamlit Dashboard ({ui_script}) ...")
    print("-> Web UI will open at http://localhost:8501\n")

    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(ui_script),
        "--server.port=8501", "--server.headless=false", "--browser.gatherUsageStats=false"
    ])


if __name__ == "__main__":
    main()
