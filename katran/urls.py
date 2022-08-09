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

from django.conf.urls.static import static
from django.conf import settings

from apps.cart.views import cart_detail, success
from apps.core.views import frontpage, production
from apps.store.views import category_detail, product_detail, catalog, brand_detail

from apps.store.api import api_add_to_cart, api_remove_from_cart, api_checkout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', frontpage, name='frontpage'),
    path('cart/', cart_detail, name='cart'),
    path('cart/success/', success, name='success'),

    # API
    path('api/api_add_to_cart/', api_add_to_cart, name='api_add_to_cart'),
    path('api/api_remove_from_cart/', api_remove_from_cart, name='api_remove_from_cart'),
    path('api/api_checkout/', api_checkout, name='api_checkout'),

    # STORE
    path('brands/<slug:slug>', brand_detail, name='brand_detail'),
    path('<slug:category_slug>/<slug:slug>', product_detail, name='product_detail'),
    path('<slug:slug>', category_detail, name='category_detail'),
    

    path('catalog/', catalog, name='catalog'),
    path('production/', production, name='production'),
]
#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
