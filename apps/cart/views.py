from itertools import product
from django.shortcuts import render
from .cart import Cart

def cart_detail(request):

    cart = Cart(request)
    productsstring = ''
    product_parts = []
    for item in cart:
        product = item['product']
        url = '/catalog/%s/%s/%s/' % (product.category.main_category.slug, product.category.slug, product.slug)
        
        if product.parts.exists:
            for pr in product.parts.all():
                product_parts.append(pr)
        # b = "{'id': '%s','title': '%s','price': '%s','quantity': '%s','total_price': '%s', 'url':'%s', 'image':'%s', 'product_parts':'%s'}," % (product.id, product.title, product.price, item['quantity'], item['total_price'],url, product.image.url, product_parts)
        b = "{'id': '%s','title': '%s','price': '%s','quantity': '%s','total_price': '%s', 'url':'%s', 'image':'%s'}," % (product.id, product.title, product.price, item['quantity'], item['total_price'],url, product.image.url)

        productsstring = productsstring + b

    context = {
        'cart': cart,
        'productsstring': productsstring,
        'product_parts': product_parts,
    }
    
    return render(request, 'cart.html', context)

def success(request):
    return render(request, 'success.html')