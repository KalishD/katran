from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from apps.store.models import Category, Product, Brand
from apps.blog.models import Post
from apps.solutions.models import Industry, CaseStudy


class StaticViewSitemap(Sitemap):
    def items(self):
        return [
            'frontpage', 'about', 'production', 'contacts', 'politics',
            'import_substitution', 'custom_development',
            'solutions_index', 'cases_index',
            'brands', 'catalog', 'blog',
        ]

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    def items(self):
        return Category.objects.select_related('main_category').only('slug', 'main_category__slug')


class ProductSitemap(Sitemap):
    def items(self):
        return Product.objects.select_related(
            'category__main_category'
        ).only('slug', 'created_at', 'category__slug', 'category__main_category__slug')

    def lastmod(self, obj):
        return obj.created_at


class BrandSitemap(Sitemap):
    def items(self):
        return Brand.objects.only('slug')


class PostsSitemap(Sitemap):
    def items(self):
        return Post.objects.only('slug', 'created_at')

    def lastmod(self, obj):
        return obj.created_at


class IndustrySitemap(Sitemap):
    def items(self):
        return Industry.objects.filter(is_visible=True)


class CaseStudySitemap(Sitemap):
    def items(self):
        return CaseStudy.objects.filter(is_visible=True)

    def lastmod(self, obj):
        return obj.created_at
