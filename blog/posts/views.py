from django.shortcuts import render, get_object_or_404
from .models import Post

# Create your views here.


def get_all_posts(request):
    published = Post.objects.filter(status=Post.Status.PUBLISHED)
    total_count = published.count()
    featured_blog = published.first()  # latest published post
    posts = published.exclude(pk=featured_blog.pk) if featured_blog else published
    return render(
        request,
        "posts/blog.html",
        {
            "posts": posts,
            "featured_blog": featured_blog,
            "total_count": total_count,
        },
    )


def get_post_detail(request, slug):
    blog = get_object_or_404(Post, slug=slug)
    return render(request, "posts/blog_detail.html", {"blog": blog})

