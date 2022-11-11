from .models import Category, Product, Brand, MainCategory
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

def menu_category(request):
    # categories = Category.objects.exclude(product__isnull=True).order_by('ordering')
    categories = Category.objects.exclude(main_category__isnull=False).exclude(product__isnull=True).order_by('ordering')
    main_categories = MainCategory.objects.filter(category__product__isnull=False).distinct().order_by('ordering')
    print(main_categories)
    context = {'menu_categories':categories, 'menu_main_categories': main_categories}
    return context

def all_products(request):
    products = Product.objects.all()

    return {'all_products':products}

def featured_product(request):
    featured_product = Product.objects.filter(is_features=True).order_by('?')[:5]
    return {'featured_product':featured_product}

def menu_brands(request):
    brands = Brand.objects.all()
    return {'menu_brands': brands}
