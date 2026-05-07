from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from apps.store.models import Category, Product, Brand

class StaticViewSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return ['frontpage', 'about', 'production', 'contacts', 'politics', 'sale_price', 'html_sitemap']

    def location(self, item):
        return reverse(item)

class CategorySitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9
    def items(self):
        return Category.objects.all()

class ProductSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1
    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.created_at

class BrandSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9
    def items(self):
        return Brand.objects.all()

class PostsSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.7
    def item(self):
        return Post.objects.all()