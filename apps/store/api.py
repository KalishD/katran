import json
import time

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.cache import cache
from apps.cart.cart import Cart

from .models import Product

from apps.order.utils import checkout
from apps.order.models import Order, OrderItem

CHECKOUT_RATE_LIMIT = 5  # max orders per hour per session
CHECKOUT_RATE_WINDOW = 3600  # 1 hour in seconds

def rate_limit_checkout(request):
    """Simple rate limiting for checkout using Django cache."""
    session_key = request.session.session_key or request.META.get('REMOTE_ADDR', 'unknown')
    cache_key = f'checkout_rate_{session_key}'
    attempts = cache.get(cache_key, 0)

    if attempts >= CHECKOUT_RATE_LIMIT:
        return False

    cache.set(cache_key, attempts + 1, CHECKOUT_RATE_WINDOW)
    return True

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
  if not rate_limit_checkout(request):
    return JsonResponse({'success': False, 'error': 'Too many checkout attempts. Please try again later.'}, status=429)

  cart = Cart(request)

  if len(cart) == 0:
    return JsonResponse({'success': False, 'error': 'Cart is empty'}, status=400)

  data = json.loads(request.body)
  name = data.get('name', '').strip()
  email = data.get('email', '').strip()
  phone = data.get('phone', '').strip()
  address = data.get('address', '').strip()

  if not name or not email:
    return JsonResponse({'success': False, 'error': 'Name and email are required'}, status=400)

  orderid = checkout(request, name, email, phone, address)

  order = Order.objects.get(pk=orderid)
  order.save()
  order.send_order_confirmation_email()
  order.send_user_confirmation_email()
  cart.clear()

  return JsonResponse({'success': True})
