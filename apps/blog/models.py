from django.db import models
from apps.store.models import Product, ImageProcessingMixin

class PostCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    class Meta:
        verbose_name_plural = "postcategories"
    def __str__(self):
        return self.name

class Post(ImageProcessingMixin, models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    body = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    postcategory = models.ForeignKey(PostCategory, on_delete=models.CASCADE)

    image = models.ImageField(upload_to="uploads/posts/", blank=True, null=True, default='static/images/blank_prodimg.jpg')
    thumbnail = models.ImageField(upload_to="uploads/posts/", blank=True, null=True)

    linked_products = models.ManyToManyField('store.Product', symmetrical=False, blank=True, related_name='linked_products')

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ('-created_at','title')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.thumbnail = self.make_thumbnail(self.image)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return '/blog/%s' % (self.slug)
