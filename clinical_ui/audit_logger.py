"""
Audit Logging and Compliance Engine for Radiologist Report Modifications.
Member 4 (Dinesh - IT Lead Deliverable).
Provides tamper-evident edit tracking, role-based change attribution,
and structured audit logging required for hospital on-premises PACS deployment.
"""

import json
import time
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path


class AuditLogEntry:
    """Represents a single immutable change event in the clinical report."""

    def __init__(
        self,
        event_id: str,
        timestamp: float,
        session_id: str,
        user_id: str,
        user_role: str,
        action: str,
        field_changed: str,
        previous_value: Any,
        new_value: Any,
        clinical_justification: str = "Clinical review correction"
    ):
        self.event_id = event_id
        self.timestamp = timestamp
        self.session_id = session_id
        self.user_id = user_id
        self.user_role = user_role
        self.action = action
        self.field_changed = field_changed
        self.previous_value = previous_value
        self.new_value = new_value
        self.clinical_justification = clinical_justification
        self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """SHA-256 tamper-evident integrity hash."""
        raw_str = f"{self.event_id}:{self.timestamp}:{self.user_id}:{self.field_changed}:{self.new_value}"
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": round(self.timestamp, 3),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.timestamp)),
            "session_id": self.session_id,
            "user_id": self.user_id,
            "user_role": self.user_role,
            "action": self.action,
            "field_changed": self.field_changed,
            "previous_value": self.previous_value,
            "new_value": self.new_value,
            "clinical_justification": self.clinical_justification,
            "checksum": self.checksum
        }


class ClinicalAuditLogger:
    """
    On-premises persistent audit log manager.
    Tracks every radiologist keystroke, caliper edit, or approval state transition.
    """

    def __init__(self, log_dir: Optional[str] = None):
        self.log_dir = Path(log_dir or "data/audit_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.events: List[AuditLogEntry] = []

    def log_edit(
        self,
        session_id: str,
        user_id: str,
        user_role: str,
        field_changed: str,
        previous_value: Any,
        new_value: Any,
        clinical_justification: str = "Radiologist manual correction"
    ) -> AuditLogEntry:
        """Records a clinical report edit event."""
        event_id = f"AUD_{int(time.time()*1000)}_{len(self.events)+1}"
        entry = AuditLogEntry(
            event_id=event_id,
            timestamp=time.time(),
            session_id=session_id,
            user_id=user_id,
            user_role=user_role,
            action="REPORT_TEXT_EDIT",
            field_changed=field_changed,
            previous_value=previous_value,
            new_value=new_value,
            clinical_justification=clinical_justification
        )
        self.events.append(entry)
        self._append_to_disk(session_id, entry)
        return entry

    def log_status_change(
        self,
        session_id: str,
        user_id: str,
        user_role: str,
        new_status: str,
        notes: str = ""
    ) -> AuditLogEntry:
        """Records report sign-off or approval."""
        event_id = f"AUD_{int(time.time()*1000)}_{len(self.events)+1}"
        entry = AuditLogEntry(
            event_id=event_id,
            timestamp=time.time(),
            session_id=session_id,
            user_id=user_id,
            user_role=user_role,
            action=f"STATUS_TRANSITION_TO_{new_status.upper()}",
            field_changed="report_approval_status",
            previous_value="DRAFT",
            new_value=new_status,
            clinical_justification=notes or "Final sign-off by radiologist"
        )
        self.events.append(entry)
        self._append_to_disk(session_id, entry)
        return entry

    def _append_to_disk(self, session_id: str, entry: AuditLogEntry) -> None:
        file_path = self.log_dir / f"{session_id}_audit_trail.jsonl"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Reads back all audit events for a session."""
        file_path = self.log_dir / f"{session_id}_audit_trail.jsonl"
        if not file_path.exists():
            return [e.to_dict() for e in self.events if e.session_id == session_id]

        events = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line.strip()))
        return events
