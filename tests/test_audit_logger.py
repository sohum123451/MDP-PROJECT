"""
Unit Tests for Clinical Audit Logger and Compliance Trail (Dinesh - IT Lead).
"""

from clinical_ui.audit_logger import ClinicalAuditLogger, AuditLogEntry


def test_audit_log_entry_checksum():
    entry = AuditLogEntry(
        event_id="EVT_01",
        timestamp=1700000000.0,
        session_id="SESS_01",
        user_id="RAD_ALVAREZ",
        user_role="radiologist",
        action="REPORT_EDIT",
        field_changed="liver_finding",
        previous_value="normal",
        new_value="steatosis"
    )

    assert len(entry.checksum) == 16
    assert entry.to_dict()["action"] == "REPORT_EDIT"
    assert entry.to_dict()["checksum"] == entry.checksum


def test_audit_logger_append_and_retrieve(tmp_path):
    logger = ClinicalAuditLogger(log_dir=str(tmp_path))

    logger.log_edit(
        session_id="SESS_TEST",
        user_id="RAD_01",
        user_role="radiologist",
        field_changed="gallbladder",
        previous_value="normal wall",
        new_value="wall thickening 4.5mm"
    )

    logger.log_status_change(
        session_id="SESS_TEST",
        user_id="RAD_01",
        user_role="radiologist",
        new_status="FINAL_APPROVED"
    )

    history = logger.get_session_history("SESS_TEST")
    assert len(history) == 2
    assert history[0]["field_changed"] == "gallbladder"
    assert history[1]["action"] == "STATUS_TRANSITION_TO_FINAL_APPROVED"
