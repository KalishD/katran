from .models import Category, Product, Brand, MainCategory
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.core.cache import cache
import math

def menu_category(request):

    visible_cats = Category.objects.filter(products__is_visible=True)
    invisible_cats = (
        Category.objects
        .exclude(products__is_visible=False)
        .filter(products__isnull=False)
    )
    empty_cats = Category.objects.filter(products__isnull=True)

    categories = (visible_cats | invisible_cats | empty_cats).distinct().order_by('ordering', '-id')

    main_categories = MainCategory.objects.filter(category__in=categories).distinct()
    total_items = len(categories)
    items_per_column = math.ceil(total_items / 4)
    side_items_per_column = math.ceil(total_items / 4)
    return {
        'menu_categories_filter': categories,
        'menu_main_categories': main_categories,
        'items_per_column': items_per_column,
        'side_items_per_column': side_items_per_column,
    }


def all_products(request):
    cache_key = 'all_products_ids'
    product_ids = cache.get(cache_key)
    if product_ids is None:
        product_ids = list(Product.objects.filter(is_visible=True).values_list('id', flat=True))
        cache.set(cache_key, product_ids, 300)
    products = Product.objects.filter(id__in=product_ids)
    return {'all_products': products}

def featured_product(request):
    cache_key = 'featured_product_ids'
    product_ids = cache.get(cache_key)
    if product_ids is None:
        product_ids = list(
            Product.objects.filter(is_features=True, is_visible=True)
            .order_by('?')[:3].values_list('id', flat=True)
        )
        cache.set(cache_key, product_ids, 600)
    featured_product = Product.objects.filter(id__in=product_ids).select_related('brand', 'category__main_category')
    return {'featured_product': featured_product}

def featured_product_success(request):
    cache_key = 'featured_product_success_ids'
    product_ids = cache.get(cache_key)
    if product_ids is None:
        product_ids = list(
            Product.objects.filter(is_features=True, is_visible=True)
            .order_by('?')[:11].values_list('id', flat=True)
        )
        cache.set(cache_key, product_ids, 600)
    featured_product_success = Product.objects.filter(id__in=product_ids).select_related('brand', 'category__main_category')
    return {'featured_product_success': featured_product_success}

def menu_brands(request):
    brands = Brand.objects.filter(is_on=True).exclude(products__isnull=True).order_by('ordering','title')
    return {'menu_brands': brands}


def featured_categories(request):
    featuredcategories = Category.objects.filter(is_features=True).order_by('ordering')
    return {'featured_categories': featuredcategories}

def bestsellers_product(request):
    cache_key = 'bestsellers_product_ids'
    product_ids = cache.get(cache_key)
    if product_ids is None:
        product_ids = list(
            Product.objects.filter(is_bestseller=True, is_visible=True)
            .order_by('?').values_list('id', flat=True)
        )
        cache.set(cache_key, product_ids, 600)
    bestsellers_product = Product.objects.filter(id__in=product_ids).select_related('brand', 'category__main_category')
    return {'bestsellers_product': bestsellers_product}