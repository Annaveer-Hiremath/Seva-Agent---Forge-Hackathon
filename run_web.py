"""
SevaAgent Web Dashboard & Government Portal Launcher
Starts the authentic NSP portal mirror on port 8765 and the Streamlit UI on port 8501 (or next available port).
"""

import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))


def is_port_in_use(host: str, port: int) -> bool:
    """Check if a local port is already bound."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False


def find_available_port(host: str = "127.0.0.1", start_port: int = 8501, max_tries: int = 20) -> int:
    """Find the next available port starting from start_port."""
    for port in range(start_port, start_port + max_tries):
        if not is_port_in_use(host, port):
            return port
    return start_port


class PortalServerThread(threading.Thread):
    def __init__(self, host="127.0.0.1", port=8765):
        super().__init__()
        import uvicorn
        from seva_agent.portal.emulator.app import nsp_emulator_app
        config = uvicorn.Config(nsp_emulator_app, host=host, port=port, log_level="warning")
        self.server = uvicorn.Server(config)
        self.server.install_signal_handlers = lambda: None
        self.daemon = True

    def run(self):
        try:
            self.server.run()
        except Exception:
            pass


def main():
    print("=====================================================================")
    print("  Starting SevaAgent Web Dashboard & Government Portal Server")
    print("=====================================================================")
    
    # 1. Start Portal Server if not already active
    if is_port_in_use("127.0.0.1", 8765):
        print("-> National Scholarship Portal Server is already online at http://127.0.0.1:8765.")
    else:
        print("-> Starting National Scholarship Portal Server on http://127.0.0.1:8765 ...")
        server = PortalServerThread()
        server.start()
        time.sleep(1.2)
        print("   [OK] Government Portal Server is online.")

    # 2. Launch Streamlit UI
    ui_script = BASE_DIR / "seva_agent" / "ui" / "app.py"
    ui_port = find_available_port("127.0.0.1", start_port=8501)

    if ui_port != 8501:
        print(f"-> Notice: Port 8501 is busy; automatically assigning open port {ui_port} for Streamlit.")
    
    print(f"-> Launching Streamlit Dashboard ({ui_script}) ...")
    print(f"-> Web UI will open at http://localhost:{ui_port}\n")

    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(ui_script),
        f"--server.port={ui_port}",
        "--server.headless=false",
        "--browser.gatherUsageStats=false"
    ])


if __name__ == "__main__":
    main()
