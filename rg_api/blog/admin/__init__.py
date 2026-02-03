"""
Admin configuration for blog app.
"""
from django.contrib import admin
from ..models import Page, Post, Category, ImageUpload, Comment
from .page import PageAdmin
from .post import PostAdmin
from .category import CategoryAdmin
from .comment import CommentAdmin
from .image import ImageAdmin

admin.site.register(Page, PageAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ImageUpload, ImageAdmin)
