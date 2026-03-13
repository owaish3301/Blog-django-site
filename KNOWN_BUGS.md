# Known Bugs

## 1. Markdown output is marked safe without sanitization
- Summary: Post body markdown is converted to HTML and returned with `mark_safe()`. If post content is ever not fully trusted, this allows XSS through rendered HTML.
- Affected filepaths:
  - `blog/posts/templatetags/markdown_extras.py`
  - `blog/posts/templates/posts/blog_detail.html`

## 2. `published_at` does not reliably mean "time actually published"
- Summary: `published_at` defaults when the row is created. If a post is created as a draft and published later, ordering and featured/latest selection can still reflect the draft creation time unless the field is updated manually.
- Affected filepaths:
  - `blog/posts/models.py`
  - `blog/posts/views.py`
  - `blog/blog/views.py`

## 4. Newsletter forms submit with GET and do nothing useful
- Summary: Both newsletter forms submit back to the current page with no backend handling. The email ends up in the query string and no subscription is processed.
- Affected filepaths:
  - `blog/posts/templates/posts/blog.html`
  - `blog/templates/landing_page/index.html`

