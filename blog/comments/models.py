import secrets
from django.db import models
from django.utils import timezone
from datetime import timedelta


class VerifiedCommenter(models.Model):
    """
    Stores verified commenters with a token that expires in ~30 days.
    The token is saved as a cookie so returning visitors don't need to re-verify.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.email})"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(48)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at


class EmailOTP(models.Model):
    """
    Temporary OTP record for email verification.
    OTPs expire after 10 minutes.
    """
    email = models.EmailField()
    name = models.CharField(max_length=100)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP for {self.email}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at


class Comment(models.Model):
    """
    A comment on a blog post, linked to a verified commenter.
    """
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    commenter = models.ForeignKey(
        VerifiedCommenter,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    body = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["post", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.commenter.name} on {self.post.title[:30]}"
