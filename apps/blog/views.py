from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page

from .models import Post, PostCategory

# Create your views here.

@cache_page(60 * 30)  # 30 minutes
def blog(request):
    posts = Post.objects.select_related('postcategory').order_by("-created_at")
    keywords = 'Статьи о пневматическом инструменте, обзоры, характеристики, отзывы'
    description = 'Статьи о пневматическом инструменте: обзоры моделей, сравнения характеристик, советы по выбору и обслуживанию пневмоинструмента.'
    context = {
            'posts': posts,
            'keywords': keywords,
            'description': description,
            }

    return render(request, 'blog.html', context)

@cache_page(60 * 60)  # 1 hour
def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.select_related('postcategory').prefetch_related(
            'linked_products__category__main_category', 'linked_products__brand'
        ),
        slug=slug
    )
    keywords = post.title
    description = post.title
    context = {
        'post': post,
        'keywords': keywords,
        'description': description,

    }

    return render(request, 'post_detail.html', context)
