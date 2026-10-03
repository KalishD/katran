from django.contrib import admin
from .models import Industry, CaseStudy


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('title', 'ordering', 'is_visible')
    list_editable = ('ordering', 'is_visible')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'short_description')
    filter_horizontal = ('related_categories',)


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'industry', 'client_name', 'ordering', 'is_visible')
    list_editable = ('ordering', 'is_visible')
    list_filter = ('industry',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'client_name', 'problem', 'solution')
    filter_horizontal = ('related_products',)
