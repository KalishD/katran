from itertools import product
from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import Product, Category, Brand, Variable, VariableItem

from django.db.models import Count
from django.db.models import Avg, Max, Min, Sum

def search(request):
    query = request.GET.get('query')
    products = Product.objects.filter(Q(title__icontains = query) | Q(description__icontains = query))

    contex = {
        'query': query,
        'products': products
    }

    return render(request, 'search.html', contex)

def product_detail(request, category_slug, slug):
    product = get_object_or_404(Product, slug=slug)
    variables = product.variable_set.all()
    context = {'product': product, 'variables': variables}

    return render(request, 'product_detail.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.product_set.all()
    var_titles = []
    first_product_vars = category.product_set.all().annotate(count=Count('variables')).latest('count').variable_set.all()
    all_cat_vars = VariableItem.objects.filter(id__in=list(category.product_set.all().order_by('variables').values_list('variables', flat=True).distinct()))

    context = {'category': category, 'products': products, 'var_titles': first_product_vars, 'all_cat_vars': all_cat_vars}

    return render(request, 'category_detail.html', context)

def catalog(request):
    categories = Category.objects.all()
    context = {'categories': categories}

    return render(request, 'catalog.html', context)

def brand_detail(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    products = brand.products.all().order_by("category")

    context = {'brand': brand, 'products': products}

    return render(request, 'brand_detail.html', context)