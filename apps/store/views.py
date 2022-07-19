from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from apps.cart.cart import Cart


# def product_detail(request, category_slug, slug):
#     product = get_object_or_404(Product, slug=slug)
#     cart = Cart(request)
#     context = {'product': product}

#     return render(request, 'product_detail.html', context)

def product_detail(request, category_slug, slug):
    product = get_object_or_404(Product, slug=slug)
    # product.num_visits = product.num_visits + 1
    # product.last_visit = datetime.now()
    # product.save()

    # Add review

    # if request.method == 'POST' and request.user.is_authenticated:
    #     stars = request.POST.get('stars', 3)
    #     content = request.POST.get('content', '')

    #     review = ProductReview.objects.create(product=product, user=request.user, stars=stars, content=content)

    #     return redirect('product_detail', category_slug=category_slug, slug=slug)

    #

    # related_products = list(product.category.products.filter(parent=None).exclude(id=product.id))
    
    # if len(related_products) >= 3:
    #     related_products = random.sample(related_products, 3)

    # if product.parent:
    #     return redirect('product_detail', category_slug=category_slug, slug=product.parent.slug)

    # imagesstring = "{'thumbnail': '%s', 'image': '%s'}," % (product.thumbnail.url, product.image.url)

    # for image in product.images.all():
    #     imagesstring = imagesstring + ("{'thumbnail': '%s', 'image': '%s'}," % (image.thumbnail.url, image.image.url))

    cart = Cart(request)
    print('Cart From View')
    print(cart.__iter__)
    if cart.has_product(product.id):
        product.in_cart = True
    else:
        product.in_cart = False

    context = {
        'product': product
        # 'imagesstring': imagesstring,
        # 'related_products': related_products
    }

    return render(request, 'product_detail.html', context)







def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()

    context = {'category': category, 'products': products}

    return render(request, 'category_detail.html', context)

def catalog(request):
    categories = Category.objects.all()
    context = {'categories': categories}

    return render(request, 'catalog.html', context)