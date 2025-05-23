from itertools import product
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Product, Category, Brand, Variable, VariableItem, MainCategory

from django.db.models import Count
from django.db.models import Avg, Max, Min, Sum

def search(request):
    query = request.GET.get('query')
    products = Product.objects.filter(Q(title__icontains = query) | Q(description__icontains = query))
    keywords = query\
                + ' со склада в СПб'
    contex = {
        'query': query,
        'products': products,
        'keywords': keywords,
    }

    return render(request, 'search.html', contex)

def product_detail(request, maincategory_slug, category_slug, slug):
    product = get_object_or_404(Product, slug=slug)
    category = product.category
    variables = product.variable_set.all()
    keywords = 'Купить '\
                + product.title\
                + (' по цене ' + str(product.price) if product.price != 0 else '')\
                + ' со склада в СПб'
    description = ''
    context = {
        'product': product, 
        'category': category, 
        'variables': variables, 
        'keywords': keywords,
        'description': description,
        }

    return render(request, 'product_detail.html', context)

def category_detail(request, maincategory_slug, slug):
    category = get_object_or_404(Category, slug=slug, main_category__slug=maincategory_slug)
    products = category.product_set.all()
    var_titles = []
    first_product_vars = category.product_set.all().annotate(count=Count('variables')).latest('count').variable_set.all()
    all_cat_vars = VariableItem.objects.filter(id__in=list(category.product_set.all().order_by('variables').values_list('variables', flat=True).distinct()))
    # display_mode = request.GET.get('display', 'grid')  # по умолчанию отображение сеткой
    keywords = 'Заказать '\
                + category.title
    description = 'Заказать ' + category.title
    context = {
        'category': category, 
        'products': products, 
        'var_titles': first_product_vars, 
        'all_cat_vars': all_cat_vars,
        'keywords': keywords,
        'description': description,
        }
    return render(request, 'category_detail.html', context)

def category_list(request, maincategory_slug, slug):
    category = get_object_or_404(Category, slug=slug)
    var_titles = []
    first_product_vars = category.product_set.all().annotate(count=Count('variables')).latest('count').variable_set.all()
    all_cat_vars = VariableItem.objects.filter(id__in=list(category.product_set.all().order_by('variables').values_list('variables', flat=True).distinct()))

    sort_field = request.GET.get('sort_field', 'title')
    sort_order = request.GET.get('sort_order', 'asc')
    if sort_field not in ['title', 'price']:
        sort_field = 'title'
    ordering = sort_field if sort_order == 'asc' else '-' + sort_field
    products = category.product_set.all().order_by(ordering)
    context = {
        'category': category, 
        'products': products, 
        'var_titles': first_product_vars, 
        'all_cat_vars': all_cat_vars,
        }
    return render(request, 'category_detail_list.html', context)

def category_grid(request, maincategory_slug, slug):
    category = get_object_or_404(Category, slug=slug)
    sort_field = request.GET.get('sort_field', 'title')
    sort_order = request.GET.get('sort_order', 'asc')
    if sort_field not in ['title', 'price']:
        sort_field = 'title'
    ordering = sort_field if sort_order == 'asc' else '-' + sort_field
    products = category.product_set.all().order_by(ordering)
    context = {
        'category': category, 
        'products': products, 
        }
    return render(request, 'category_detail_grid.html', context)

from django.views.decorators.http import require_GET

@require_GET
def category_products_api(request, main_category_slug, category_slug):
    category = get_object_or_404(Category, slug=category_slug, main_category__slug=main_category_slug)
    # all_vars = VariableItem.objects.filter(
    #     id__in=list(
    #         category.product_set.all().order_by('variables').values_list('variables', flat=True).distinct()
    #     )
    # )
    all_vars = VariableItem.objects.filter(id__in=list(category.product_set.all().order_by('variables').values_list('variables', flat=True).distinct()))
    products_qs = Product.objects.filter(category=category)

    products = []
    for p in products_qs:
        variables = {v.varitem: v.value for v in p.variable_set.all()}
        characteristics = []
        for var in all_vars:
            characteristics.append(variables.get(var, "+"))

        products.append({
            'id': p.id,
            'title': p.title,
            'price': float(p.price) if p.price else None,
            'image': p.image.url if p.image else '',
            'category': p.category.title,
            'brand': p.brand.title if p.brand else None,
            'brand_url': p.brand.get_absolute_url() if p.brand else None,
            'brand_image': p.brand.image.url if p.brand and p.brand.image else None,
            'url': p.get_absolute_url(),
            'characteristics': characteristics
        })

    return JsonResponse({'products': products})


def main_category_detail(request, slug):
    main_category = get_object_or_404(MainCategory, slug=slug)
    # sort_field = request.GET.get('sort_field', 'title')
    # sort_order = request.GET.get('sort_order', 'asc')
    # if sort_field not in ['title', 'price']:
        # sort_field = 'title'
    # ordering = sort_field if sort_order == 'asc' else '-' + sort_field
    # products = category.product_set.all().order_by(ordering)
    context = {
        'main_category': main_category, 
        # 'products': products, 
        }
    return render(request, 'main_category_detail.html', context)

def catalog(request):
    categories = Category.objects.all()
    context = {'categories': categories}

    return render(request, 'catalog.html', context)

def brand_detail(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    products = brand.products.all().order_by("category")

    context = {'brand': brand, 'products': products}

    return render(request, 'brand_detail.html', context)