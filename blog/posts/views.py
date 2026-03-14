from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Post
from django.utils import timezone


# Create your views here.
def get_all_posts(request):
    published = Post.objects.filter(
        status=Post.Status.PUBLISHED, published_at__lte=timezone.now()
    )
    total_count = published.count()
    featured_blog = published.first()  # latest published post
    posts = published.exclude(pk=featured_blog.pk) if featured_blog else published

    paginator = Paginator(posts, 9)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "posts/blog.html",
        {
            "posts": page_obj,
            "featured_blog": featured_blog,
            "total_count": total_count,
        },
    )


def get_post_detail(request, slug):
    blog = get_object_or_404(
        Post, slug=slug, status=Post.Status.PUBLISHED, published_at__lte=timezone.now()
    )
    return render(request, "posts/blog_detail.html", {"blog": blog})
