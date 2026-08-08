import json
from django.http import JsonResponse
from .comparison import Comparison, COMPARISON_MAX_ITEMS


def api_add_to_comparison(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    if not product_id:
        return JsonResponse({'success': False, 'error': 'product_id required'}, status=400)

    comparison = Comparison(request)
    added = comparison.add(product_id)
    return JsonResponse({
        'success': True,
        'count': len(comparison),
        'added': added,
    })


def api_remove_from_comparison(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    if not product_id:
        return JsonResponse({'success': False, 'error': 'product_id required'}, status=400)

    comparison = Comparison(request)
    comparison.remove(product_id)
    return JsonResponse({
        'success': True,
        'count': len(comparison),
    })


def api_toggle_comparison(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    if not product_id:
        return JsonResponse({'success': False, 'error': 'product_id required'}, status=400)

    comparison = Comparison(request)
    was_present = str(product_id) in comparison.comparison
    if was_present:
        comparison.remove(product_id)
        return JsonResponse({
            'success': True,
            'count': len(comparison),
            'added': False,
        })
    else:
        added = comparison.add(product_id)
        return JsonResponse({
            'success': True,
            'count': len(comparison),
            'added': added,
        })
