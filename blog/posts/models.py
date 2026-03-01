from django.db import models
from django.utils import timezone
from django.conf import settings


class Post(models.Model):
    # enum for status
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PU', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, max_length=250)
    description = models.CharField(max_length=250, default=None, null=True)
    body = models.TextField()
    category = models.CharField(max_length=10, default=None, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'blog_posts')
    published_at = models.DateTimeField(default=timezone.now, )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices = Status, default = Status.DRAFT)



    class Meta:
        ordering = ["-published_at"]
        indexes = [models.Index(fields=["-published_at"]), ]


    def __str__(self):
        return self.title

    def read_time(self):
        words = len(self.body.split())
        minutes = round(words / 100)  # 200 words per minute
        return max(1, minutes)  # minimum 1 minute