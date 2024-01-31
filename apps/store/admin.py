from django.contrib import admin
from django.core.files import File
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html
from django import forms
from django.urls import path
from django.shortcuts import render, redirect
from slugify import slugify
import csv, codecs, os, re, operator, io, requests
from io import BytesIO
from PIL import Image
from apps.store.models import Category, Product, Brand, Variable, VariableItem, MainCategory
from urllib.parse import parse_qsl, urljoin, urlparse
from urllib.request import urlopen
from apps.core.utils import *
from import_export.admin import ExportActionMixin

class VariableInline(admin.TabularInline):
  model = Variable
  raw_id_fields = ['product']

# CSV Import Products
class CsvImportForm(forms.Form):
    csv_files = forms.FileField()

@admin.register(VariableItem)
class VariableItemAdmin(admin.ModelAdmin):
  change_list_template = "variableitem_changelist.html"
  
  def get_urls(self):
    urls = super().get_urls()
    my_urls = [
      path('import-csv-var/', self.import_csv),
    ]
    return my_urls + urls
    
  def import_csv(self, request):
    if request.method == "POST":
      csv_file = request.FILES["csv_files"]
      with io.TextIOWrapper(csv_file, encoding="utf-8") as text_file:
        reader = csv.reader(text_file, lineterminator='\n', delimiter=',')
        for row in reader:
          try:
            varitem = VariableItem.objects.get_or_create(
              id = row[0],
              title = row[1],
              dimention = row[2],
            )
          except Exception as inst:
            print(inst)
            print('Exception:',row)
        self.message_user(request, "Your csv file has been imported")
        return redirect("..")
    form = CsvImportForm()
    payload = {"form": form}
    return render(
        request, "csv_form.html", payload
    )
    
# admin.site.register(Product)
@admin.register(Product)
class ProductAdmin(ExportActionMixin, admin.ModelAdmin):
  
  change_list_template = "products_changelist.html"

  def get_urls(self):
    urls = super().get_urls()
    my_urls = [
        path('import-csv/', self.import_csv),
        path('import-csv-price/', self.import_csv_price)
    ]
    return my_urls + urls
  
  def import_csv_price(self, request):
    if request.method == "POST":
      csv_file = request.FILES["csv_files"]
      with io.TextIOWrapper(csv_file, encoding="utf-8") as text_file:
        reader = csv.reader(text_file, lineterminator='\n', delimiter=';')
        for row in reader:
          try:
            product = Product.objects.filter(sku=row[0]).first()
            product.price = row[5]
            product.save()
          except:
            print('Error! Product not found!', row)
        self.message_user(request, "Your csv file has been imported")
        return redirect("..")
    form = CsvImportForm()
    payload = {"form": form}
    return render(
      request, "csv_form.html", payload
    )
  
  def import_csv(self, request):
    if request.method == "POST":
        csv_file = request.FILES["csv_files"]
        with io.TextIOWrapper(csv_file, encoding="utf-8") as text_file:
          reader = csv.reader(text_file, lineterminator='\n', delimiter = ';')
          for count, row in enumerate(reader, start=1):
            # print('Product #',count, type(count))
            # print('!!!_row_!!!',row)
            i = 8
            try:
              print('slug')
              print(row[2])
              slug = slugify(str(row[2]))
              print(slug)
              product = Product.objects.update_or_create(
                id = count,
                sku = row[1],
                title = row[2],
                slug = slug,
                description = row[3],
                price = row[6],
                is_features = 0,
                category_id = row[5],
                brand_id = row[4],
              )
              if row[7]:
                url = row[7]
                parse_object = urlparse(url)
                domain = parse_object.netloc
                path = parse_object.path
                filename = url.split('/')[-1]
                # print('Domain, path, filename',domain, path, filename)
                response = requests.get(url)
                response_content = BytesIO(urlopen(url).read())
                pil_image = Image.open(response_content)
                django_file = pil_to_django(pil_image)
                product[0].image.save(filename, django_file)
              tmp_row = []
              while row[i] != '': 
                # tmp_row.extend((row[i],row[i+1]))
                product[0].variable_set.get_or_create(
                  varitem = VariableItem.objects.filter(id = int(row[i]))[0],
                  value = row[i+1]
                )
                i += 2  
            except Exception as inst:
              print('Error, line #', count)
              print(inst)
          self.message_user(request, "Your csv file has been imported")
          return redirect("..")
    form = CsvImportForm()
    payload = {"form": form}
    return render(
        request, "csv_form.html", payload
    )

  list_display = ("sku","title","product_category","brand","price","is_features")
  search_fields = ("title__contains",)
  fields = ("category","brand","sku","title","slug","description","price","is_features","image")
  prepopulated_fields = {'slug': ('title',) }
  inlines = [VariableInline]
  save_as = True
  def product_category(self,obj):
    url = (
      reverse("admin:store_product_changelist")
      + "?"
      + urlencode({"category_id": f"{obj.category.id}"})
    )
    return format_html('<a href={}>{}</a>', url, obj.category)



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

# admin.site.register(MainCategory)
@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
  list_display = ("title",)
  prepopulated_fields = {'slug': ('title',) }
  fields = ("title","slug","ordering")
  
# admin.site.register(Category)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ("title", "main_category", "ordering","product_count")

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
  fields = ("main_category","title","slug","ordering")
  prepopulated_fields = {'slug': ('title',) }
  



# admin.site.register(Variable)
@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
  # filter_horizontal = ('product',)
  pass