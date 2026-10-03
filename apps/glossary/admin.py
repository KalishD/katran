from django import forms
from django.contrib import admin
from django_summernote.widgets import SummernoteWidget
from .models import GlossaryPage


class GlossaryPageAdminForm(forms.ModelForm):
    body = forms.CharField(widget=SummernoteWidget())

    class Meta:
        model = GlossaryPage
        fields = '__all__'


@admin.register(GlossaryPage)
class GlossaryPageAdmin(admin.ModelAdmin):
    form = GlossaryPageAdminForm
    list_display = ('title', 'page_type', 'ordering', 'is_visible')
    list_editable = ('ordering', 'is_visible')
    list_filter = ('page_type', 'is_visible')
    search_fields = ('title', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('related_products', 'related_categories', 'related_pages')
    fieldsets = (
        (None, {
            'fields': ('page_type', 'title', 'slug', 'category',
                       'short_description', 'body', 'faq')
        }),
        ('Связи', {
            'fields': ('related_products', 'related_categories')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
        ('Публикация', {
            'fields': ('ordering', 'is_visible')
        }),
    )