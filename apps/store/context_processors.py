from .models import Category, Product
from django.shortcuts import get_object_or_404


def menu_category(request):
    categories = Category.objects.all()

    return {'menu_categories':categories}

def all_products(request):
    products = Product.objects.all()

    return {'all_products':products}

def featured_product(request):
    featured_product = Product.objects.filter(is_features=True)
    return {'featured_product':featured_product}
