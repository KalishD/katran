import json
from django.shortcuts import render
from django.http import JsonResponse
from .comparison import Comparison


def comparison_detail(request):
    comparison = Comparison(request)
    products = comparison.get_products()

    products_json = []
    spec_rows = []

    if products:
        for p in products:
            url = p.get_absolute_url()
            brand_url = p.brand.get_absolute_url() if p.brand else ''
            products_json.append({
                'id': p.id,
                'title': p.title,
                'url': url,
                'image': p.image.url if p.image else '',
                'image_sm': p.get_resized_url('image', 'sm') if p.image else '',
                'image_md': p.get_resized_url('image', 'md') if p.image else '',
                'brand': p.brand.title if p.brand else '',
                'brand_url': brand_url,
                'price': str(p.price) if p.price else '',
                'main_category': p.category.main_category.title,
                'main_category_url': p.category.main_category.get_absolute_url(),
                'category': p.category.title,
                'category_url': p.category.get_absolute_url(),
            })

        var_ids = set()
        for p in products:
            for v in p.variable_set.all():
                var_ids.add(v.varitem_id)
        from apps.store.models import VariableItem
        all_variables = VariableItem.objects.filter(pk__in=var_ids)

        for var in all_variables:
            values = {}
            for p in products:
                val = ''
                for v in p.variable_set.select_related('varitem').all():
                    if v.varitem_id == var.id:
                        dim = v.varitem.dimention or ''
                        val = f'{v.value} {dim}'.strip()
                        break
                values[p.id] = val
            spec_rows.append({
                'title': var.title,
                'dimention': var.dimention or '',
                'values': values,
            })

    return render(request, 'comparison.html', {
        'comparison': comparison,
        'products_json': json.dumps(products_json),
        'spec_rows_json': json.dumps(spec_rows),
    })
