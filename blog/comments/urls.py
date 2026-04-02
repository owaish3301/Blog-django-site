from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("post/", views.post_comment, name="post_comment"),
    path("list/<slug:slug>/", views.get_comments, name="get_comments"),
    path("check-auth/", views.check_auth, name="check_auth"),
]
