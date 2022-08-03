from django.shortcuts import render

from apps.store.models import Product

def frontpage(request):
    katran_products = Product.objects.filter(brand = 1)    
    # featured_product = Product.objects.filter(is_features=True)
    context = {
        'katran_products': katran_products,
    }

    return render(request, 'frontpage.html', context)

def production(request):
    # katran_products = Product.objects.filter(brand = 'Катран-Пневмо')    
    # featured_product = Product.objects.filter(is_features=True)
    mp006 = Product.objects.filter(sku = 1011040).first()
    mp01122 = Product.objects.filter(sku = 1011030).first()
    mp01115 = Product.objects.filter(sku = 1011020).first()
    rm8 = Product.objects.filter(sku = 1040560).first()
    rm12 = Product.objects.filter(sku = 1040550).first()
    rm16 = Product.objects.filter(sku = 1040540).first()

    context = {
        'mp006': mp006,
        'mp01122': mp01122,
        'mp01115': mp01115,
        'rm8': rm8,
        'rm12': rm12,
        'rm16': rm16,
    }

    return render(request, 'production.html', context)
