# Known Bugs

Production review updated on 2026-04-03.

## 1. Production settings are still using unsafe development defaults
- Severity: High
- Summary: The site is configured like a development deployment. `SECRET_KEY` is hard-coded, `DEBUG` is enabled, `ALLOWED_HOSTS` allows everything, and the deploy check reports missing HSTS, missing HTTPS redirect, and insecure cookie settings.
- Why it matters: In production this can expose Django debug pages, weaken cookie protection, and make host-header or transport-security mistakes much more damaging.
- Evidence:
  - `python manage.py check --deploy` reported warnings `security.W004`, `W008`, `W009`, `W012`, `W016`, and `W018`.
- Affected filepaths:
  - `blog/blog/settings.py`

## 2. App startup is brittle if `DATABASE_URL` is missing or malformed
- Severity: High
- Summary: Settings parsing assumes `DATABASE_URL` exists and is valid. If it is missing, `urlparse(os.getenv("DATABASE_URL"))` can lead to a `TypeError` during settings import instead of a clean configuration error. The parsed database port is also ignored because the code hard-codes `5432`.
- Why it matters: A bad environment variable can take the whole site down at boot, and alternate ports cannot be honored even if they are present in the URL.
- Affected filepaths:
  - `blog/blog/settings.py`
