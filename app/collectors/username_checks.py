from typing import Any

import requests
from flask import current_app


SITES: dict[str, str] = {
    "GitHub": "https://github.com/{u}",
    "GitLab": "https://gitlab.com/{u}",
    "Reddit": "https://www.reddit.com/user/{u}",
    "Medium": "https://medium.com/@{u}",
    "DEV": "https://dev.to/{u}",
    "Hacker News": "https://news.ycombinator.com/user?id={u}",
}


def run(usernames: list[str]) -> dict[str, Any]:
    timeout = float(current_app.config.get("HTTP_TIMEOUT_SECONDS", 8))
    headers = {"User-Agent": "footprint-audit/1.0"}
    out: dict[str, Any] = {"usernames": []}

    for u in usernames:
        u = u.strip()
        if not u:
            continue
        u_entry: dict[str, Any] = {"username": u, "profiles": []}
        for site, tmpl in SITES.items():
            url = tmpl.format(u=u)
            status = _check_url(url, timeout=timeout, headers=headers)
            u_entry["profiles"].append({"site": site, "url": url, **status})
        out["usernames"].append(u_entry)

    return out


def _check_url(url: str, timeout: float, headers: dict[str, str]) -> dict[str, Any]:
    try:
        r = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        if r.status_code in {200, 301, 302}:
            return {"status": "found", "status_code": r.status_code}
        if r.status_code == 404:
            return {"status": "not_found", "status_code": r.status_code}
        if r.status_code == 429:
            return {"status": "rate_limited", "status_code": r.status_code}
        return {"status": "unknown", "status_code": r.status_code}
    except requests.RequestException as e:
        return {"status": "error", "error": str(e)}

