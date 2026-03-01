from django.shortcuts import render
from .models import Post

# Create your views here.


def get_all_posts(request):
    posts = Post.objects.all()
    return render(request, "posts/blog.html", {'posts': posts, 'featured_blog':None})

def get_post_detail(request):
    pass