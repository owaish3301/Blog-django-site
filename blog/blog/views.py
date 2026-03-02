from django.shortcuts import render
from posts.models import Post


def landing_page(request):
    latest_posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by('-published_at')[:3]
    return render(request, 'landing_page/index.html', {'latest_posts': latest_posts})