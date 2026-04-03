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

## 3. Commenter verification is not concurrency-safe
- Severity: High
- Summary: `verify_otp()` uses `update_or_create(email=...)`, but `VerifiedCommenter.email` is not unique and the `token` is generated only later in `save()`.
- Why it matters: Concurrent verification requests for the same email can create duplicate commenter rows or trigger integrity problems. Later lookups that expect a single row can then raise `MultipleObjectsReturned` and return a 500.
- Affected filepaths:
  - `blog/comments/views.py`
  - `blog/comments/models.py`


## 5. Comment APIs can 500 on bad input and expose scheduled posts
- Severity: Medium
- Summary: `get_comments()` casts `page` with `int(request.GET.get("page", 1))` without validation, so `/comments/list/<slug>/?page=abc` can raise a server error. Also, `post_comment()` and `get_comments()` only require `status=PUBLISHED`; they do not enforce `published_at__lte=timezone.now()`.
- Why it matters: A malformed request can trigger a 500, and scheduled posts can become discoverable and commentable before the post detail page is publicly available.
- Affected filepaths:
  - `blog/comments/views.py`
  - `blog/posts/views.py`


## 7. Markdown rendering is marked safe without sanitization
- Severity: Medium
- Summary: Post body markdown is converted to HTML and returned with `mark_safe()` after enabling multiple markdown extensions, but no sanitization step is applied.
- Why it matters: If post content is ever not fully trusted, this becomes an XSS path that can execute arbitrary HTML or script payloads in readers' browsers.
- Affected filepaths:
  - `blog/posts/templatetags/markdown_extras.py`
  - `blog/posts/templates/posts/blog_detail.html`

## 8. `published_at` does not reliably mean "time actually published"
- Severity: Medium
- Summary: `published_at` defaults at row creation time. If a post is drafted first and published later, ordering, "latest post", and featured-post logic can still reflect the draft creation timestamp unless the field is manually updated.
- Why it matters: Production content ordering can be wrong even when the post status is correct, which affects homepage latest-post selection and blog page featuring.
- Affected filepaths:
  - `blog/posts/models.py`
  - `blog/posts/views.py`
  - `blog/blog/views.py`

