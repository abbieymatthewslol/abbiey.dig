import time
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CodeRecord:
    code: str
    created_at: float


_email_codes: dict[str, CodeRecord] = {}


def set_email_code(email: str, code: str) -> None:
    _email_codes[email.lower()] = CodeRecord(code=code, created_at=time.time())


def verify_email_code(email: str, code: str, ttl_seconds: int = 900) -> bool:
    key = email.lower()
    rec = _email_codes.get(key)
    if not rec:
        return False
    if time.time() - rec.created_at > ttl_seconds:
        _email_codes.pop(key, None)
        return False
    if rec.code != code.strip():
        return False
    _email_codes.pop(key, None)
    return True


@dataclass(frozen=True)
class ReportRecord:
    report: dict[str, Any]
    created_at: float


_reports: dict[str, ReportRecord] = {}


def _prune_reports(ttl_seconds: int) -> None:
    now = time.time()
    expired = [sid for sid, rec in _reports.items() if now - rec.created_at > ttl_seconds]
    for sid in expired:
        _reports.pop(sid, None)


def save_report(session_id: str, report: dict[str, Any], ttl_seconds: int = 3600) -> None:
    _prune_reports(ttl_seconds)
    _reports[session_id] = ReportRecord(report=report, created_at=time.time())


def load_report(session_id: str, ttl_seconds: int = 3600) -> dict[str, Any] | None:
    _prune_reports(ttl_seconds)
    rec = _reports.get(session_id)
    return rec.report if rec else None
