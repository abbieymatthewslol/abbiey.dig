import secrets
import time
from typing import Any

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for

from .collectors import email_checks, phone_checks, username_checks
from .mail import can_send_email, send_verification_email
from .storage import load_report, save_report, set_email_code, verify_email_code


bp = Blueprint("main", __name__)


@bp.before_app_request
def ensure_session_id() -> None:
    if "sid" not in session:
        session["sid"] = secrets.token_urlsafe(16)


@bp.get("/")
def index() -> str:
    return render_template("index.html", can_email=can_send_email())


@bp.post("/request-email-code")
def request_email_code() -> str:
    email = (request.form.get("email") or "").strip()
    if not email:
        return render_template("index.html", can_email=can_send_email(), error="Email is required to verify.")
    if not can_send_email():
        return render_template("index.html", can_email=False, error="Email verification is not configured.")

    code = _generate_code()
    set_email_code(email, code)
    send_verification_email(email, code)
    session["pending_email"] = email
    session.pop("verified_email", None)
    return render_template("verify_email.html", email=email)


@bp.post("/verify-email")
def verify_email() -> str:
    email = (request.form.get("email") or "").strip()
    code = (request.form.get("code") or "").strip()
    if not email or not code:
        return render_template("verify_email.html", email=email, error="Email and code are required.")
    ok = verify_email_code(email, code)
    if not ok:
        return render_template("verify_email.html", email=email, error="Invalid or expired code.")
    session["verified_email"] = email
    session.pop("pending_email", None)
    return redirect(url_for("main.index"))


@bp.post("/scan")
def scan() -> str:
    started_at = time.time()

    first_name = (request.form.get("first_name") or "").strip()
    middle_name = (request.form.get("middle_name") or "").strip()
    last_name = (request.form.get("last_name") or "").strip()
    email = (request.form.get("email") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    default_region = (request.form.get("default_region") or "US").strip().upper()
    usernames_raw = (request.form.get("usernames") or "").strip()

    if email:
        verified_email = (session.get("verified_email") or "").strip()
        if verified_email.lower() != email.lower():
            return render_template(
                "index.html",
                can_email=can_send_email(),
                error="Email verification required. Request a code and verify this email before scanning.",
                form=request.form,
            )

    usernames = [x.strip() for x in usernames_raw.replace(",", "\n").splitlines() if x.strip()]
    report: dict[str, Any] = {
        "input": {
            "name": {"first": first_name, "middle": middle_name, "last": last_name},
            "email": email,
            "phone": phone,
            "usernames": usernames,
            "default_phone_region": default_region,
        },
        "results": {},
        "generated_at": int(time.time()),
        "elapsed_ms": None,
    }

    if email:
        report["results"]["email"] = email_checks.run(email)
    if phone:
        report["results"]["phone"] = phone_checks.run(phone, default_region=default_region)
    if usernames:
        report["results"]["usernames"] = username_checks.run(usernames)

    report["elapsed_ms"] = int((time.time() - started_at) * 1000)
    save_report(session["sid"], report)
    return render_template("report.html", report=report)


@bp.get("/report.json")
def report_json():
    rep = load_report(session.get("sid", ""))
    if not rep:
        return jsonify({"error": "No report available"}), 404
    return jsonify(rep)


def _generate_code() -> str:
    return f"{secrets.randbelow(1000000):06d}"

