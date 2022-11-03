from io import BytesIO
from django.core.files import File
from PIL import Image
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    ordering = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('ordering',)
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return '/%s' % (self.slug)
    
    def get_products(self):
        return Product.objects.filter(category=self)


class Brand(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, null=True)

    image = models.ImageField(upload_to="uploads/brands/", blank=True, null=True, default='static/images/blank_prodimg.jpg')
    thumbnail = models.ImageField(upload_to="uploads/brands/", blank=True, null=True)

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'
        
    def get_products(self):
        return Product.objects.filter(brand=self)   
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.thumbnail = self.make_thumbnail(self.image)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return '/%s' % (self.slug)
        
    def make_thumbnail(self, image, size=(60, 60)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=80)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.DO_NOTHING, blank=True, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    sku = models.PositiveSmallIntegerField(blank=False, null=False, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    is_features = models.BooleanField(default=False)

    image = models.ImageField(upload_to="uploads/", blank=True, null=True, default='static/images/blank_prodimg.jpg')
    thumbnail = models.ImageField(upload_to="uploads/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add= True)
    variables = models.ManyToManyField('VariableItem', through='Variable', related_name='variables')
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('-created_at','title')
        
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.thumbnail = self.make_thumbnail(self.image)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return '/%s/%s' % (self.category.slug, self.slug)

    def make_thumbnail(self, image, size=(60, 60)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=80)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail

class VariableItem(models.Model):
    title = models.CharField(max_length=255)
    dimention = models.CharField(max_length=255, blank=True, null=True,)
    
    def __str__(self):
        return self.title

class Variable(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    varitem = models.ForeignKey(VariableItem, on_delete=models.DO_NOTHING)
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.varitem.title