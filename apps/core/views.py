from multiprocessing import context
from django.shortcuts import render

from apps.store.models import Product, Category, Brand
from apps.blog.models import Post

def frontpage(request):
    katran_products = Product.objects.filter(brand = 1, category__main_category__in = range(1,2)).order_by('sku')
    cangairgrinders = Product.objects.filter(category = 16).order_by('sku')
    anglegrinders = Product.objects.filter(category = 15).order_by('-price')
    airhammers = Product.objects.filter(category__in = range(5,6)).order_by('-price')
    posts = Post.objects.all()
    keywords = 'Купить пневмоинструмент, пневматические молотки отбойные, пневматические молотки рубильные, российский пневмоинструмент'
    description = 'Магазин пневматического иструмента, ООО "Катран-Пневмо" более 30 лет на рынке. Купить пневмоинструмент в СПб.'
    context = {
        'katran_products': katran_products,
        'cangairgrinders': cangairgrinders,
        'anglegrinders': anglegrinders,
        'airhammers': airhammers,
        'posts': posts,
        'keywords': keywords,
        'description': description,
    }

    return render(request, 'frontpage.html', context)

def politics(request):
    context = {}
    return render(request, 'politics.html', context)

def production(request):
    mp006 = Product.objects.filter(sku = 4).first()
    mp01122 = Product.objects.filter(sku = 5882).first()
    rm8 = Product.objects.filter(sku = 17).first()
    rm12 = Product.objects.filter(sku = 18).first()
    rm16 = Product.objects.filter(sku = 19).first()
    tp28a = Product.objects.filter(sku = 31).first()
    tpv3a = Product.objects.filter(sku = 237).first()
    mp011_list = [mp01122,]
    rm_list = [rm8,rm12,rm16]
    tramb_list = [tp28a, tpv3a]
    keywords = ''
    description = ''
    context = {
        'mp006': mp006,
        'mp01122': mp01122,
        'rm8': rm8,
        'rm12': rm12,
        'rm16': rm16,
        'mp011_list': mp011_list,
        'rm_list': rm_list,
        'tramb_list': tramb_list,
        'keywords': keywords,
        'description': description,
    }

    return render(request, 'production.html', context)


def about(request):
    keywords = ''
    description = ''
    context = {
        'keywords': keywords,
        'description': description,
    }
    return render(request, 'about.html', context)