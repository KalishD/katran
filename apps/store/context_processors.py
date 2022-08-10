from .models import Category, Product, Brand
from django.shortcuts import get_object_or_404


def menu_category(request):
    categories = Category.objects.all()

    return {'menu_categories':categories}

def all_products(request):
    products = Product.objects.all()

    return {'all_products':products}

def featured_product(request):
    featured_product = Product.objects.filter(is_features=True).order_by('?')[:5]
    return {'featured_product':featured_product}

def menu_brands(request):
    brands = Brand.objects.all()
    return {'menu_brands': brands}
