from .cart import Cart

def cart(request):
  cart = Cart(request)
  print('!!!!!!!!!!!!!!!!!!')
  print('Cart CP __ cart: ', cart.cart.values())
  return {'cart': Cart(request)}