"""
On-Premises HTTP Serving Engine for EchoScribe-AI Review Interface.
Member 4 (Dinesh - IT Deliverable).
Serves the web dashboard, provides REST audit logging endpoints,
and maintains local data isolation for hospital network deployment.
"""

import http.server
import socketserver
import json
import urllib.parse
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from clinical_ui.audit_logger import ClinicalAuditLogger

PORT = 8080
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
audit_logger = ClinicalAuditLogger()


class ClinicalRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler serving web assets and clinical REST endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(BASE_DIR / "index.html", "rb") as f:
                self.wfile.write(f.read())
            return

        elif parsed.path == "/api/health":
            self._send_json({"status": "healthy", "service": "EchoScribe-AI IT Server", "deployment": "on-premises"})
            return

        elif parsed.path == "/api/audit-history":
            events = audit_logger.get_session_history("SESS_DEMO")
            self._send_json({"events": events})
            return

        # Serve static files
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/audit-log":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                entry = audit_logger.log_edit(
                    session_id=data.get("session_id", "SESS_DEMO"),
                    user_id=data.get("user_id", "UNKNOWN"),
                    user_role=data.get("user_role", "radiologist"),
                    field_changed=data.get("field_changed", "general"),
                    previous_value=data.get("previous_value", ""),
                    new_value=data.get("new_value", ""),
                    clinical_justification=data.get("clinical_justification", "Review edit")
                )
                self._send_json({"status": "logged", "entry": entry.to_dict()})
            except Exception as e:
                self.send_error(400, f"Invalid JSON payload: {str(e)}")
            return

        self.send_error(404, "Endpoint not found")

    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(port: int = PORT):
    print("=" * 70)
    print(f"  ECHOSCRIBE-AI ON-PREMISES CLINICAL REVIEW SERVER (IT LEAD: DINESH)")
    print(f"  Serving dashboard at: http://localhost:{port}")
    print("=" * 70)
    with socketserver.TCPServer(("", port), ClinicalRequestHandler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()
