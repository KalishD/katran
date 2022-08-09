from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Brand, Variable


def product_detail(request, category_slug, slug):
    product = get_object_or_404(Product, slug=slug)
    variables = product.variable_set.all()
    context = {'product': product, 'variables': variables}

    return render(request, 'product_detail.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    var_titles = []
    first_product_vars = category.products.first().variable_set.all()
    for var in first_product_vars:
        var_titles.append(var)
    context = {'category': category, 'products': products, 'var_titles': var_titles}

    return render(request, 'category_detail.html', context)

def catalog(request):
    categories = Category.objects.all()
    context = {'categories': categories}

    return render(request, 'catalog.html', context)

def brand_detail(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    products = brand.products.all()

    context = {'brand': brand, 'products': products}

    return render(request, 'brand_detail.html', context)