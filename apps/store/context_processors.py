from .models import Category, Product, Brand, MainCategory
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

def menu_category(request):
    categories = Category.objects.exclude(product__isnull=True).order_by('-id')
    # categories = Category.objects.exclude(main_category__isnull=False).exclude(product__isnull=True).order_by('ordering')
    main_categories = MainCategory.objects.filter(category__product__isnull=False).distinct()
    context = {'menu_categories':categories, 'menu_main_categories': main_categories}
    return context

def all_products(request):
    products = Product.objects.all()

    return {'all_products':products}

def featured_product(request):
    featured_product = Product.objects.filter(is_features=True).order_by('?')[:5]
    return {'featured_product':featured_product}

def featured_product_success(request):
    featured_product_success = Product.objects.filter(is_features=True).order_by('?')[:11]
    return {'featured_product_success':featured_product_success}

def menu_brands(request):
    brands = Brand.objects.all()
    return {'menu_brands': brands}


def featured_cetegories(request):
    featuredcategories = Category.objects.filter(is_features = 1).order_by('-ordering')
    return {'featured_cetegories':featuredcategories}
