from django.contrib import admin
from .models import Order, OrderItem

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
  # list_display = ("name","email","phone","address", "created_at")
  pass

class OrderItemInline(admin.TabularInline):
  model = OrderItem
  raw_id_fields = ['order']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  def item_count(self,obj):
    count = OrderItem.objects.filter(order=obj).count()
    return count
  item_count.short_description = "Products"
  def order_sum(self,obj):
    sum = 0
    for order_item in OrderItem.objects.filter(order=obj):
      sum += order_item.price
    return sum
  order_sum.short_decription = "Total price"
    
  list_display = ("name","email","phone","address", "created_at", "item_count", "order_sum")
  inlines = [OrderItemInline]

