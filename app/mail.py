import smtplib
from email.message import EmailMessage

from flask import current_app


def can_send_email() -> bool:
    cfg = current_app.config
    return bool(cfg.get("SMTP_HOST") and cfg.get("MAIL_FROM"))


def send_verification_email(to_email: str, code: str) -> None:
    cfg = current_app.config

    msg = EmailMessage()
    msg["Subject"] = "Your verification code"
    msg["From"] = cfg["MAIL_FROM"]
    msg["To"] = to_email
    msg.set_content(f"Your verification code is: {code}\n\nIf you did not request this, you can ignore this email.")

    with smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=10) as smtp:
        if cfg["SMTP_USE_TLS"]:
            smtp.starttls()
        if cfg["SMTP_USERNAME"] and cfg["SMTP_PASSWORD"]:
            smtp.login(cfg["SMTP_USERNAME"], cfg["SMTP_PASSWORD"])
        smtp.send_message(msg)

