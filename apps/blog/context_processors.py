from .models import Post, PostCategory
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
import math


def all_posts(request):
    posts = Post.objects.all()

    return {'all_posts':posts}