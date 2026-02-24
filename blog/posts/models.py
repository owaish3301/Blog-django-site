from django.db import models
from django.utils import timezone

class Post(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, max_length=250)
    body = models.TextField()
    # author = models.ForeignKey(User, on_delete=models.CASCADE)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]
        indexes = [models.Index(fields=["-pulished_at"]), ]

    def __str__(self):
        return self.title
