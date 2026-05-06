# abbiey.dig

Self-audit web app that generates a digital footprint report from identifiers you own (or have explicit permission to use). The default collectors use legitimate public endpoints and avoid Tor/onion and third-party “data broker” enrichment.

## Quickstart

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
export SECRET_KEY="change-me"
python run.py
```

Open http://127.0.0.1:5000

## Email verification (recommended)

Set these environment variables to enable one-time-code verification:

- SMTP_HOST
- SMTP_PORT (default 587)
- SMTP_USERNAME (optional)
- SMTP_PASSWORD (optional)
- SMTP_USE_TLS (default true)
- MAIL_FROM

## Optional sources

- HIBP_API_KEY: Enables Have I Been Pwned breach lookups for the verified email.
