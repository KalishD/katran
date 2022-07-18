from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  list_display = ("name","email","phone","address", "created_at")

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
  # list_display = ("name","email","phone","address", "created_at")
  pass