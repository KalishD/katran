from audioop import add
import datetime
from itertools import product
import os

from random import randint

from apps.cart.cart import Cart
from apps.order.models import Order, OrderItem

def checkout(request, name, email, phone, address):
  order = Order(name=name, email=email, phone=phone, address=address)
  print('*****************')
  print('Checkout func()')
  print('Order: ', order)
  order.save()

  cart = Cart(request)

  for item in cart:
    OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])

  return order.id