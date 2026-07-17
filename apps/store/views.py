from django.shortcuts import render, get_object_or_404
from django.db.models import Q, F, Value
from django.db.models.functions import Coalesce, Lower
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_page, never_cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import TrigramSimilarity

from .models import Product, Category, Brand, Variable, VariableItem, MainCategory, Patent

from django.db.models import Count
from django.db.models import Avg, Max, Min, Sum
import re

def normalize_query(q):
    # return q.lower().replace('-', '').replace(' ', '')
    return q

@never_cache
def search(request):
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
    ).select_related('brand', 'category__main_category').distinct().order_by('price')

    products_count = len(products_list)
    context = {
        'query': query,
        'raw_query': raw_query,
        'products': products_list,
        'count':products_count,
        'keywords': f'{raw_query} заказ с доставкой по всей России, доставка ТК',
        'description': 'Результаты поиска на сайте katran-pnevmo.ru. ',
    }
    return render(request, 'search.html', context)

@never_cache
@require_GET
def search_api(request):
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

    products_list = qs_products.filter(q_objects).distinct().select_related('brand', 'category__main_category')
    products = []
    for p in products_list:
        
        products.append({
            'id': p.id,
            'title': p.title,
            'price': float(p.price) if p.price else None,
            'image': p.image.url if p.image else '',
            'image_sm': p.get_resized_url('image', 'sm') if p.image else '',
            'image_md': p.get_resized_url('image', 'md') if p.image else '',
            'image_sm': p.get_resized_url('image', 'sm') if p.image else '',
            'image_md': p.get_resized_url('image', 'md') if p.image else '',
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

    return JsonResponse({'products': products, 'count': products_count})

@cache_page(60 * 30)  # 30 minutes
def catalog(request):
    categories = Category.objects.select_related('main_category').all()
    keywords = 'Заказать пневматический инструмент, каталог пневмоинструмента'
    description = 'Каталог пневмоинструмента на сайте katran-pnevmo.ru'
    context = {
        'categories': categories,
        'keywords': keywords,
        'description': description,
        }

    return render(request, 'catalog.html', context)

@cache_page(60 * 30)  # 30 minutes
def main_category_detail(request, slug):
    main_category = get_object_or_404(MainCategory, slug=slug)
    categories = main_category.get_categories().select_related('main_category')
    keywords = f'Заказать {main_category.title}, купить {main_category.title}'
    description = f'Заказать {main_category.title} '
    context = {
        'main_category': main_category, 
        'categories': categories,
        'keywords': keywords,
        'description': description, 
        }
    return render(request, 'main_category_detail.html', context)






@cache_page(60 * 15)  # 15 minutes
def category_detail(request, maincategory_slug, slug):
    """
    Renders the category detail page.
    This view primarily fetches the category details and passes them to the template.
    Product data is now fetched dynamically via the category_products_api.
    """
    category = get_object_or_404(Category, slug=slug, main_category__slug=maincategory_slug)

    # Optimized: fetch variable IDs with a single query instead of loading all products
    from django.db.models import Subquery, OuterRef
    all_cat_vars_ids = Variable.objects.filter(
        product__category=category
    ).values('varitem_id').distinct().values_list('varitem_id', flat=True)
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


ALLOWED_SORT_FIELDS_CATEGORY = {'is_features', 'title', 'price', 'price_wo_tax', 'sku', 'ordering', 'created_at'}

@never_cache
@require_GET
def category_products_api(request, main_category_slug, category_slug):
    """
    API endpoint to fetch products for a category with pagination and sorting.
    """
    category = get_object_or_404(Category, slug=category_slug, main_category__slug=main_category_slug)
    products_qs = Product.objects.filter(category=category, is_visible=True).select_related('brand', 'category__main_category').prefetch_related('variable_set__varitem')

    sort_field = request.GET.get('sortField', 'is_features')
    sort_order = request.GET.get('sortOrder', 'asc')

    if sort_field not in ALLOWED_SORT_FIELDS_CATEGORY:
        sort_field = 'is_features'

    if sort_order == 'desc':
        products_qs = products_qs.order_by(f'-{sort_field}', 'category')
    else:
        products_qs = products_qs.order_by(sort_field, 'category')
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
    # Use the same optimized query as category_detail
    all_cat_vars_ids = Variable.objects.filter(
        product__category=category
    ).values('varitem_id').distinct().values_list('varitem_id', flat=True)
    all_cat_vars = VariableItem.objects.filter(id__in=list(all_cat_vars_ids))

    products_data = []
    for p in products_page.object_list: # Iterate over products for the current page
        # Collect variables for the current product — single iteration, not triple
        variables = {}
        for v in p.variable_set.all():
            variables[v.varitem] = {
                'value': v.value,
                'title': v.varitem.title,
                'dimention': v.varitem.dimention,
            }

        characteristics = []
        characteristicsitems = []
        characteristicsdimention = []

        # Populate characteristics based on all_cat_vars for consistent structure
        for var in all_cat_vars:
            var_data = variables.get(var)
            characteristics.append(var_data['value'] if var_data else None)
            characteristicsitems.append(var_data['title'] if var_data else None)
            characteristicsdimention.append(var_data['dimention'] if var_data else None)

        products_data.append({
            'id': p.id,
            'title': p.title,
            'price': float(p.price) if p.price else None,
            'image': p.image.url if p.image else '',
            'image_sm': p.get_resized_url('image', 'sm') if p.image else '',
            'image_md': p.get_resized_url('image', 'md') if p.image else '',
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

@cache_page(60 * 30)  # 30 minutes
def product_detail(request, maincategory_slug, category_slug, slug):
    product = get_object_or_404(
        Product.objects.select_related(
            'category__main_category', 'brand', 'analog', 'analog__brand', 'analog__category__main_category'
        ).prefetch_related(
            'variable_set__varitem', 'faqs', 'parts', 'similar_products'
        ),
        slug=slug
    )
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





@cache_page(60 * 30)  # 30 minutes
def brands(request):
    keywords = 'Каталог производителей пневмоинструмент'
    description = 'Каталог производителей пневмоинструмент'

    brands_qs = Brand.objects.all().order_by('ordering')
    all_products = Product.objects.filter(
        is_visible=True,
        category__main_category__in=range(1, 2)
    ).select_related('brand', 'category__main_category').order_by('?')

    brand_product_map = {}
    for p in all_products:
        if p.brand_id not in brand_product_map:
            brand_product_map[p.brand_id] = []
        if len(brand_product_map[p.brand_id]) < 5:
            brand_product_map[p.brand_id].append(p)

    brand_items = []
    for brand in brands_qs:
        brand_items.append({
            'brand': brand,
            'products': brand_product_map.get(brand.id, [])
        })

    context = {
        'brand_items': brand_items,
        'keywords': keywords,
        'description': description,
    }
    return render(request, 'brands.html', context)

@cache_page(60 * 30)  # 30 minutes
def brand_detail(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    products = brand.products.filter(is_visible=True).select_related(
        'category__main_category'
    ).order_by("is_features")
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


ALLOWED_SORT_FIELDS_BRAND = {'category__ordering', 'title', 'price', 'price_wo_tax', 'sku', 'ordering', 'created_at'}

@never_cache
@require_GET
def brand_products_api(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    """
    API endpoint to fetch products for a category with pagination and sorting.
    """
    products_qs = Product.objects.filter(brand=brand, is_visible=True).select_related('brand', 'category__main_category').prefetch_related('variable_set__varitem')

    sort_field = request.GET.get('sortField', 'category__ordering')
    sort_order = request.GET.get('sortOrder', 'asc')

    if sort_field not in ALLOWED_SORT_FIELDS_BRAND:
        sort_field = 'category__ordering'

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

    # Get all unique variable items for the brand's products for consistent characteristics display.
    all_brand_vars_ids = Variable.objects.filter(
        product__brand=brand
    ).values('varitem_id').distinct().values_list('varitem_id', flat=True)
    all_brand_vars = VariableItem.objects.filter(id__in=list(all_brand_vars_ids))

    products_data = []
    for p in products_page.object_list: # Iterate over products for the current page
        # Collect variables for the current product — single iteration, not triple
        variables = {}
        for v in p.variable_set.all():
            variables[v.varitem] = {
                'value': v.value,
                'title': v.varitem.title,
                'dimention': v.varitem.dimention,
            }

        characteristics = []
        characteristicsitems = []
        characteristicsdimention = []

        # Populate characteristics based on all_brand_vars for consistent structure
        for var in all_brand_vars:
            var_data = variables.get(var)
            characteristics.append(var_data['value'] if var_data else None)
            characteristicsitems.append(var_data['title'] if var_data else None)
            characteristicsdimention.append(var_data['dimention'] if var_data else None)

        products_data.append({
            'id': p.id,
            'title': p.title,
            'price': float(p.price) if p.price else None,
            'image': p.image.url if p.image else '',
            'image_sm': p.get_resized_url('image', 'sm') if p.image else '',
            'image_md': p.get_resized_url('image', 'md') if p.image else '',
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