import json
import re
import time

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.cache import cache
from django.views.decorators.http import require_POST
from apps.cart.cart import Cart

from .models import PriceRequest, Product

from apps.order.utils import checkout
from apps.order.models import Order, OrderItem

CHECKOUT_RATE_LIMIT = 5  # max orders per hour per session
CHECKOUT_RATE_WINDOW = 3600  # 1 hour in seconds

PRICE_REQUEST_RATE_LIMIT = 10  # max price requests per hour per session
PRICE_REQUEST_RATE_WINDOW = 3600  # 1 hour in seconds

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]{2,}$')


def rate_limit_checkout(request):
    """Simple rate limiting for checkout using Django cache."""
    session_key = request.session.session_key or request.META.get('REMOTE_ADDR', 'unknown')
    cache_key = f'checkout_rate_{session_key}'
    attempts = cache.get(cache_key, 0)

    if attempts >= CHECKOUT_RATE_LIMIT:
        return False

    cache.set(cache_key, attempts + 1, CHECKOUT_RATE_WINDOW)
    return True


def rate_limit_price_request(request):
    """Same pattern as checkout, separate bucket so one cannot starve the other."""
    session_key = request.session.session_key or request.META.get('REMOTE_ADDR', 'unknown')
    cache_key = f'price_request_rate_{session_key}'
    attempts = cache.get(cache_key, 0)

    if attempts >= PRICE_REQUEST_RATE_LIMIT:
        return False

    cache.set(cache_key, attempts + 1, PRICE_REQUEST_RATE_WINDOW)
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


@require_POST
def api_request_price(request):
  """Lead capture for products priced on request.

  The row is stored first and the notification email is best-effort, so a mail
  outage cannot silently drop the only conversion path these products have.
  """
  if not rate_limit_price_request(request):
    return JsonResponse(
      {'success': False, 'error': 'Слишком много запросов. Попробуйте позже или позвоните нам.'},
      status=429,
    )

  try:
    data = json.loads(request.body)
  except (json.JSONDecodeError, UnicodeDecodeError):
    return JsonResponse({'success': False, 'error': 'Некорректный запрос.'}, status=400)

  product_id = data.get('product_id')
  name = str(data.get('name', '')).strip()
  email = str(data.get('email', '')).strip()
  phone = str(data.get('phone', '')).strip()
  comment = str(data.get('comment', '')).strip()

  if not name:
    return JsonResponse({'success': False, 'error': 'Укажите имя.'}, status=400)
  if not EMAIL_RE.match(email):
    return JsonResponse({'success': False, 'error': 'Проверьте e-mail.'}, status=400)

  product = get_object_or_404(Product, pk=product_id, is_visible=True)

  price_request = PriceRequest.objects.create(
    product=product,
    name=name[:150],
    email=email[:254],
    phone=phone[:40],
    comment=comment[:2000],
    source_url=str(data.get('source_url', ''))[:500],
  )
  price_request.send_office_email()

  return JsonResponse({'success': True, 'id': price_request.pk})
