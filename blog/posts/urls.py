from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_all_posts, name="get_all_posts"),
    path('<slug:slug>', views.get_post_detail, name="post_detail")
]
