from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from apps.store.models import Product

# Create your models here.

class Order(models.Model):
  name = models.CharField(max_length=255, null=False, blank=False)
  email = models.EmailField(null=False, blank=False)
  phone = PhoneNumberField(null=False, blank=False)
  address = models.TextField(null=False, blank=False)

  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return '%s' % self.name

  class Meta:
    verbose_name = 'Заказ'
    verbose_name_plural = 'Заказы'
    ordering = ('-created_at','name', 'email')

class OrderItem(models.Model):
  order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
  product = models.ForeignKey(Product, related_name="items", on_delete=models.DO_NOTHING)

  price = models.FloatField()
  quantity = models.PositiveSmallIntegerField(default=1)
  
  def __str__(self):
    return '%s' % self.id