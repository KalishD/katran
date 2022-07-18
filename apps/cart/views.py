from django.shortcuts import render
from .cart import Cart

# def cart_detail(request):
#     cart = Cart(request)

#     context = {
#         'cart': cart
#     }

#     return render(request, 'cart.html', context)

def cart_detail(request):
    cart = Cart(request)
    productsstring = ''
    
    for item in cart:
        product = item['product']
        # url = '/%s/%s/' % (product.category.slug, product.slug)
        print(item['total_price'])
        b = "{'id': '%s', 'title': '%s', 'price': '%s', 'quantity': '%s', 'total_price': '%s'}," % (product.id, product.title, product.price, int(item['quantity']), item['total_price'])
        # b = "{'id': '%s', 'title': '%s', 'price': '%s', 'quantity': '%s', 'total_price': '%s', 'thumbnail': '%s', 'url': '%s'}," % (product.id, product.title, product.price, item['quantity'], item['total_price'], product.get_thumbnail, url)
        productsstring = productsstring + b
    
    context = {
        'cart': cart,
        'productsstring': productsstring
        }
    
    return render(request, 'cart.html', context)
