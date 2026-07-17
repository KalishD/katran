from io import BytesIO
from decimal import Decimal
from django.core.files import File
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
from django.db import models
from django_summernote.fields import SummernoteTextField
from meta.models import ModelMeta
from django.utils.html import strip_tags
from slugify import slugify
import os
import re


class ImageProcessingMixin:
    """Mixin providing image processing methods for models with image fields."""

    def _is_new_upload(self, field_name):
        field = getattr(self, field_name)
        if not field:
            return False
        return not field._committed

    def _delete_existing(self, field_name, target_name=None):
        field = getattr(self, field_name)
        if not field:
            return
        upload_to = field.field.upload_to
        # Delete the original uploaded file
        if field.name:
            orig_path = os.path.join(upload_to, os.path.basename(field.name))
            if field.storage.exists(orig_path):
                field.storage.delete(orig_path)
        # Delete any file at the target path
        if target_name:
            target_path = os.path.join(upload_to, target_name)
            if field.storage.exists(target_path):
                field.storage.delete(target_path)

    def _delete_path(self, field_name, path):
        field = getattr(self, field_name)
        if field.storage.exists(path):
            field.storage.delete(path)

    def convert_rgb(self, image, target_name=None):
        if not image:
            return image
        img = Image.open(image)
        img = img.convert('RGB')
        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=80)
        thumb_io.seek(0)
        name = target_name if target_name else os.path.basename(image.name)
        return File(thumb_io, name=name)

    def make_thumbnail(self, image, target_name=None, size=(60, 60)):
        if not image:
            return image
        img = Image.open(image)
        img = img.convert('RGB')
        img.thumbnail(size)
        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=80)
        thumb_io.seek(0)
        name = target_name if target_name else os.path.basename(image.name)
        return File(thumb_io, name=name)

    def make_resized(self, image, target_name=None, max_width=800):
        """Resize image to max_width maintaining aspect ratio, save as JPEG."""
        if not image:
            return image
        img = Image.open(image)
        img = img.convert('RGB')
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)
        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=80)
        thumb_io.seek(0)
        name = target_name if target_name else os.path.basename(image.name)
        return File(thumb_io, name=name)

    def get_resized_url(self, field_name, suffix):
        """Get URL for a resized variant (e.g. _sm, _md). Falls back to original."""
        field = getattr(self, field_name)
        if not field or not field.name:
            return ''
        url = field.url
        base, ext = os.path.splitext(url)
        return f'{base}_{suffix}{ext}'

    def generate_variants(self, field_name='image', slug=None):
        """Generate _sm and _md resized variants for an image field."""
        field = getattr(self, field_name)
        if not field or not field.name:
            return
        slug = slug or self.slug
        upload_to = field.field.upload_to
        for suffix, max_width in [('sm', 400), ('md', 800)]:
            variant = self.make_resized(field, target_name=f'{slug}_{suffix}.jpg', max_width=max_width)
            variant_path = os.path.join(upload_to, f'{slug}_{suffix}.jpg')
            field.storage.save(variant_path, variant)


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

class Category(ImageProcessingMixin, models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    ordering = models.PositiveSmallIntegerField(default=0)
    main_category = models.ForeignKey(MainCategory, on_delete=models.SET_NULL, blank=True, null=True)
    is_features = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    image = models.ImageField(upload_to="uploads/categories/", blank=True, null=True, default='static/images/blank_prodimg.jpg')

    def save(self, *args, **kwargs):
        is_new = self._is_new_upload('image')
        if is_new:
            self._delete_existing('image', target_name=f'{self.slug}.jpg')
            self._delete_existing('image', target_name=f'{self.slug}_sm.jpg')
            self._delete_existing('image', target_name=f'{self.slug}_md.jpg')
            self.image = self.convert_rgb(self.image, target_name=f'{self.slug}.jpg')
        super().save(*args, **kwargs)
        if is_new:
            self.generate_variants('image', self.slug)
        
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('ordering',)
        indexes = [
            models.Index(fields=['main_category', 'slug']),
        ]
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return '/catalog/%s/%s/' % (self.main_category.slug, self.slug)
    
    def get_products(self):
        return Product.objects.filter(category=self)

    def count_visible_products(self):
        return Product.objects.filter(category=self, is_visible=True).count()


class Brand(ImageProcessingMixin, models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, null=True)

    image = models.ImageField(upload_to="uploads/brands/", blank=True, null=True, default='static/images/blank_prodimg.jpg')
    thumbnail = models.ImageField(upload_to="uploads/brands/", blank=True, null=True)

    ordering = models.PositiveSmallIntegerField(default=0)
    country = models.CharField(max_length=255, null=True, blank=True)

    is_on = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'
        indexes = [
            models.Index(fields=['is_on', 'ordering']),
        ]

    def get_products(self):
        return Product.objects.filter(brand=self)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self._is_new_upload('image')
        if is_new:
            self._delete_existing('image', target_name=f'{self.slug}.jpg')
            self._delete_existing('image', target_name=f'{self.slug}_sm.jpg')
            self._delete_existing('image', target_name=f'{self.slug}_md.jpg')
            self.image = self.convert_rgb(self.image, target_name=f'{self.slug}.jpg')
            self._delete_existing('thumbnail', target_name=f'{self.slug}_thumb.jpg')
            self.thumbnail = self.make_thumbnail(self.image, target_name=f'{self.slug}_thumb.jpg')
        super().save(*args, **kwargs)
        if is_new:
            self.generate_variants('image', self.slug)


    def get_absolute_url(self):
        return '/brands/%s/' % (self.slug)


class Product(ImageProcessingMixin, ModelMeta, models.Model):
    tax = 22

    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    sku = models.PositiveSmallIntegerField(blank=False, null=False, unique=True)
    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена с НДС')
    price_wo_tax = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена без НДС')

    is_features = models.BooleanField(default=False)
    is_sale = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    is_in_sales_price = models.BooleanField(default=False, db_index=True)

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
    has_patent = models.BooleanField(default=False)
    is_import = models.BooleanField(default=False, verbose_name='Импортный товар', db_index=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('-created_at','title')
        indexes = [
            models.Index(fields=['category', 'is_visible']),
            models.Index(fields=['brand', 'is_visible']),
            models.Index(fields=['is_features', 'is_visible']),
            models.Index(fields=['is_bestseller', 'is_visible']),
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.title)
        self.set_price_w_tax()
        is_new = self._is_new_upload('image')
        if is_new:
            self._delete_existing('image', target_name=f'{self.slug}.jpg')
            self._delete_existing('image', target_name=f'{self.slug}_sm.jpg')
            self._delete_existing('image', target_name=f'{self.slug}_md.jpg')
            self.image = self.convert_rgb(self.image, target_name=f'{self.slug}.jpg')
            self._delete_existing('thumbnail', target_name=f'{self.slug}_thumb.jpg')
            self.thumbnail = self.make_thumbnail(self.image, target_name=f'{self.slug}_thumb.jpg')
        super().save(*args, **kwargs)
        if is_new:
            self.generate_variants('image', self.slug)

    def set_price_w_tax(self):
        tax_multiplier = Decimal(1) + Decimal(self.tax) / Decimal(100)
        self.price = self.price_wo_tax * tax_multiplier
        self.price = self.price.quantize(Decimal('0.01'))

    def get_absolute_url(self):
        return '/catalog/%s/%s/%s/' % (self.category.main_category.slug, self.category.slug, self.slug)

    def get_patent(self):
        return Patent.objects.filter(product=self)
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
            'price': str(self.price),
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
    varitem = models.ForeignKey(VariableItem, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=['product', 'varitem']),
        ]

    def __str__(self):
        return self.varitem.title


class Patent(ImageProcessingMixin, models.Model):
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
        if self._is_new_upload('image'):
            name = slugify(self.title) if self.title else str(self.pk)
            self._delete_existing('image', target_name=f'{name}.jpg')
            self.image = self.convert_rgb(self.image, target_name=f'{name}.jpg')
        super().save(*args, **kwargs)



    class Meta:
        verbose_name = 'Патент'
        verbose_name_plural = 'Патенты'

    def __str__(self):
        return f'Патент {self.document_number} - {self.title}'


class ProductFAQ(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='faqs', verbose_name='Товар')
    question = models.CharField(max_length=500, verbose_name='Вопрос')
    answer = models.TextField(verbose_name='Ответ')
    ordering = models.PositiveSmallIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'
        ordering = ('ordering',)

    def __str__(self):
        return self.question
