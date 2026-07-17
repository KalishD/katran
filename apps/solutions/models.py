from django.db import models
from django.utils.text import slugify
from django_summernote.fields import SummernoteTextField


class Industry(models.Model):
    """Отраслевая страница — решений для конкретной отрасли."""

    title = models.CharField(max_length=255, verbose_name='Название отрасли')
    slug = models.SlugField(max_length=255, unique=True)
    icon_class = models.CharField(
        max_length=64, blank=True, default='',
        verbose_name='CSS-класс иконки (FontAwesome)',
        help_text='Например: fa-solid fa-ship'
    )
    short_description = models.TextField(
        blank=True, default='',
        verbose_name='Краткое описание (для карточки)'
    )
    description = SummernoteTextField(
        blank=True, default='',
        verbose_name='Полное описание (HTML)'
    )
    # Какой инструмент рекомендуется для этой отрасли
    recommended_tools = models.TextField(
        blank=True, default='',
        verbose_name='Рекомендуемый инструмент',
        help_text='Текст или HTML со списком рекомендуемых категорий'
    )
    # Связь с категориями каталога
    related_categories = models.ManyToManyField(
        'store.Category', blank=True,
        verbose_name='Связанные категории каталога'
    )
    # SEO
    meta_title = models.CharField(max_length=255, blank=True, default='', verbose_name='Meta Title')
    meta_description = models.CharField(max_length=500, blank=True, default='', verbose_name='Meta Description')
    meta_keywords = models.CharField(max_length=500, blank=True, default='', verbose_name='Meta Keywords')

    ordering = models.PositiveSmallIntegerField(default=0, verbose_name='Порядок')
    is_visible = models.BooleanField(default=True, verbose_name='Видимость')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Отрасль'
        verbose_name_plural = 'Отрасли'
        ordering = ('ordering', 'title')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/solutions/{self.slug}/'


class CaseStudy(models.Model):
    """Кейс — реальный проект / история клиента."""

    title = models.CharField(max_length=255, verbose_name='Название кейса')
    slug = models.SlugField(max_length=255, unique=True)
    industry = models.ForeignKey(
        Industry, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Отрасль'
    )
    client_name = models.CharField(
        max_length=255, blank=True, default='',
        verbose_name='Название клиента (если можно показать)'
    )
    problem = models.TextField(verbose_name='Задача / Проблема')
    solution = models.TextField(verbose_name='Наше решение')
    result = models.TextField(
        blank=True, default='',
        verbose_name='Результат'
    )
    body = SummernoteTextField(
        blank=True, default='',
        verbose_name='Подробное описание (HTML)'
    )
    # Фотографии проекта
    image = models.ImageField(
        upload_to='uploads/case_studies/', blank=True, null=True,
        verbose_name='Главное фото'
    )
    # Связь с продуктами
    related_products = models.ManyToManyField(
        'store.Product', blank=True,
        verbose_name='Задействованные продукты'
    )
    # Метрики
    metric_label = models.CharField(
        max_length=128, blank=True, default='',
        verbose_name='Метрика (напр. «Рост производительности»)'
    )
    metric_value = models.CharField(
        max_length=64, blank=True, default='',
        verbose_name='Значение метрики (напр. «27%»)'
    )

    # SEO
    meta_title = models.CharField(max_length=255, blank=True, default='', verbose_name='Meta Title')
    meta_description = models.CharField(max_length=500, blank=True, default='', verbose_name='Meta Description')

    ordering = models.PositiveSmallIntegerField(default=0, verbose_name='Порядок')
    is_visible = models.BooleanField(default=True, verbose_name='Видимость')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Кейс'
        verbose_name_plural = 'Кейсы'
        ordering = ('ordering', '-created_at')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/solutions/cases/{self.slug}/'
