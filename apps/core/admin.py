from django.contrib import admin
from django.contrib.sites.models import Site

class CustomSiteAdmin(admin.ModelAdmin):
    list_display = ('domain', 'name')
    # Добавьте любые другие настройки админки, если нужно