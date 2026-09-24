from django.db import models


class GlossaryPage(models.Model):
    """pSEO-страница справочника: wiki-термин, сценарий, «как выбрать», SEO-текст категории."""

    class PageType(models.TextChoices):
        TERM = 'term', 'Wiki-термин / глоссарий'
        SCENARIO = 'scenario', 'Сценарий / задача'
        GUIDE = 'guide', 'Как выбрать'
        CATEGORY = 'category', 'SEO-текст категории'
        MODEL = 'model', 'Конкретная модель / бестселлер'

    page_type = models.CharField(
        max_length=20, choices=PageType.choices, default=PageType.TERM,
        verbose_name='Тип страницы')
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='Slug')

    category = models.ForeignKey(
        'store.Category', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Связанная категория (для SEO-текста категории)')

    short_description = models.TextField(
        blank=True, default='',
        verbose_name='Краткое описание (для карточки в списке)')

    body = models.TextField(
        blank=True, default='',
        verbose_name='Основной контент (HTML)')

    faq = models.JSONField(
        blank=True, default=list,
        verbose_name='FAQ (JSON: [{"q": "...", "a": "..."}])')

    related_products = models.ManyToManyField(
        'store.Product', blank=True,
        verbose_name='Связанные товары')
    related_categories = models.ManyToManyField(
        'store.Category', blank=True, related_name='glossary_pages',
        verbose_name='Связанные категории каталога')

    related_pages = models.ManyToManyField(
        'self', blank=True, symmetrical=False,
        verbose_name='Связанные страницы справочника')

    meta_title = models.CharField(max_length=255, blank=True, default='', verbose_name='Meta Title')
    meta_description = models.CharField(max_length=500, blank=True, default='', verbose_name='Meta Description')
    meta_keywords = models.CharField(max_length=500, blank=True, default='', verbose_name='Meta Keywords')

    ordering = models.PositiveSmallIntegerField(default=0, verbose_name='Порядок')
    is_visible = models.BooleanField(default=True, verbose_name='Видимость')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Страница справочника'
        verbose_name_plural = 'Страницы справочника'
        ordering = ('page_type', 'ordering', 'title')
        indexes = [
            models.Index(fields=['page_type', 'is_visible']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/glossary/%s/' % (self.slug)