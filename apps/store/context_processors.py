from .models import Category, Product, Brand, MainCategory
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
import math

def menu_category(request):

    visible_cats = Category.objects.filter(products__is_visible=True)
    # 2) Категории, где есть товары, но ни один не видимый
    invisible_cats = (
        Category.objects
        .exclude(products__is_visible=False)
        .filter(products__isnull=False)
    )
    # 3) Категории без товаров совсем
    empty_cats = Category.objects.filter(products__isnull=True)

    # Объединяем все три набора и убираем дубликаты
    categories = (visible_cats | invisible_cats | empty_cats).distinct().order_by('ordering', '-id')

    # Основные категории — только те, в которых есть связанные категории из списка выше
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
    products = Product.objects.all()

    return {'all_products':products}

def featured_product(request):
    featured_product = Product.objects.filter(is_features=True, is_visible=True).order_by('?')[:3]
    return {'featured_product':featured_product}

def featured_product_success(request):
    featured_product_success = Product.objects.filter(is_features=True, is_visible=True).order_by('?')[:11]
    return {'featured_product_success':featured_product_success}

def menu_brands(request):
    brands = Brand.objects.filter(is_on=True).exclude(products__isnull=True).order_by('ordering','title')
    return {'menu_brands': brands}


def featured_categories(request):

    featuredcategories = Category.objects.filter(is_features = True).order_by('ordering')
    return {'featured_categories':featuredcategories}

def bestsellers_product(request):
    bestsellers_product = Product.objects.filter(is_bestseller=True, is_visible=True).order_by('?')
    return {'bestsellers_product':bestsellers_product}