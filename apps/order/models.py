from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from apps.store.models import Product
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class Order(models.Model):
  name = models.CharField(max_length=255, null=False, blank=False)
  email = models.EmailField(null=False, blank=False)
  phone = PhoneNumberField(null=False, blank=False)
  address = models.TextField(null=False, blank=False)

  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return '%s' % self.name

  def send_order_confirmation_email(self):
    subject = f'Новый заказ #{self.id} на сайте'
    recipient_list = ['office@katran-pnevmo.ru'] # Адрес, на который отправляем письмо
    # recipient_list = ['katran-pnevmo@yandex.ru'] # Адрес, на который отправляем письмо
    
    # Получаем все OrderItem'ы, связанные с этим заказом
    # order_items = self.orderitem_set.all()
    order_items = OrderItem.objects.filter(order=self)

    order_items = self.orderitem_set.all()
    
    # Calculate total price for each item and the grand total
    items_with_totals = []
    total_order_price = 0
    for item in order_items:
        item_total = item.quantity * item.price
        items_with_totals.append({
            'item': item,
            'item_total': item_total,
        })
        total_order_price += item_total

    context = {
        'order': self,
        'items_with_totals': items_with_totals, # Pass items with their calculated totals
        'total_order_price': total_order_price,
    }

    # Генерируем HTML-содержимое письма из шаблона
    html_message = render_to_string('emails/order_confirmation.html', context)
    plain_message = strip_tags(html_message) # Обычный текст для клиентов, не поддерживающих HTML

    send_mail(
        subject,
        plain_message,
        from_email=None, # Использует DEFAULT_FROM_EMAIL из settings.py
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False,
    )

  def send_user_confirmation_email(self):
    subject = f'Ваш заказ #{self.id} на сайте katran-pnevmo.ru'
    recipient_list = [self.email] # Адрес, на который отправляем письмо
    # recipient_list = ['katran-pnevmo@yandex.ru'] # Адрес, на который отправляем письмо
    
    # Получаем все OrderItem'ы, связанные с этим заказом
    # order_items = self.orderitem_set.all()
    order_items = OrderItem.objects.filter(order=self)

    order_items = self.orderitem_set.all()
    
    # Calculate total price for each item and the grand total
    items_with_totals = []
    total_order_price = 0
    for item in order_items:
        item_total = item.quantity * item.price
        items_with_totals.append({
            'item': item,
            'item_total': item_total,
        })
        total_order_price += item_total

    context = {
        'order': self,
        'items_with_totals': items_with_totals, # Pass items with their calculated totals
        'total_order_price': total_order_price,
    }

    # Генерируем HTML-содержимое письма из шаблона
    html_message = render_to_string('emails/user_confirmation.html', context)
    plain_message = strip_tags(html_message) # Обычный текст для клиентов, не поддерживающих HTML

    send_mail(
        subject,
        plain_message,
        from_email=None, # Использует DEFAULT_FROM_EMAIL из settings.py
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False,
    )     

  class Meta:
    verbose_name = 'Заказ'
    verbose_name_plural = 'Заказы'
    ordering = ('-created_at','name', 'email')

class OrderItem(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE)
  product = models.ForeignKey(Product, related_name="products", on_delete=models.DO_NOTHING)

  price = models.FloatField()
  quantity = models.PositiveSmallIntegerField(default=1)
  
  def __str__(self):
    return '%s' % self.id