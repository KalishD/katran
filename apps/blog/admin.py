from django.contrib import admin
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html
from django import forms
from django.urls import path
from django.shortcuts import render, redirect
from slugify import slugify
import csv, codecs, os, re, operator, io, requests
from io import BytesIO
from PIL import Image
from apps.blog.models import PostCategory, Post
from apps.store.models import Category, Product, Brand, Variable, VariableItem, MainCategory
from urllib.parse import parse_qsl, urljoin, urlparse
from urllib.request import urlopen
from apps.core.utils import *
from import_export.admin import ExportActionMixin
from django_summernote.admin import SummernoteModelAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
# Register your models here.


def rename_image_file(old_path, new_path):
    if old_path and default_storage.exists(old_path) and old_path != new_path:
        if default_storage.exists(new_path):
            default_storage.delete(new_path)
        with default_storage.open(old_path, 'rb') as f:
            content = f.read()
        default_storage.save(new_path, ContentFile(content))
        default_storage.delete(old_path)
    return new_path


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


    def save_model(self, request, obj, form, change):
        # сначала сохраняем сам объект
        super().save_model(request, obj, form, change)
       

@admin.register(Post)
class PostAdmin(ExportActionMixin, SummernoteModelAdmin, admin.ModelAdmin):
    list_display = ("title","postcategory","created_at")
    search_fields = ("title__contains",)
    fields = ("postcategory","title","slug","body","image","linked_products")
    summernote_fields = ('body',)
    prepopulated_fields = {'slug': ('title',) }
    filter_horizontal = ('linked_products',)
    actions = ['rename_images', 'generate_image_variants']

    @admin.action(description='Создать _sm/_md версии изображений')
    def generate_image_variants(self, request, queryset):
        count = 0
        for obj in queryset:
            if not obj.image or obj.image.name == 'static/images/blank_prodimg.jpg':
                continue
            try:
                obj.generate_variants('image', obj.slug)
                count += 1
            except Exception as e:
                self.message_user(request, f'Ошибка для {obj.title}: {e}', level='error')
        self.message_user(request, f'Созданы варианты для {count} статей')

    @admin.action(description='Переименовать изображения по slug')
    def rename_images(self, request, queryset):
        count = 0
        for obj in queryset:
            if not obj.image or obj.image.name == 'static/images/blank_prodimg.jpg':
                continue
            old_path = obj.image.name
            new_path = f'uploads/posts/{obj.slug}.jpg'
            if old_path != new_path:
                obj.image.name = rename_image_file(old_path, new_path)
                count += 1
            if obj.thumbnail:
                old_thumb = obj.thumbnail.name
                new_thumb = f'uploads/posts/{obj.slug}_thumb.jpg'
                if old_thumb != new_thumb:
                    obj.thumbnail.name = rename_image_file(old_thumb, new_thumb)
                    count += 1
            obj.save(update_fields=['image', 'thumbnail'])
        self.message_user(request, f'Переименовано: {count} файлов')

@admin.register(PostCategory)
class PostCategoryAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ("name","posts_count")
    fields = ("name","slug")
    prepopulated_fields = {'slug': ('name',) }
    def posts_count(self, obj):
        count = Post.objects.filter(postcategory=obj).count()

        url = (
        reverse("admin:blog_post_changelist")
        + "?"
        + urlencode({"category_id": f"{obj.id}"})
        )
        return format_html('<a href={}>{} Posts</a>', url, count)

    posts_count.short_description = "Posts"
