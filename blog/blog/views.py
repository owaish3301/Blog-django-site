from django.shortcuts import render
from posts.models import Post
from django.utils import timezone


def landing_page(request):
    latest_posts = Post.objects.filter(
        status=Post.Status.PUBLISHED, published_at__lte=timezone.now()
    ).order_by("-published_at")[:3]
    return render(request, "landing_page/index.html", {"latest_posts": latest_posts})

