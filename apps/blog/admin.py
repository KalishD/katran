from django.contrib import admin
from django.core.files import File
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


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    linked = forms.ModelMultipleChoiceField(
        queryset=Product.objects.none(),  # заполняем в __init__
        required=False,
        widget=FilteredSelectMultiple('Связанные товары', False)
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # базовый queryset — все продукты
        qs = Product.objects.filter(is_visible=True)
        
        # parts: только main_category_id в [3,4,5]
        self.fields['linked'].queryset = qs.filter(category__main_category_id__in=[1,3,4,5])

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # общий queryset только видимые продукты
        qs = Product.objects.filter(is_visible=True)

        if db_field.name == 'linked':
            # запчасти: только main_category_id в [3,4,5]
            kwargs['queryset'] = qs.filter(category__main_category_id__in=[1,3,4,5])

        return super().formfield_for_manytomany(db_field, request, **kwargs)

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
