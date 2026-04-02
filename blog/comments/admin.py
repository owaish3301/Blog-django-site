from django.contrib import admin
from .models import Comment, VerifiedCommenter, EmailOTP


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("commenter", "post", "created_at", "is_approved")
    list_filter = ("is_approved", "created_at")
    search_fields = ("commenter__name", "commenter__email", "body")
    raw_id_fields = ("post", "commenter")
    actions = ["approve_comments", "disapprove_comments"]

    @admin.action(description="Approve selected comments")
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Disapprove selected comments")
    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)


@admin.register(VerifiedCommenter)
class VerifiedCommenterAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at", "expires_at")
    search_fields = ("name", "email")
    readonly_fields = ("token",)


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ("email", "otp", "created_at", "expires_at", "is_used")
    list_filter = ("is_used",)
    search_fields = ("email",)
