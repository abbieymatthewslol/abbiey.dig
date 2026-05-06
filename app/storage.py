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


_reports: dict[str, dict[str, Any]] = {}


def save_report(session_id: str, report: dict[str, Any]) -> None:
    _reports[session_id] = report


def load_report(session_id: str) -> dict[str, Any] | None:
    return _reports.get(session_id)

