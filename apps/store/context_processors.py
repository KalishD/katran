from .models import Category, Product, Brand
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

def menu_category(request):
    # categories = Category.objects.all()
    # sellers = Seller.objects.prefetch_related(
    # Prefetch('genre_set', 
    #          queryset=Genre.objects.exclude(pk__in=[x.genre.pk for x in Book.objects.all()])
    # ))
    categories = Category.objects.prefetch_related(
        Prefetch(
            'products',
            queryset=Product.objects.filter(pk__in=[x.pk for x in Product.objects.all()])
        )
    )
    # for category in categories:
    #     products = category.products.all()
    #     print('Products: ', products)
    print('Categories: ',categories)
    for cat in categories:
        print(cat.products.count())
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
