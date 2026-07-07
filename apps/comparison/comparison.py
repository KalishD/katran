COMPARISON_SESSION_ID = 'comparison'
COMPARISON_MAX_ITEMS = 4


class Comparison(object):

    def __init__(self, request):
        self.session = request.session
        comparison = self.session.get(COMPARISON_SESSION_ID)
        if not comparison:
            comparison = self.session[COMPARISON_SESSION_ID] = {}
        self.comparison = comparison

    def add(self, product_id):
        product_id = str(product_id)
        if product_id not in self.comparison:
            if len(self.comparison) >= COMPARISON_MAX_ITEMS:
                return False
            self.comparison[product_id] = True
            self.save()
        return True

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.comparison:
            del self.comparison[product_id]
            self.save()

    def toggle(self, product_id):
        product_id = str(product_id)
        if product_id in self.comparison:
            self.remove(product_id)
            return False
        else:
            added = self.add(product_id)
            return added

    def get_product_ids(self):
        return [int(pid) for pid in self.comparison.keys()]

    def get_products(self):
        from apps.store.models import Product
        ids = self.get_product_ids()
        if not ids:
            return Product.objects.none()
        products = Product.objects.filter(
            pk__in=ids, is_visible=True
        ).select_related(
            'category__main_category', 'brand'
        ).prefetch_related(
            'variable_set__varitem'
        )
        ordered = sorted(products, key=lambda p: ids.index(p.id))
        return ordered

    def __len__(self):
        return len(self.comparison)

    def save(self):
        self.session[COMPARISON_SESSION_ID] = self.comparison
        self.session.modified = True

    def clear(self):
        if COMPARISON_SESSION_ID in self.session:
            del self.session[COMPARISON_SESSION_ID]
            self.session.modified = True
