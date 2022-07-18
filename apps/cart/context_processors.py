from .cart import Cart

def cart(request):
    print('Return Cart:')
    
    cart = Cart(request)
    print('cart', cart)
    print('cart.keys()', cart.cart)
    return {'cart': cart}