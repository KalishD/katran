from django.shortcuts import render, get_object_or_404

from .models import Post, PostCategory

# Create your views here.

def blog(request):
    posts = Post.objects.all().order_by("-created_at")
    keywords = 'Статьи о пневматическом инструменте, обзоры, характеристики, отзывы'
    description = 'Статьи о пневматическом инструменте: обзоры моделей, сравнения характеристик, советы по выбору и обслуживанию пневмоинструмента.'
    context = {
            'posts': posts,
            'keywords': keywords,
            'description': description,
            }

    return render(request, 'blog.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    keywords = post.title
    description = post.title
    context = {
        'post': post,
        'keywords': keywords,
        'description': description,

    }

    return render(request, 'post_detail.html', context)
