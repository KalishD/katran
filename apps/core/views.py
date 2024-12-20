from multiprocessing import context
from django.shortcuts import render

from apps.store.models import Product, Category
from apps.blog.models import Post
def frontpage(request):
    katran_products = Product.objects.filter(brand = 1).order_by('sku')
    cangairgrinders = Product.objects.filter(category = 1).order_by('sku')
    featurescategories = Category.objects.filter(is_features = 1).order_by('ordering')
    posts = Post.objects.all()
    keywords = ''
    description = ''
    context = {
        'katran_products': katran_products,
        'cangairgrinders': cangairgrinders,
        'posts': posts,
        'featurescategories': featurescategories,
        'keywords': keywords,
        'description': description,
    }

    return render(request, 'frontpage.html', context)

def politics(request):
    context = {}
    return render(request, 'politics.html', context)

def production(request):
    mp006 = Product.objects.filter(sku = 1011040).first()
    mp01122 = Product.objects.filter(sku = 1011030).first()
    mp01115 = Product.objects.filter(sku = 1011020).first()
    mp011s = Product.objects.filter(sku = 1010140).first()
    rm8 = Product.objects.filter(sku = 1040560).first()
    rm12 = Product.objects.filter(sku = 1040550).first()
    rm16 = Product.objects.filter(sku = 1040540).first()
    tp28a = Product.objects.filter(sku = 1090150).first()
    tpv3a = Product.objects.filter(sku = 1090160).first()
    mp011_list = [mp01115,mp01122,mp011s]
    rm_list = [rm8,rm12,rm16]
    tramb_list = [tp28a, tpv3a]
    keywords = ''
    description = ''
    context = {
        'mp006': mp006,
        'mp01122': mp01122,
        'mp01115': mp01115,
        'mp011s':  mp011s,
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