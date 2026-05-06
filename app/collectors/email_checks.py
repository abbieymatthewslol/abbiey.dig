import hashlib
from typing import Any

import dns.resolver
import requests
from email_validator import EmailNotValidError, validate_email
from flask import current_app


def run(email: str) -> dict[str, Any]:
    result: dict[str, Any] = {"input": email}
    normalized = email.strip()

    try:
        v = validate_email(normalized, check_deliverability=False)
        normalized = v.normalized
        result["normalized"] = normalized
        result["valid_format"] = True
    except EmailNotValidError as e:
        result["valid_format"] = False
        result["error"] = str(e)
        return result

    domain = normalized.split("@", 1)[1]
    result["domain"] = domain
    result["dns"] = _dns_checks(domain)
    result["gravatar"] = _gravatar_check(normalized)
    result["hibp"] = _hibp_breaches(normalized)
    return result


def _dns_checks(domain: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    try:
        mx = dns.resolver.resolve(domain, "MX")
        out["mx_records"] = sorted([str(r.exchange).rstrip(".") for r in mx])
    except Exception:
        out["mx_records"] = []
    try:
        a = dns.resolver.resolve(domain, "A")
        out["a_records"] = sorted([str(r) for r in a])
    except Exception:
        out["a_records"] = []
    return out


def _gravatar_check(email: str) -> dict[str, Any]:
    h = hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()
    url = f"https://www.gravatar.com/avatar/{h}?d=404"
    timeout = float(current_app.config.get("HTTP_TIMEOUT_SECONDS", 8))
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "footprint-audit/1.0"})
        return {"url": url, "has_gravatar": r.status_code == 200, "status_code": r.status_code}
    except requests.RequestException as e:
        return {"url": url, "has_gravatar": None, "error": str(e)}


def _hibp_breaches(email: str) -> dict[str, Any]:
    api_key = current_app.config.get("HIBP_API_KEY") or ""
    if not api_key:
        return {"enabled": False}

    timeout = float(current_app.config.get("HTTP_TIMEOUT_SECONDS", 8))
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {
        "hibp-api-key": api_key,
        "user-agent": "footprint-audit/1.0",
        "accept": "application/json",
    }
    params = {"truncateResponse": "false"}
    try:
        r = requests.get(url, timeout=timeout, headers=headers, params=params)
        if r.status_code == 404:
            return {"enabled": True, "breaches": []}
        if r.status_code != 200:
            return {"enabled": True, "error": f"HIBP returned {r.status_code}", "status_code": r.status_code}
        data = r.json()
        breaches = []
        for b in data:
            breaches.append(
                {
                    "name": b.get("Name"),
                    "title": b.get("Title"),
                    "domain": b.get("Domain"),
                    "breach_date": b.get("BreachDate"),
                    "added_date": b.get("AddedDate"),
                    "pwn_count": b.get("PwnCount"),
                    "data_classes": b.get("DataClasses"),
                    "is_verified": b.get("IsVerified"),
                    "is_fabricated": b.get("IsFabricated"),
                    "is_sensitive": b.get("IsSensitive"),
                    "description": b.get("Description"),
                }
            )
        return {"enabled": True, "breaches": breaches}
    except requests.RequestException as e:
        return {"enabled": True, "error": str(e)}

