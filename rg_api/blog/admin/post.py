from django.contrib import admin
from django import forms
from django.db import models
from mdeditor.widgets import MDEditorWidget
from ..models import Post
from .image import ImageInline
from .comment import CommentInline


class PostModelForm(forms.ModelForm):
    title = forms.CharField()
    title.widget.attrs.update({'style': 'width: 600px'})

    summary = forms.CharField(widget=forms.Textarea())
    summary.widget.attrs.update({'style': 'width: 600px; resize: none'})

    class Meta:
        model = Post
        fields = ['title', 'author', 'summary', 'categories', 'body', 'image']


class PostAdmin(admin.ModelAdmin):
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

    def get_form(self, request, obj=None, **kwargs):
        form = super(PostAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['author'].initial = request.user

        return form
