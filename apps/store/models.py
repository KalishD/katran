from io import BytesIO
from django.core.files import File
from PIL import Image
from django.db import models
from django_summernote.fields import SummernoteTextField
from meta.models import ModelMeta
from django.utils.html import strip_tags
from slugify import slugify
import re

class MainCategory(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    ordering = models.PositiveIntegerField(default=0)
    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ('ordering',)
        
    def __str__(self):
        return self.title
    
    def get_categories(self):
        return Category.objects.filter(main_category=self)

    def get_absolute_url(self):
        return '/catalog/%s/' % (self.slug)

class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    ordering = models.PositiveSmallIntegerField(default=0)
    main_category = models.ForeignKey(MainCategory, on_delete=models.DO_NOTHING, blank=True, null=True)
    is_features = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    summer_description = SummernoteTextField(default='')

    image = models.ImageField(upload_to="uploads/brands/", blank=True, null=True, default='static/images/blank_prodimg.jpg')
    def save(self, *args, **kwargs):
        self.thumbnail = self.make_thumbnail(self.image)
        print('-=-=-=Convert=-=-=-')
        self.image = self.convert_rgb(self.image)
        super().save(*args, **kwargs)

    def convert_rgb(self, image):
        img = Image.open(image)
        print('-=-=-=Convert=-=-=-')
        img.convert('RGB')
        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=80)
        image = File(thumb_io, name=image.name)

        return image
        
    def make_thumbnail(self, image, size=(60, 60)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=80)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail
        
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('ordering',)
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return '/catalog/%s/%s/' % (self.main_category.slug, self.slug)
    
    def get_products(self):
        return Product.objects.filter(category=self)

    def count_visible_products(self):
        return Product.objects.filter(category=self, is_visible=True).count()


class Brand(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, null=True)

    image = models.ImageField(upload_to="uploads/brands/", blank=True, null=True, default='static/images/blank_prodimg.jpg')
    thumbnail = models.ImageField(upload_to="uploads/brands/", blank=True, null=True)

    ordering = models.PositiveSmallIntegerField(default=0)
    country = models.CharField(max_length=255, null=True, blank=True)

    is_on = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'
        
    def get_products(self):
        return Product.objects.filter(brand=self)   
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.thumbnail = self.make_thumbnail(self.image)
        print('-=-=-=Convert=-=-=-')
        self.image = self.convert_rgb(self.image)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return '/brands/%s/' % (self.slug)
    
    def convert_rgb(self, image):
        img = Image.open(image)
        print('-=-=-=Convert=-=-=-')
        img.convert('RGB')
        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=80)
        image = File(thumb_io, name=image.name)

        return image
        
    def make_thumbnail(self, image, size=(60, 60)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=80)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail


class Product(ModelMeta, models.Model):
    tax = 22

    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.DO_NOTHING, blank=True, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    sku = models.PositiveSmallIntegerField(blank=False, null=False, unique=True)
    description = models.TextField(blank=True, null=True)
        
    price = models.FloatField(verbose_name='Цена с НДС')
    price_wo_tax = models.FloatField(verbose_name='Цена без НДС')

    is_features = models.BooleanField(default=False)
    is_sale = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    is_in_sales_price = models.BooleanField(default=False)
    
    article = models.CharField(max_length=255,blank=True, null=True)

    image = models.ImageField(upload_to="uploads/products/", blank=True, null=True, default='static/images/blank_prodimg.jpg')
    partlist = models.ImageField(upload_to="uploads/products/partlists/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="uploads/products/thumb/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add= True)
    variables = models.ManyToManyField('VariableItem', through='Variable', related_name='variables')

    parts = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='used_in')
    analog = models.OneToOneField('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='analog_of')
    similar_products = models.ManyToManyField('self', blank=True)

    keywords = models.CharField(max_length=255, blank=True, null=True)

    ordering = models.PositiveSmallIntegerField(blank=True, null=True)

    in_stock = models.PositiveSmallIntegerField(blank=True, null=True, default=1)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('-created_at','title')
        
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.set_price_w_tax()
        self.thumbnail = self.make_thumbnail(self.image)

        super().save(*args, **kwargs)

    def set_price_w_tax(self):
        self.price = self.price_wo_tax * (1 + self.tax/100)
        self.price = round(self.price, 2)

    def get_absolute_url(self):
        return '/catalog/%s/%s/%s/' % (self.category.main_category.slug, self.category.slug, self.slug)

    def make_thumbnail(self, image, size=(60, 60)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=80)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail
    _metadata = {
        'name': 'title',
        'description': 'get_schema_description',
        'image': 'get_schema_image',
        'url': 'get_absolute_url',
        'object_type': 'product'  # Явно устанавливаем тип 'product' для Open Graph
    }
    
    _schema = {
        '@type': 'Product',
        'name': 'title',
        'url': 'get_schema_url',
        'image': 'get_schema_image',
        'description': 'get_schema_description',
        'sku': 'sku',
        'brand': 'get_schema_brand',
        'offers': 'get_schema_offer',
        'category': 'get_schema_category'
    }
    def get_schema_description(self):
        variables_list = ''
        for var in self.variable_set.all():
            variables_list += var.value + var.varitem.dimention + '; '

        schema_description = f'{self.title}; {self.article} Характеристики: {variables_list}'
        return strip_tags(schema_description)

    def get_schema_category(self):
        return self.category.title

    def get_schema_url(self):
        return self.build_absolute_uri(self.get_absolute_url())

    def get_schema_image(self):
        """
        Возвращает абсолютный URL изображения для Schema.org.
        """
        if self.image and self.image.url:
            return self.build_absolute_uri(self.image.url)
        return None

    def get_schema_brand(self):
        """
        Возвращает вложенный объект Schema.org для бренда, если он существует.
        Это предотвращает ошибки, если поле brand пустое.
        """
        if self.brand:
            return {
                '@type': 'Brand',
                'name': self.brand.title
            }
        return None

    def get_schema_offer(self):
        """
        Создает объект Offer для текущего продукта.
        """
        return {
            '@context': 'https://schema.org/',
            '@type': 'Offer',
            'url': self.build_absolute_uri(self.get_absolute_url()),
            'name': self.title,
            'priceCurrency': 'RUB', # Установите валюту, например, 'RUB' или 'USD'
            'price': self.price,
            'itemCondition': 'https://schema.org/NewCondition',
            'availability': 'https://schema.org/InStock', # Укажите актуальный статус наличия
        }        

    def get_clean_title(self):
        return re.sub(r'\s*\([^()]*\)$', '', self.title)

    def get_last_word_title(self):
        # 1. Удаляем концевые пробелы, чтобы не получить пустую строку после rsplit
        text = self.get_clean_title().strip()
        
        # 2. Разделяем строку только один раз (maxsplit=1) с правого конца.
        #    Это создаст список из максимум двух элементов: [Всё_Остальное, Последнее_Слово].
        parts = text.rsplit(maxsplit=1)
        
        if parts:
            # Последний элемент списка (даже если список состоит из одного элемента)
            return parts[-1]
        else:
            return ""
        
class VariableItem(models.Model):
    title = models.CharField(max_length=255)
    dimention = models.CharField(max_length=255, blank=True, null=True,)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

class Variable(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    varitem = models.ForeignKey(VariableItem, on_delete=models.DO_NOTHING)
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.varitem.title


class Patent(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='patent', blank=True, null=True, verbose_name='Товар')
    document_number = models.CharField(max_length=255, verbose_name='Номер документа')
    publication_date = models.DateField(verbose_name='Дата публикации')
    image = models.ImageField(upload_to='uploads/patents/', blank=True, null=True, verbose_name='Схема')
    document_image = models.ImageField(upload_to='uploads/patents/', blank=True, null=True, verbose_name='Бланк патента')
    title = models.CharField(max_length=255, verbose_name='Название')
    library = models.CharField(max_length=255, blank=True, null=True, verbose_name='Библиотека')
    link = models.URLField(blank=True, null=True, verbose_name='Ссылка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    def save(self, *args, **kwargs):
        if self.image:
            self.image = self.convert_rgb(self.image)
        super().save(*args, **kwargs)

    def convert_rgb(self, image):
        img = Image.open(image)
        img.convert('RGB')
        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=80)
        image = File(thumb_io, name=image.name)
        return image

    class Meta:
        verbose_name = 'Патент'
        verbose_name_plural = 'Патенты'

    def __str__(self):
        return f'Патент {self.document_number} - {self.title}'