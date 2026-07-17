import json
from django.shortcuts import render
from .cart import Cart

def cart_detail(request):

    cart = Cart(request)
    products_data = []
    product_parts = []
    for item in cart:
        product = item['product']
        url = '/catalog/%s/%s/%s/' % (product.category.main_category.slug, product.category.slug, product.slug)

        if product.parts.exists:
            for pr in product.parts.all():
                product_parts.append(pr)
        products_data.append({
            'id': product.id,
            'title': product.title,
            'price': float(product.price),
            'quantity': item['quantity'],
            'total_price': float(item['total_price']),
            'url': url,
            'image': product.image.url if product.image else '',
        })

    context = {
        'cart': cart,
        'productsstring': json.dumps(products_data),
        'product_parts': product_parts,
    }

    return render(request, 'cart.html', context)

def success(request):
    return render(request, 'success.html')