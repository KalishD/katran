from itertools import product
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, F, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
import random
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import TrigramSimilarity

from .models import Product, Category, Brand, Variable, VariableItem, MainCategory

from django.db.models import Count
from django.db.models import Avg, Max, Min, Sum
import re

def normalize_query(q):
    # return q.lower().replace('-', '').replace(' ', '')
    return q

def search(request):
    print('\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= def search -=-=-=-=-=--=-=-=-=-=--=-=-=-=-=-=-=\n')
    raw_query = request.GET.get('query')

    if not raw_query:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'products_html'})
        return render(request, 'search.html', {'query': raw_query, 'products': [], 'keywords': ''})

    query = raw_query

    products_list = Product.objects.filter(is_visible=True).filter(
        Q(title__icontains=query, is_visible=True) |
        Q(description__icontains=query, is_visible=True) |
        Q(article__icontains=query, is_visible=True)
    ).distinct().order_by('price')

    products_count = len(products_list)
    print('\n-=-=-=-=-=-=-=-=-=   products_count not Api\n')
    print(products_list.count())
    context = {
        'query': query,
        'raw_query': raw_query,
        'products': products_list,
        'count':products_count,
        'keywords': f'{raw_query} заказ с доставкой по всей России, доставка ТК',
        'description': 'Результаты поиска на сайте katran-pnevmo.ru. ',
    }
    return render(request, 'search.html', context)

@require_GET
def search_api(request):
    print('\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= def API search -=-=-=-=-=--=-=-=-=-=--=-=-=-=-=-=-=\n')
    raw_query = request.GET.get('query')
    if not raw_query:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'products_html': '', 'pagination_html': ''})
        return render(request, 'search.html', {'query': raw_query, 'products': [], 'keywords': ''})

    query = normalize_query(raw_query)
    qs_products = Product.objects.filter(is_visible=True)

    search_terms = raw_query.split()
    q_objects = Q()

    for term in search_terms:
        q_objects |= (
            Q(title__icontains=term) |
            Q(description__icontains=term) |
            Q(article__icontains=term)
            )

    products_list = qs_products.filter(q_objects).distinct()
    products = []
    for p in products_list:
        
        products.append({
            'id': p.id,
            'title': p.title,
            'price': float(p.price) if p.price else None,
            'image': p.image.url if p.image else '',
            'category': p.category.title,
            'main_category': p.category.main_category.title,
            'category_url': p.category.get_absolute_url(),
            'main_category_url': p.category.main_category.get_absolute_url(),
            'brand': p.brand.title if p.brand else None,
            'brand_url': p.brand.get_absolute_url() if p.brand else None,
            'brand_image': p.brand.image.url if p.brand and p.brand.image else None,
            'url': p.get_absolute_url(),
            })
    products_count = len(products)
    print('\n-=-=-=-=-=-=-=-=-=   products_count\n')
    print(products_count)

    return JsonResponse({'products': products, 'count': products_count})

def catalog(request):
    categories = Category.objects.all()
    keywords = 'Заказать пневматический инструмент, каталог пневмоинструмента'
    description = 'Каталог пневмоинструмента на сайте katran-pnevmo.ru'
    context = {
        'categories': categories,
        'keywords': keywords,
        'description': description,
        }

    return render(request, 'catalog.html', context)

def main_category_detail(request, slug):
    main_category = get_object_or_404(MainCategory, slug=slug)
    categories = main_category.get_categories()
    keywords = f'Заказать {main_category.title}, купить {main_category.title}'
    description = f'Заказать {main_category.title} '
    context = {
        'main_category': main_category, 
        'categories': categories,
        'keywords': keywords,
        'description': description, 
        }
    return render(request, 'main_category_detail.html', context)






def category_detail(request, maincategory_slug, slug):
    """
    Renders the category detail page.
    This view primarily fetches the category details and passes them to the template.
    Product data is now fetched dynamically via the category_products_api.
    """
    category = get_object_or_404(Category, slug=slug, main_category__slug=maincategory_slug)
    all_cat_vars_ids = category.products.all().order_by('variables').values_list('variables', flat=True).distinct()
    all_cat_vars = VariableItem.objects.filter(id__in=list(all_cat_vars_ids))
    # These context variables might still be useful for initial rendering of category-specific headers
    # or static elements that don't change with pagination/sorting.
    # If `var_titles` and `all_cat_vars` are needed for dynamic product characteristics,
    # they should ideally be fetched and included in the JSON response of `category_products_api`
    # or handled entirely on the frontend if they are truly static for the category.
    # For now, they are commented out as they are not directly used by the Vue app's product loop.
    # var_titles = []
    # first_product_vars = category.products.all().annotate(count=Count('variables')).latest('count').variable_set.all()
    # all_cat_vars = VariableItem.objects.filter(id__in=list(category.products.all().order_by('variables').values_list('variables', flat=True).distinct()))

    keywords = f'Заказать {category.title}'
    description = f'Заказать {category.title}'

    context = {
        'category': category,
        # 'products': products, # Products are now fetched via API
        # 'var_titles': first_product_vars,
        'all_cat_vars': all_cat_vars,
        'keywords': keywords,
        'description': description,
    }
    return render(request, 'category_detail.html', context)


@require_GET
def category_products_api(request, main_category_slug, category_slug):
    """
    API endpoint to fetch products for a category with pagination and sorting.
    """
    category = get_object_or_404(Category, slug=category_slug, main_category__slug=main_category_slug)
    products_qs = Product.objects.filter(category=category, is_visible=True)

    # Get sorting parameters from request.GET
    sort_field = request.GET.get('sortField', 'is_features') # Default sort field
    sort_order = request.GET.get('sortOrder', 'asc') # Default sort order ('asc' or 'desc')

    # Apply sorting to the queryset
    if sort_field == 'is_features':
        if sort_order == 'desc':
            products_qs = products_qs.order_by(f'-{sort_field}', 'category')
        else:
            products_qs = products_qs.order_by(sort_field, 'category')
    else:
        if sort_order == 'desc':
            products_qs = products_qs.order_by(f'-{sort_field}')
        else:
            products_qs = products_qs.order_by(sort_field)
    # Get pagination parameters from request.GET
    page = request.GET.get('page', 1)
    per_page = request.GET.get('perPage', 15) # Default items per page

    # Validate and sanitize per_page
    try:
        per_page = int(per_page)
        if not (1 <= per_page <= 100): # Set a reasonable limit to prevent excessively large pages
            per_page = 15
    except ValueError:
        per_page = 15 # Fallback to default if not a valid integer

    # Initialize Paginator
    paginator = Paginator(products_qs, per_page)

    # Get the requested page
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products_page = paginator.page(paginator.num_pages)

    # Get all unique variable items for the category's products for consistent characteristics display.
    # This ensures that all products in the category display the same set of characteristic columns,
    # even if a specific product doesn't have a value for a particular variable.
    all_cat_vars_ids = category.products.all().order_by('variables').values_list('variables', flat=True).distinct()
    all_cat_vars = VariableItem.objects.filter(id__in=list(all_cat_vars_ids))

    products_data = []
    for p in products_page.object_list: # Iterate over products for the current page
        # Collect variables for the current product
        variables = {v.varitem: v.value for v in p.variable_set.all()}
        variablesitems = {v.varitem: v.varitem.title for v in p.variable_set.all()}
        variablesdimention = {v.varitem: v.varitem.dimention for v in p.variable_set.all()}

        characteristics = []
        characteristicsitems = []
        characteristicsdimention = []

        # Populate characteristics based on all_cat_vars for consistent structure
        for var in all_cat_vars:
            characteristics.append(variables.get(var)) # Get value, or None if not present
            characteristicsitems.append(variablesitems.get(var))
            characteristicsdimention.append(variablesdimention.get(var))

        products_data.append({
            'id': p.id,
            'title': p.title,
            'price': float(p.price) if p.price else None,
            'image': p.image.url if p.image else '',
            'category': p.category.title,
            'main_category': p.category.main_category.title,
            'category_url': p.category.get_absolute_url(),
            'main_category_url': p.category.main_category.get_absolute_url(),
            'brand': p.brand.title if p.brand else None,
            'brand_url': p.brand.get_absolute_url() if p.brand else None,
            'brand_image': p.brand.image.url if p.brand and p.brand.image else None,
            'url': p.get_absolute_url(),
            'characteristics': characteristics,
            'characteristicsitems': characteristicsitems,
            'characteristicsdimention': characteristicsdimention,
            'is_features': p.is_features,
            'sku': p.sku,
            'in_stock': p.in_stock,
        })

    return JsonResponse({
        'products': products_data,
        'currentPage': products_page.number,
        'totalPages': paginator.num_pages,
        'totalProducts': paginator.count,
    })

def product_detail(request, maincategory_slug, category_slug, slug):
    product = get_object_or_404(Product, slug=slug)
    category = product.category
    variables = product.variable_set.all().order_by('-varitem__is_primary')
    variables_list = ''
    for var in variables:
        if var.varitem.is_primary:
            variables_list += var.value + (var.varitem.dimention if var.varitem.dimention else '') + '; '
    cln_title = re.sub(r'\s*\([^()]*\)$', '', product.title)
    keywords = 'купить '\
                + cln_title\
                + ', '\
                + str(product.keywords)
    
    meta_description = f'{cln_title} {product.brand} с доставкой по всей России; {variables_list}'
    # Создание и передача объекта meta в контекст
    meta = product.as_meta(request)

    context = {
        'cln_title': cln_title,
        'variables_list': variables_list,
        'product': product, 
        'category': category, 
        'variables': variables, 
        'keywords': keywords,
        'description': meta_description,
        'meta': meta,
        }

    return render(request, 'product_detail.html', context)





def brands(request):
    brand_items = []
    keywords = 'Каталог производителей пневмоинструмент'
    description = 'Каталог производителей пневмоинструмент'
    for brand in Brand.objects.all().order_by('ordering'):
        # берем только видимые товары
        prods = list(brand.products.filter(is_visible=True, category__main_category__in = range(1,2)))
        random.shuffle(prods)
        # первые 5 «рандомных»
        random_five = prods[:5]
        brand_items.append({
            'brand': brand,
            'products': random_five
        })
        context = {
            'brand_items': brand_items,
            'keywords': keywords,
            'description': description,
        }
    return render(request, 'brands.html', context)

def brand_detail(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    products = brand.products.filter(is_visible=True).order_by("is_features")
    keywords = f'Заказать пневмоинструмент фирмы {brand.title}, купить {brand.title}, заказать {brand.title}, пневмоинструмент {brand.title}'
    description = f'Заказать пневмоинструмент фирмы {brand.title} с доставкой по всей России'
    all_brand_vars = VariableItem.objects.filter(id__in=list(brand.products.all().order_by('variables').values_list('variables', flat=True).distinct()))
    context = {
        'brand': brand,
        'products': products,
        'keywords': keywords,
        'description': description,
        'all_brand_vars': all_brand_vars,
    }

    return render(request, 'brand_detail.html', context)


@require_GET
def brand_products_api(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    """
    API endpoint to fetch products for a category with pagination and sorting.
    """
    products_qs = Product.objects.filter(brand=brand, is_visible=True)

    # Get sorting parameters from request.GET
    sort_field = request.GET.get('sortField', 'category__ordering') # Default sort field
    sort_order = request.GET.get('sortOrder', 'asc') # Default sort order ('asc' or 'desc')

    # Apply sorting to the queryset
    if sort_order == 'desc':
        products_qs = products_qs.order_by(f'-{sort_field}')
    else:
        products_qs = products_qs.order_by(sort_field)

    # Get pagination parameters from request.GET
    page = request.GET.get('page', 1)
    per_page = request.GET.get('perPage', 20) # Default items per page

    # Validate and sanitize per_page
    try:
        per_page = int(per_page)
        if not (1 <= per_page <= 100): # Set a reasonable limit to prevent excessively large pages
            per_page = 20
    except ValueError:
        per_page = 20 # Fallback to default if not a valid integer

    # Initialize Paginator
    paginator = Paginator(products_qs, per_page)

    # Get the requested page
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products_page = paginator.page(paginator.num_pages)

    # Get all unique variable items for the category's products for consistent characteristics display.
    # This ensures that all products in the category display the same set of characteristic columns,
    # even if a specific product doesn't have a value for a particular variable.
    all_brand_vars_ids = brand.products.all().order_by('variables').values_list('variables', flat=True).distinct()
    all_brand_vars = VariableItem.objects.filter(id__in=list(all_brand_vars_ids))

    products_data = []
    for p in products_page.object_list: # Iterate over products for the current page
        # Collect variables for the current product
        variables = {v.varitem: v.value for v in p.variable_set.all()}
        variablesitems = {v.varitem: v.varitem.title for v in p.variable_set.all()}
        variablesdimention = {v.varitem: v.varitem.dimention for v in p.variable_set.all()}

        characteristics = []
        characteristicsitems = []
        characteristicsdimention = []

        # Populate characteristics based on all_brand_vars for consistent structure
        for var in all_brand_vars:
            characteristics.append(variables.get(var)) # Get value, or None if not present
            characteristicsitems.append(variablesitems.get(var))
            characteristicsdimention.append(variablesdimention.get(var))

        products_data.append({
            'id': p.id,
            'title': p.title,
            'price': float(p.price) if p.price else None,
            'image': p.image.url if p.image else '',
            'category': p.category.title,
            'main_category': p.category.main_category.title,
            'category_url': p.category.get_absolute_url(),
            'main_category_url': p.category.main_category.get_absolute_url(),
            'brand': p.brand.title if p.brand else None,
            'brand_url': p.brand.get_absolute_url() if p.brand else None,
            'brand_image': p.brand.image.url if p.brand and p.brand.image else None,
            'url': p.get_absolute_url(),
            'characteristics': characteristics,
            'characteristicsitems': characteristicsitems,
            'characteristicsdimention': characteristicsdimention,
            'is_features': p.is_features,
            'sku': p.sku,
            'in_stock': p.in_stock,
        })

    return JsonResponse({
        'products': products_data,
        'currentPage': products_page.number,
        'totalPages': paginator.num_pages,
        'totalProducts': paginator.count,
    })