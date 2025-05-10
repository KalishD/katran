from itertools import product
from django.shortcuts import render, get_object_or_404
from django.db.models import Q  

from .models import Post, PostCategory

from django.db.models import Count
from django.db.models import Avg, Max, Min, Sum

# Create your views here.

def blog(request):
    posts = Post.objects.all().order_by("-created_at")
    context = {'posts': posts}

    return render(request, 'blog.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    context = {'post': post}

    return render(request, 'post_detail.html', context)
