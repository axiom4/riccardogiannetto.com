from django.contrib import admin

from blog.models import Page, Post, Category, ImageUpload, Comment

from django.db import models
from mdeditor.widgets import MDEditorWidget

from django import forms


class ImageInline(admin.TabularInline):
    model = ImageUpload
    readonly_fields = ['image_tag']
    extra = 0


class CommentInline(admin.TabularInline):
    model = Comment
    readonly_fields = ['text', 'mail', 'created_at', 'ip']
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class PageModelForm(forms.ModelForm):
    title = forms.CharField()
    title.widget.attrs.update({'style': 'width: 600px'})

    class Meta:
        model = Page
        fields = ['title', 'author', 'tag', 'body']


class PageAdmin(admin.ModelAdmin):
    fields = [
        ('title'),
        ('author', 'tag'),
        'body'
    ]
    list_display = ('title', 'tag', 'author', 'created_at')
    save_on_top = True
    search_fields = ['title',]
    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget},
    }

    form = PageModelForm

    def get_form(self, request, obj=None, **kwargs):
        form = super(PageAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['author'].initial = request.user
        return form


class PostModelForm(forms.ModelForm):
    title = forms.CharField()
    title.widget.attrs.update({'style': 'width: 600px'})

    summary = forms.CharField(widget=forms.Textarea())
    summary.widget.attrs.update({'style': 'width: 600px; resize: none'})

    class Meta:
        model = Post
        fields = ['title', 'author', 'summary', 'categories', 'body', 'image']


class CommentAdmin(admin.ModelAdmin):
    fields = [('mail', 'post'), 'text']
    list_display = ('mail', 'post', 'text', 'created_at')
    list_filter = ('post__title', 'mail')
    search_fields = ('mail', 'post')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


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


class CategoryAdmin(admin.ModelAdmin):
    fields = ['name']


class ImageAdmin(admin.ModelAdmin):
    fields = [('title', 'short_name'),
              ('image', 'image_tag'), ('post', 'author')]
    list_display = ('title', 'short_name', 'post', 'image_tag')
    list_filter = ('post__title',)
    search_fields = ('title', 'short_name', 'post__title')
    save_on_top = False
    list_display_links = ('title',)
    readonly_fields = ['image_tag']

    def get_form(self, request, obj=None, **kwargs):
        form = super(ImageAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['author'].initial = request.user
        return form


admin.site.register(ImageUpload, ImageAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
