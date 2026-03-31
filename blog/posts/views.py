from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from django.utils import timezone
from .forms import SubscriptionForm

# Create your views here.
def get_all_posts(request):
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            redirect("/blog/?subscribed=1")
        else:
            redirect("/blog/?subscribed=error")
    else:
        form = SubscriptionForm()

    published = Post.objects.filter(
        status=Post.Status.PUBLISHED, published_at__lte=timezone.now()
    )
    total_count = published.count()
    featured_blog = published.first()  # latest published post
    posts = published.exclude(pk=featured_blog.pk) if featured_blog else published

    paginator = Paginator(posts, 9)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    pagination_range = list(
        paginator.get_elided_page_range(number=page_obj.number)
    )

    return render(
        request,
        "posts/blog.html",
        {
            "posts": page_obj,
            "pagination_range": pagination_range,
            "pagination_ellipsis": paginator.ELLIPSIS,
            "featured_blog": featured_blog,
            "total_count": total_count,
            "form" : form
        },
    )


def get_post_detail(request, slug):
    blog = get_object_or_404(
        Post, slug=slug, status=Post.Status.PUBLISHED, published_at__lte=timezone.now()
    )
    return render(request, "posts/blog_detail.html", {"blog": blog})
