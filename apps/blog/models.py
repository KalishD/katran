from io import BytesIO
from django.core.files import File
from PIL import Image
from django.db import models

# Create your models here.

class PostCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    class Meta:
        verbose_name_plural = "postcategories"
    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    body = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(PostCategory, on_delete=models.CASCADE)

    image = models.ImageField(upload_to="uploads/posts/", blank=True, null=True, default='static/images/blank_prodimg.jpg')
    thumbnail = models.ImageField(upload_to="uploads/posts/", blank=True, null=True)

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
        return '/%s/%s' % (self.category.slug, self.slug)

    def make_thumbnail(self, image, size=(60, 60)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=80)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail
