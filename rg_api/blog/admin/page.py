"""
Page admin.
"""
from django.contrib import admin
from django import forms
from django.db import models
from mdeditor.widgets import MDEditorWidget
from ..models import Page


class PageModelForm(forms.ModelForm):
    """
    Page model form.
    """
    title = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'style': 'width: 600px'})

    class Meta:
        """
        Meta options.
        """
        model = Page
        fields = ['title', 'author', 'tag', 'body']


class PageAdmin(admin.ModelAdmin):
    """
    Page admin.
    """
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

    def get_form(self, request, obj=None, change=False, **kwargs):
        """Customize form to set default author to current user."""
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields['author'].initial = request.user
        return form
