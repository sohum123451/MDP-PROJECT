"""
Master Review Presentation & Live Demonstration Launcher.
EchoScribe-AI / SonoAssist: Real-Time Multimodal Ultrasound Reporting Platform.
Integrates deliverables across all 5 team members:
- Joel (CSE Core 1)
- Sohum (CSE Core 2)
- Manya (Business Systems & DS)
- Dinesh (IT)
- Nikilan (Health Science)
"""

import sys
import subprocess
import webbrowser
import threading
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from clinical_ui.server import run_server, PORT


def launch_presentation():
    print("=" * 85)
    print("  ECHOSCRIBE-AI: MULTIMODAL ULTRASOUND CLINICAL DOCUMENTATION PLATFORM")
    print("  BAXXX191 Basic Multidisciplinary Project - Master Presentation Launcher")
    print("=" * 85)
    print("\n[TEAM ROSTER & RESPONSIBILITY BREAKDOWN]")
    print("  • Joel    (CSE Core 1):           Capture & Lead Systems Integrator (Branch: joel)")
    print("  • Sohum   (CSE Core 2):           Speech Models & Biased ASR Lead   (Branch: sohum)")
    print("  • Manya   (Business Systems/DS):  Data Science, Harness & ROI Lead  (Branch: manya)")
    print("  • Dinesh  (IT):                   Review Interface & Audit Lead     (Branch: dinesh)")
    print("  • Nikilan (Health Science):       Clinical Lead & Domain Expert     (Branch: nikilan)")

    print("\n[1] Running Pre-Flight Multidisciplinary Test Suite...")
    try:
        res = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        print(f"    Test Results: {res.stdout.strip()}")
    except Exception as e:
        print(f"    Note on tests: {e}")

    # Launch browser automatically after 1 second
    url = f"http://localhost:{PORT}"
    def open_browser():
        time.sleep(1.2)
        print(f"\n[2] Launching Presentation & Clinical Review Interface in Browser...")
        print(f"    Opening: {url}\n")
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()

    print("=" * 85)
    print(f"  LIVE CLINICAL REVIEW SERVER ACTIVE AT: {url}")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 85)

    try:
        run_server(PORT)
    except KeyboardInterrupt:
        print("\nReview presentation server gracefully stopped.")


if __name__ == "__main__":
    launch_presentation()
