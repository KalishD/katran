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
from urllib.parse import parse_qsl, urljoin, urlparse
from urllib.request import urlopen
from apps.core.utils import *
from import_export.admin import ExportActionMixin
from django_summernote.admin import SummernoteModelAdmin
# Register your models here.

@admin.register(Post)
class PostAdmin(ExportActionMixin, SummernoteModelAdmin, admin.ModelAdmin):
    list_display = ("title","postcategory","created_at")
    search_fields = ("title__contains",)
    fields = ("postcategory","title","slug","body","image")
    summernote_fields = ('body',)
    prepopulated_fields = {'slug': ('title',) }

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
