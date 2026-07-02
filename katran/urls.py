"""katran URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView

from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls import include
from apps.cart.views import cart_detail, success
from apps.comparison.views import comparison_detail
from apps.comparison.api import api_add_to_comparison, api_remove_from_comparison, api_toggle_comparison
from apps.core.views import frontpage, production, about, politics, contacts, RobotsTxtView, temp, html_sitemap, politics_agree, sale_price, export_pricelist, csp_report
from apps.store.views import category_detail, product_detail, catalog, brand_detail, search, main_category_detail, category_products_api, brands, brand_products_api, search_api
from apps.blog.views import blog, post_detail
from apps.store.api import api_add_to_cart, api_remove_from_cart, api_checkout

from .sitemaps import StaticViewSitemap, CategorySitemap, ProductSitemap, BrandSitemap, PostsSitemap

sitemaps = {'static': StaticViewSitemap, 'product': ProductSitemap, 'category': CategorySitemap, 'brand': BrandSitemap, 'post': PostsSitemap}

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path("robots.txt", RobotsTxtView.as_view(content_type="text/plain"), name="robots"),
    # path("llms.txt", LLMSTxtView.as_view(content_type="text/plain"), name="llms"),
    # path("YML.yml", YMLView.as_view(content_type="text/plain"), name="YML"),
    path('', frontpage, name='frontpage'),
    path('cart/', cart_detail, name='cart'),
    path('cart/success/', success, name='success'),
    path('comparison/', comparison_detail, name='comparison'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('sitemap/', html_sitemap, name='html_sitemap'),
    # API
    path('api/api_add_to_cart/', api_add_to_cart, name='api_add_to_cart'),
    path('api/api_remove_from_cart/', api_remove_from_cart, name='api_remove_from_cart'),
    path('api/api_checkout/', api_checkout, name='api_checkout'),
    path('api/api_toggle_comparison/', api_toggle_comparison, name='api_toggle_comparison'),
    path('api/api_remove_from_comparison/', api_remove_from_comparison, name='api_remove_from_comparison'),

    # STORE
    path('brands/', brands, name='brands'),
    path('brands/<slug:slug>/', brand_detail, name='brand_detail'),
    path('api/brands/<slug:slug>/', brand_products_api, name='brand_products_api'),
    
    path('catalog/', catalog, name='catalog'),
    path('catalog/<slug:slug>/', main_category_detail, name='main_category_detail'),
    path('catalog/<slug:maincategory_slug>/<slug:slug>/', category_detail, name='category_detail'),
    path('api/catalog/<slug:main_category_slug>/<slug:category_slug>/', category_products_api, name='category_products_api'),
    path('catalog/<slug:maincategory_slug>/<slug:category_slug>/<slug:slug>/', product_detail, name='product_detail'),

    
    path('production/', production, name='production'),
    path('about/', about, name='about'),
    path('privacy-policy/', politics, name='politics'),
    path('privacy-policy_agree/', politics_agree, name='politics_agree'),
    path('contacts/', contacts, name='contacts'),
    path('pricelist/', sale_price, name='sale_price'),
    path('download_pricelist/', export_pricelist, name='export_pricelist'),
    path('search/', search, name="search"),
    path('api/search/', search_api, name='search_api'),
    path('csp-report/', csp_report, name='csp_report'),
    #BLOG
    path('temp/', temp, name="temp"),
    path('blog/', blog, name="blog"),
    path('blog/<slug:slug>/', post_detail, name='post_detail'),
]

# Summernote URLs (staff only)
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import re_path
urlpatterns += [
    re_path(r'^static/summernote/', staff_member_required(include('django_summernote.urls'))),
]
#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)