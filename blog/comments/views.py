import json
import random
import string
from datetime import timedelta

from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.utils import timezone
from django.shortcuts import get_object_or_404

from posts.models import Post
from .models import EmailOTP, VerifiedCommenter, Comment


def _generate_otp():
    return "".join(random.choices(string.digits, k=6))


@csrf_protect
@require_POST
def send_otp(request):
    """Send a 6-digit OTP to the provided email address."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid request body."}, status=400)

    email = data.get("email", "").strip().lower()
    name = data.get("name", "").strip()

    if not email or not name:
        return JsonResponse({"error": "Name and email are required."}, status=400)

    if len(name) > 100:
        return JsonResponse({"error": "Name is too long."}, status=400)

    # Rate limit: max 3 OTPs per email in last 10 minutes
    recent_count = EmailOTP.objects.filter(
        email=email,
        created_at__gte=timezone.now() - timedelta(minutes=10),
    ).count()
    if recent_count >= 3:
        return JsonResponse(
            {"error": "Too many OTP requests. Please wait a few minutes."},
            status=429,
        )

    otp_code = _generate_otp()

    # Save the OTP locally first
    otp_record = EmailOTP.objects.create(
        email=email,
        name=name,
        otp=otp_code,
    )

    try:
        send_mail(
            subject="Your verification code — Owaish Codes",
            message=f"Your verification code is: {otp_code}\n\nThis code expires in 10 minutes.",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
            html_message=f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0"/></head>
<body style="margin:0;padding:0;background-color:#f9f9f7;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f9f9f7;padding:48px 16px;">
    <tr><td align="center">
      <table width="100%" cellpadding="0" cellspacing="0" style="max-width:480px;background-color:#ffffff;border-radius:24px;border:1px solid #e5e5e0;overflow:hidden;">
        <tr><td style="background-color:#0f0f0e;padding:32px 36px;">
          <p style="margin:0;font-family:monospace;font-size:11px;letter-spacing:0.2em;text-transform:uppercase;color:#888;">Owaish Codes</p>
          <h1 style="margin:10px 0 0;font-size:22px;font-weight:700;color:#ffffff;">Verify your email</h1>
        </td></tr>
        <tr><td style="padding:36px;">
          <p style="margin:0 0 20px;font-size:15px;line-height:1.7;color:#4a4a45;">
            Hey {name} — here's your verification code:
          </p>
          <div style="background:#f5f0e8;border:2px dashed #c7baaa;border-radius:12px;padding:20px;text-align:center;margin:0 0 24px;">
            <span style="font-family:monospace;font-size:32px;font-weight:800;letter-spacing:0.3em;color:#cf4d2d;">{otp_code}</span>
          </div>
          <p style="margin:0;font-size:13px;color:#999;line-height:1.6;">
            This code expires in 10 minutes. If you didn't request this, just ignore this email.
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
""",
        )
    except Exception as e:
        # If sending mail failed, delete the OTP attempt so they can try again.
        otp_record.delete()
        return JsonResponse(
            {"error": "Failed to send the email. Please try again later."},
            status=500
        )

    return JsonResponse({"message": "OTP sent successfully."})


@csrf_protect
@require_POST
def verify_otp(request):
    """Verify the OTP and return a commenter token."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid request body."}, status=400)

    email = data.get("email", "").strip().lower()
    otp_code = data.get("otp", "").strip()

    if not email or not otp_code:
        return JsonResponse({"error": "Email and OTP are required."}, status=400)

    otp_record = (
        EmailOTP.objects.filter(email=email, otp=otp_code, is_used=False)
        .order_by("-created_at")
        .first()
    )

    if not otp_record:
        return JsonResponse({"error": "Invalid OTP."}, status=400)

    if otp_record.is_expired:
        return JsonResponse({"error": "OTP has expired. Please request a new one."}, status=400)

    # Mark OTP as used
    otp_record.is_used = True
    otp_record.save(update_fields=["is_used"])

    # Create or update verified commenter
    commenter, created = VerifiedCommenter.objects.update_or_create(
        email=email,
        defaults={
            "name": otp_record.name,
            "expires_at": timezone.now() + timedelta(days=30),
        },
    )
    if created or not commenter.token:
        commenter.save()  # triggers token generation in save()

    response = JsonResponse({
        "message": "Email verified successfully.",
        "name": commenter.name,
        "token": commenter.token,
    })

    # Set cookie that expires in 30 days
    response.set_cookie(
        "commenter_token",
        commenter.token,
        max_age=60 * 60 * 24 * 30,
        httponly=True,
        samesite="Lax",
    )

    return response


@csrf_protect
@require_POST
def post_comment(request):
    """Post a new comment on a blog post."""
    token = request.COOKIES.get("commenter_token")
    if not token:
        return JsonResponse({"error": "You must verify your email first."}, status=401)

    try:
        commenter = VerifiedCommenter.objects.get(token=token)
    except VerifiedCommenter.DoesNotExist:
        return JsonResponse({"error": "Invalid session. Please verify again."}, status=401)

    if commenter.is_expired:
        return JsonResponse({"error": "Session expired. Please verify your email again."}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid request body."}, status=400)

    post_slug = data.get("post_slug", "").strip()
    body = data.get("body", "").strip()

    if not post_slug or not body:
        return JsonResponse({"error": "Post and comment body are required."}, status=400)

    if len(body) > 2000:
        return JsonResponse({"error": "Comment is too long (max 2000 characters)."}, status=400)

    post = get_object_or_404(Post, slug=post_slug, status=Post.Status.PUBLISHED)

    comment = Comment.objects.create(
        post=post,
        commenter=commenter,
        body=body,
    )

    return JsonResponse({
        "message": "Comment posted successfully.",
        "comment": {
            "id": comment.id,
            "name": commenter.name,
            "body": comment.body,
            "created_at": comment.created_at.strftime("%b %d, %Y"),
            "initial": commenter.name[0].upper() if commenter.name else "?",
        },
    })


@require_GET
def get_comments(request, slug):
    """Get paginated comments for a post (load-more style)."""
    post = get_object_or_404(Post, slug=slug, status=Post.Status.PUBLISHED)

    page = int(request.GET.get("page", 1))
    per_page = 5

    comments = Comment.objects.filter(post=post, is_approved=True).select_related("commenter")
    total = comments.count()

    start = (page - 1) * per_page
    end = start + per_page
    page_comments = comments[start:end]

    has_more = end < total

    return JsonResponse({
        "comments": [
            {
                "id": c.id,
                "name": c.commenter.name,
                "body": c.body,
                "created_at": c.created_at.strftime("%b %d, %Y"),
                "initial": c.commenter.name[0].upper() if c.commenter.name else "?",
            }
            for c in page_comments
        ],
        "has_more": has_more,
        "total": total,
        "page": page,
    })


@require_GET
def check_auth(request):
    """Check if the user has a valid commenter token cookie."""
    token = request.COOKIES.get("commenter_token")
    if not token:
        return JsonResponse({"authenticated": False})

    try:
        commenter = VerifiedCommenter.objects.get(token=token)
    except VerifiedCommenter.DoesNotExist:
        return JsonResponse({"authenticated": False})

    if commenter.is_expired:
        return JsonResponse({"authenticated": False})

    return JsonResponse({
        "authenticated": True,
        "name": commenter.name,
        "email": commenter.email,
    })
