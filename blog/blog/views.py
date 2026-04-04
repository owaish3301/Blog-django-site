from django.shortcuts import render
from posts.models import Post
from django.utils import timezone
from django.conf import settings
from django.shortcuts import redirect

def landing_page(request):
    latest_posts = Post.objects.filter(
        status=Post.Status.PUBLISHED, published_at__lte=timezone.now()
    ).order_by("-published_at")[:3]
    return render(request, "landing_page/index.html", {"latest_posts": latest_posts})


def legal_page(request):
    return render(
        request,
        "legal/legal.html",
        {
            "contact_email": getattr(settings, "DEFAULT_FROM_EMAIL", ""),
            "last_updated": "April 4, 2026",
        },
    )

def about_page(request):
    return redirect('https://owaish.codes')