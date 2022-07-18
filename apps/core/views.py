from django.shortcuts import render

from apps.store.models import Product

def frontpage(request):
    # katran_products = Product.objects.filter(brand = 'Катран-Пневмо')    
    # featured_product = Product.objects.filter(is_features=True)
    context = {}

    return render(request, 'frontpage.html', context)
