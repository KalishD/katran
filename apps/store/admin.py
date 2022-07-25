from django.contrib import admin
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html

from apps.store.models import Category, Product, Brand, Variable, VariableItem

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
  list_display = ("title","product_count")
  fields = ("title","slug","description", "image")
  prepopulated_fields = {'slug': ('title',) }

  def product_count(self, obj):
    count = Product.objects.filter(brand=obj).count()

    url = (
      reverse("admin:store_product_changelist")
      + "?"
      + urlencode({"brand_id": f"{obj.id}"})
    )
    return format_html('<a href={}>{} Products</a>', url, count)

  product_count.short_description = "Products"


  
# admin.site.register(Category)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ("title", "product_count")

  def product_count(self, obj):
    count = Product.objects.filter(category=obj).count()

    url = (
      reverse("admin:store_product_changelist")
      + "?"
      + urlencode({"category_id": f"{obj.id}"})
    )
    return format_html('<a href={}>{} Products</a>', url, count)
  
  def get_form(self, request, obj=None, **kwargs):
    form = super().get_form(request, obj, **kwargs)
    form.base_fields["title"].label = "Название: "
    return form
    

  product_count.short_description = "Products"
  fields = ("title","slug","ordering")
  prepopulated_fields = {'slug': ('title',) }
  

# admin.site.register(Product)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = ("sku","title","product_category","brand","price","is_features")
  search_fields = ("title__contains",)
  fields = ("category","brand","sku","title","slug","description","price","is_features","image")
  prepopulated_fields = {'slug': ('title',) }

  def product_category(self,obj):
    url = (
      reverse("admin:store_product_changelist")
      + "?"
      + urlencode({"category_id": f"{obj.category.id}"})
    )
    return format_html('<a href={}>{}</a>', url, obj.category)
  

# admin.site.register(Variable)
@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
  # filter_horizontal = ('product',)
  pass

admin.site.register(VariableItem)

