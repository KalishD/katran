from django.shortcuts import render, get_object_or_404

from .models import Post, PostCategory

# Create your views here.

def blog(request):
    posts = Post.objects.all().order_by("-created_at")
    keywords = 'Стаьи о пневматическом инструменте'
    description = ''
    context = {
            'posts': posts,
            'keywords': keywords,
            'description': description,
            }

    return render(request, 'blog.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    keywords = {post.title}
    description = {post.title}
    context = {
        'post': post,
        'keywords': keywords,
        'description': description,

    }

    return render(request, 'post_detail.html', context)
