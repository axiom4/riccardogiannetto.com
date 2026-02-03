from django.contrib import admin
from django import forms
from django.db import models
from mdeditor.widgets import MDEditorWidget
from ..models import Page


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
