from django.contrib import admin
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html
from django import forms
from django.urls import path
from django.shortcuts import render, redirect
from slugify import slugify
import csv, codecs, os, re, operator, io
from apps.store.models import Category, Product, Brand, Variable, VariableItem

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
class ProductAdmin(admin.ModelAdmin):
  
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
          for row in reader:
            i = 7
            try:
              slug = slugify(str(row[1]))
              print(row)
              product = Product.objects.update_or_create(
                sku = row[0],
                title = row[1],
                slug = slug,
                description = row[2],
                price = row[5],
                is_features = 0,
                category_id = row[4],
                brand_id = row[3],
              )
              tmp_row = []
              while row[i] != '': 
                # tmp_row.extend((row[i],row[i+1]))
                product[0].variable_set.get_or_create(
                  varitem = VariableItem.objects.filter(id = int(row[i]))[0],
                  value = row[i+1]
                )
                i += 2              
            except Exception as inst:
              print(inst)
              print('!!!_row_!!!',row)
              print('!!!_iter_!!!', i)
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
  



# admin.site.register(Variable)
@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
  # filter_horizontal = ('product',)
  pass