from django.conf import settings
from apps.store.models import Product

class Cart(object):

  def __init__(self, request):
    self.session = request.session
    cart = self.session.get(settings.CART_SESSION_ID)

    if not cart:
      cart = self.session[settings.CART_SESSION_ID] = {}

    self.cart = cart

  def __iter__(self):
    product_ids = self.cart.keys()

    # Batch-fetch all products in a single query instead of N individual queries
    products = Product.objects.filter(pk__in=product_ids).select_related(
        'category__main_category', 'brand'
    )
    products_map = {str(p.id): p for p in products}

    for p in product_ids:
      self.cart[str(p)]['product'] = products_map.get(str(p))

    for item in self.cart.values():
      item['total_price'] = float(float(item['price']) * int(item['quantity']))

      yield item

  def __len__(self):
    return sum(item['quantity'] for  item in self.cart.values())


  def add(self, product, quantity=1, update_quantity=False):
    product_id = str(product.id)
    price = float(product.price)

    if product_id not in self.cart:
      self.cart[product_id] = {'quantity': 0, 'price': price, 'id': product_id}

    if update_quantity:
      self.cart[product_id]['quantity'] = quantity
    else:
      self.cart[product_id]['quantity'] += 1

    self.save()

  def get_total_length(self):
    return sum(int(item['quantity']) for item in self.cart.values())

  # def get_total_cost(self):
  #   for item in self.cart.values():
  #     item['total_price'] = float(item['price']) * int(item['quantity'])
  #   return sum(float(item['total_price']) for item in self)
  def get_total_cost(self):
    # if "total_price" in self.cart.values():
      # return sum(float(item['total_price']) for item in self)
    # else:
      # return 0
    return sum(int(item['total_price']) for item in self)

  def remove(self, product_id):
    if str(product_id) in self.cart:
      del self.cart[product_id]
      self.save()

  def save(self):
    self.session[settings.CART_SESSION_ID] = self.cart
    self.session.modified = True

  def clear(self):
    del self.session[settings.CART_SESSION_ID]
    self.session.modified = True