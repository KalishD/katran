import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from apps.cart.cart import Cart

from .models import Product

from apps.order.utils import checkout
from apps.order.models import Order, OrderItem

def api_add_to_cart(request):
  jsonresponse = {'success': True}
  data = json.loads(request.body)
  product_id = data['product_id']
  update = data['update']
  quantity = data['quantity']
  cart = Cart(request)

  product = get_object_or_404(Product, pk=product_id)

  if not update:
    cart.add(product=product, quantity=1, update_quantity=False)
  else:
    cart.add(product=product, quantity=quantity, update_quantity=True)

  return JsonResponse(jsonresponse)

def api_remove_from_cart(request):
  data = json.loads(request.body)
  jsonresponse = {'success': True}
  
  product_id = str(data['product_id'])

  cart = Cart(request)
  cart.remove(product_id)

  return JsonResponse(jsonresponse)

def api_checkout(request):
  cart = Cart(request)
  data = json.loads(request.body)
  jsonresponse = {'success': True}
  name = data['name']
  email = data['email']
  phone = data['phone']
  address = data['address']

  orderid = checkout(request, name, email, phone, address)

  paid = True

  if paid == True:
    order = Order.objects.get(pk=orderid)
    order.save()

    cart.clear()

  return JsonResponse(jsonresponse)
