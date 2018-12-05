from django.contrib import admin
from .models import Comment
# Register your models here.


class CommentModelAdmin(admin.ModelAdmin):
    list_display = ["user", "content", "parent", "pk", "is_parent", "timestamp", "content_type", "content_object"]

    class Meta:
        model = Comment


admin.site.register(Comment, CommentModelAdmin)
