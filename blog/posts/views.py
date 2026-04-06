from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from django.utils import timezone
from .forms import SubscriptionForm
from django.core.mail import send_mail
from subscription.models import Subscriber
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

def _build_blog_list_context(request, form):
    category = request.GET.get("category")
    search = request.GET.get("q")

    published = Post.objects.filter(
        status=Post.Status.PUBLISHED, published_at__lte=timezone.now()
    )

    if category:
        published = published.filter(category__slug__iexact = category)
    if search:
        vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
        query = SearchQuery(search)

        published = published.annotate(
            rank=SearchRank(vector, query)
        ).filter(rank__gte=0.1).order_by('-rank')

    total_count = published.count()
    featured_blog = published.first()  # latest published post
    posts = published.exclude(pk=featured_blog.pk) if featured_blog else published

    paginator = Paginator(posts, 9)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    pagination_range = list(paginator.get_elided_page_range(number=page_obj.number))

    return {
        "posts": page_obj,
        "pagination_range": pagination_range,
        "pagination_ellipsis": paginator.ELLIPSIS,
        "featured_blog": featured_blog,
        "total_count": total_count,
        "form": form,
    }


def get_all_posts(request):
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()
            Subscriber.objects.get_or_create(email=email)

            try:
                send_mail(
                    "Welcome to Owaish Codes",
                    "You're now subscribed to Owaish Codes.\n\n"
                    "Whenever I publish something new, it'll land in your inbox. No spam. Just signal.\n\n"
                    "— Owaish",
                    None,
                    [email],
                    fail_silently=False,
                    html_message="""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Welcome to Owaish Codes</title>
</head>
<body style="margin:0;padding:0;background-color:#f9f9f7;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f9f9f7;padding:48px 16px;">
    <tr>
      <td align="center">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background-color:#ffffff;border-radius:24px;border:1px solid #e5e5e0;overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="background-color:#0f0f0e;padding:36px 40px;">
              <p style="margin:0;font-family:monospace;font-size:11px;letter-spacing:0.2em;text-transform:uppercase;color:#888;">Owaish Codes</p>
              <h1 style="margin:12px 0 0;font-size:26px;font-weight:700;color:#ffffff;line-height:1.3;">You're in the loop.</h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <p style="margin:0 0 20px;font-size:16px;line-height:1.7;color:#4a4a45;">
                Hey — thanks for subscribing.
              </p>
              <p style="margin:0 0 20px;font-size:16px;line-height:1.7;color:#4a4a45;">
                Whenever I publish something new — a deep dive, a build log, or a brain dump — it'll land quietly in your inbox.
              </p>
              <p style="margin:0 0 32px;font-size:16px;line-height:1.7;color:#4a4a45;">
                No noise. No spam. Just signal.
              </p>

              <!-- CTA -->
              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="border-radius:100px;background-color:#0f0f0e;">
                    <a href="https://blog.owaish.codes" style="display:inline-block;padding:14px 28px;font-family:monospace;font-size:12px;letter-spacing:0.15em;text-transform:uppercase;color:#ffffff;text-decoration:none;font-weight:700;">
                      Read the blog →
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Divider -->
          <tr>
            <td style="padding:0 40px;">
              <div style="height:1px;background-color:#e5e5e0;"></div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:28px 40px;">
              <p style="margin:0;font-size:13px;color:#999;line-height:1.6;font-style:italic;">
                — Owaish
              </p>
              <p style="margin:12px 0 0;font-size:11px;color:#bbb;font-family:monospace;">
                You're receiving this because you subscribed at blog.owaish.codes
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
                    """,
                )

                response = redirect("/blog/?subscribed=1")
                response.set_cookie("subscribed", "1", max_age=60 * 60 * 24 * 365)
                return response
            except Exception:
                form.add_error(
                    None,
                    "Your subscription was saved, but the welcome email could not be sent right now. "
                    "This can happen when the mail provider rejects the address or rate-limits requests.",
                )

                response = render(
                    request,
                    "posts/blog.html",
                    _build_blog_list_context(request, form),
                )
                response.set_cookie("subscribed", "1", max_age=60 * 60 * 24 * 365)
                return response
    else:
        form = SubscriptionForm()

    return render(
        request,
        "posts/blog.html",
        _build_blog_list_context(request, form),
    )


def get_post_detail(request, slug):
    blog = get_object_or_404(
        Post, slug=slug, status=Post.Status.PUBLISHED, published_at__lte=timezone.now()
    )

    # Initial comments (first page)
    from comments.models import Comment, VerifiedCommenter

    comments_qs = Comment.objects.filter(
        post=blog, is_approved=True
    ).select_related("commenter").order_by("-created_at")

    total_comments = comments_qs.count()
    initial_comments = comments_qs[:5]
    has_more_comments = total_comments > 5

    # Check if visitor is verified via cookie
    commenter_name = None
    commenter_email = None
    is_verified = False
    token = request.COOKIES.get("commenter_token")
    if token:
        try:
            commenter = VerifiedCommenter.objects.get(token=token)
            if not commenter.is_expired:
                is_verified = True
                commenter_name = commenter.name
                commenter_email = commenter.email
        except VerifiedCommenter.DoesNotExist:
            pass

    return render(request, "posts/blog_detail.html", {
        "blog": blog,
        "comments": initial_comments,
        "total_comments": total_comments,
        "has_more_comments": has_more_comments,
        "is_verified": is_verified,
        "commenter_name": commenter_name,
        "commenter_email": commenter_email,
    })

