from django.contrib import admin
from .models import Post, SavedPost, CommentPost
# Register your models here.

admin.site.register(Post)
admin.site.register(SavedPost)
admin.site.register(CommentPost)