from django.shortcuts import render
# from django.http import HttpResponse

# Create your views here.


def get_all_posts(request):
    return render(request, "posts/blog.html")
