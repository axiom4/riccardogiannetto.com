"""
Post admin.
"""
from django.contrib import admin
from django import forms
from django.db import models
from mdeditor.widgets import MDEditorWidget
from ..models import Post
from .image import ImageInline
from .comment import CommentInline


class PostModelForm(forms.ModelForm):
    """
    Post model form with custom widgets.
    """
    title = forms.CharField()
    summary = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'style': 'width: 600px'})
        self.fields['summary'].widget.attrs.update({'style': 'width: 600px; resize: none'})

    class Meta:
        """
        Meta options.
        """
        model = Post
        fields = ['title', 'author', 'summary', 'categories', 'body', 'image']


class PostAdmin(admin.ModelAdmin):
    """
    Post admin.
    """
    save_on_top = True
    fields = [
        ('title', 'author', 'image', 'image_tag'),
        ('summary', 'categories'),
        'body'
    ]

    list_display = ('title', 'summary', 'image', 'image_tag', 'author')
    search_fields = ['title', 'summary']
    inlines = [ImageInline, CommentInline]
    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget}
    }
    readonly_fields = ['image_tag']
    form = PostModelForm

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields['author'].initial = request.user

        return form
