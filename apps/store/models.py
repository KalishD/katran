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


# Canonical spec slugs, matched case-insensitively against VariableItem.title.
# Adding a key here makes the spec available to templates and the API payloads
# without touching views.
#
# Several VariableItem titles describe the same physical quantity; they are
# aliased onto one slug rather than renamed in the database, so the admin
# keeps whatever wording the supplier used. ``Product.get_specs()`` keeps the
# lowest-id row per slug when a product carries more than one alias.
#
# 'производитель' is deliberately absent: it duplicates Product.brand and is
# unused by every product.
SPEC_SLUG_BY_TITLE = {
    # --- габариты и общие ---
    'номинальная мощность': 'power',
    'вес': 'weight',
    'длина': 'length',
    'габаритные размеры': 'dimensions',
    'ширина': 'width',
    'высота': 'height',
    'ширина рабочей части шарошки': 'plate_width',
    'размер рабочей поверхности': 'pad_size',
    'число звездочек шарошки': 'plate_sprockets',
    'диапазон рабочих температур': 'temperature_range',

    # --- вращение и привод ---
    'частота вращения шпинделя на холостом ходу': 'rpm',
    'частота вращения на холостом ходу': 'rpm',
    'частота вращения (правое / левое)': 'rpm',
    'частота колебаний': 'oscillation_rate',
    'статический момент дебаланса': 'balance_momentum',
    'передаточное отношение': 'gear_ratio',
    'шпиндель': 'spindle',
    'резьба': 'thread',
    'резьба шпинделя': 'spindle_thread',
    'вылет шпинделя': 'spindle_projection',
    'реверс': 'reverser',

    # --- ударные ---
    'энергия удара': 'impact_energy',
    'частота удара': 'impact_rate',
    'крутящий момент': 'torque',
    'макс. момент затяжки': 'torque',
    'макс. крутящий момент': 'torque',
    'квадрат': 'drive_square',

    # --- пневмосеть и цилиндр ---
    'расход воздуха': 'air_consumption',
    'рабочее давление': 'air_pressure',
    'максимальное давление воздуха': 'air_pressure_max',
    'присоединительная резьба штуцера': 'air_inlet',
    'диаметр сопла': 'nozzle_diameter',
    'внутренний диаметр шланга': 'hose_inner_diameter',
    'диаметр поршня': 'piston_diameter',
    'ход поршня': 'stroke',
    'величина хода телескопического податчика': 'feed_extension',

    # --- хвостовик и патрон ---
    'тип хвостовика': 'shank_type',
    'диаметр хвостовика': 'shank_diameter',
    'длина хвостовика': 'shank_length',
    'тип сверлильного патрона': 'chuck_type',
    'диаметр цанги': 'chuck_diameter',

    # --- оснастка и ёмкости ---
    'диаметр абразивного инструмента': 'disc',
    'диаметр проволочной щетки': 'wire_brush_diameter',
    'диаметр башмака': 'shoe_diameter',
    'диаметр заклепки': 'rivet_diameter',
    'диаметр': 'diameter',
    'макс. диаметр сверла': 'drill_capacity',
    'макс. диаметр бурения': 'bore_capacity',
    'макс. глубина бурения': 'bore_depth',
    'макс. диаметр бор-фрезы': 'boring_cutter_capacity',
    'макс. диаметр головки': 'head_capacity',
    'макс. диаметр шлиф. головки': 'grinder_head_capacity',
    'макс. диаметр затягиваемой резьбы': 'thread_capacity',
    'макс. диаметр нарезаемой резьбы': 'threading_capacity',
    'емкость бачка': 'tank_capacity',
}

# Card strip: ordered (slug, label) pairs plus a hard cap. The first five
# entries are the compressor question every buyer of a pneumatic tool asks;
# the rest fill the leftover slot on tools that have no disc or rpm.
# Order is priority: SPEC_CARD_LIMIT cuts the tail, so raising the limit
# never reshuffles what is already shown.
SPEC_CARD_ROWS = (
    ('disc', 'Ø'),
    ('rpm', ''),
    ('air_consumption', 'воздух'),
    ('air_pressure', 'давл.'),
    ('air_inlet', 'штуцер'),
    ('impact_energy', 'энергия'),
    ('impact_rate', 'частота'),
    ('torque', 'момент'),
    ('shank_diameter', 'хвост. Ø'),
    ('shank_length', 'хвост. L'),
    ('shank_type', 'тип хвост.'),
    ('stroke', 'ход'),
    ('drive_square', 'квадрат'),
)
SPEC_CARD_LIMIT = 5


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
        """Get URL for a resized variant (e.g. _sm, _md). Empty if variant file is missing."""
        field = getattr(self, field_name)
        if not field or not field.name:
            return ''
        storage = field.storage
        name = field.name
        base, ext = os.path.splitext(name)
        variant_name = f'{base}_{suffix}{ext}'
        try:
            if storage.exists(variant_name):
                return storage.url(variant_name)
        except Exception:
            return ''
        return ''

    def get_srcset(self, field_name='image', widths=None):
        """Build srcset string with only existing variant files. Always includes original."""
        widths = widths or [('sm', 400), ('md', 800)]
        field = getattr(self, field_name)
        if not field or not field.name:
            return ''
        parts = []
        for suffix, width in widths:
            vurl = self.get_resized_url(field_name, suffix)
            if vurl:
                parts.append(f'{vurl} {width}w')
        parts.append(f'{field.url} 1200w')
        return ', '.join(parts)

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
    is_one_piece_price = models.BooleanField(default=False)
    image = models.ImageField(upload_to="uploads/categories/", blank=True, null=True, default='static/images/blank_prodimg.jpg', max_length=255)

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

    image = models.ImageField(upload_to="uploads/brands/", blank=True, null=True, default='static/images/blank_prodimg.jpg', max_length=255)
    thumbnail = models.ImageField(upload_to="uploads/brands/", blank=True, null=True, max_length=255)

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

    image = models.ImageField(upload_to="uploads/products/", blank=True, null=True, default='static/images/blank_prodimg.jpg', max_length=255)
    partlist = models.ImageField(upload_to="uploads/products/partlists/", blank=True, null=True, max_length=255)
    thumbnail = models.ImageField(upload_to="uploads/products/thumb/", blank=True, null=True, max_length=255)

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
        'category': 'get_schema_category',
        'additionalProperty': 'get_schema_properties',
    }

    def get_schema_properties(self):
        """Schema.org PropertyValue rows built from the real spec data."""
        return [
            {'@type': 'PropertyValue', 'name': spec['title'], 'value': spec['text']}
            for spec in self.get_specs().values()
        ]

    @property
    def schema(self):
        """Product JSON-LD node, with empty values omitted.

        django-meta's default ``schema`` includes a key even when the resolver
        returns ``None``, which emits ``"offers": null`` for price-on-request
        products. That is invalid Schema.org, so build the node here instead and
        skip anything that resolved to nothing.
        """
        node = {}
        for field, value in self._schema.items():
            if not value:
                continue
            resolved = self._get_meta_value(field, value)
            if resolved in (None, '', [], {}):
                continue
            node[field] = resolved
        node.setdefault('@type', 'Product')
        return node

    def get_schema_description(self):
        variables_list = ''
        for var in self.variable_set.all():
            unit = var.varitem.dimention or ''
            variables_list += f'{var.value}{unit}; '

        article = strip_tags(self.article).strip() if self.article else ''
        parts = [self.title]
        if article:
            parts.append(article)
        if variables_list.strip('; '):
            parts.append(f'Характеристики: {variables_list.strip("; ")}')
        return '; '.join(parts)

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

        Для товаров с нулевой ценой (цена по запросу) Offer не возвращается:
        публиковать price="0.00" неверно, это ломает валидность Product в Schema.org.
        """
        if not self.price:
            return None
        return {
            '@context': 'https://schema.org/',
            '@type': 'Offer',
            'url': self.build_absolute_uri(self.get_absolute_url()),
            'name': self.title,
            'priceCurrency': 'RUB', # Установите валюту, например, 'RUB' или 'USD'
            'price': str(self.price),
            'itemCondition': 'https://schema.org/NewCondition',
            'availability': self.get_schema_availability(),
        }

    def get_schema_availability(self):
        if self.in_stock == 1:
            return 'https://schema.org/InStock'
        if self.in_stock == 0:
            return 'https://schema.org/BackOrder'
        return 'https://schema.org/PreOrder'

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

    def get_specs(self):
        """Canonical specs used by cards, the compressor block and JSON-LD.

        Keyed by a stable slug instead of VariableItem pk, because pks differ
        between databases. Memoised per instance because ``variable_set`` is
        already prefetched by the views.
        """
        cached = getattr(self, '_specs_cache', None)
        if cached is not None:
            return cached

        specs = {}
        # Sorted in Python, not via .order_by(): once ``variable_set`` is
        # prefetched Django serves the cached list and drops the ordering.
        for var in sorted(self.variable_set.all(), key=lambda v: v.varitem_id):
            slug = SPEC_SLUG_BY_TITLE.get((var.varitem.title or '').strip().lower())
            if not slug or slug in specs:
                continue
            specs[slug] = {
                'value': var.value,
                'unit': var.varitem.dimention or '',
                'text': f'{var.value} {var.varitem.dimention or ""}'.strip(),
                'title': var.varitem.title,
            }

        self._specs_cache = specs
        return specs

    def get_spec_rows(self):
        """Ordered, display-ready pairs for the card strip.

        Single source of truth for both the SSR render and the Vue listing, so
        the two branches cannot drift apart (they did once, when the unit was
        hardcoded in the template on top of the already-joined spec text).
        Capped by SPEC_CARD_LIMIT to hold the strip to one line, which is what
        keeps the price blocks aligned across a row of cards.
        """
        cached = getattr(self, '_spec_rows_cache', None)
        if cached is not None:
            return cached

        specs = self.get_specs()
        rows = []
        for slug, label in SPEC_CARD_ROWS:
            spec = specs.get(slug)
            if not spec or not spec['text']:
                continue
            rows.append({
                'slug': slug,
                'label': label,
                'prefix': f'{label} ' if label else '',
                'text': spec['text'],
            })
            if len(rows) >= SPEC_CARD_LIMIT:
                break

        self._spec_rows_cache = rows
        return rows

    def get_spec(self, slug):
        return self.get_specs().get(slug)

    def get_compressor_requirements(self):
        """Compressor match block: rows plus a derived receiver hint.

        This is the single most useful block for a pneumatic tool buyer. The
        catalog data already carries air consumption, working pressure and the
        inlet thread, and no competitor surfaces them together.
        """
        specs = self.get_specs()
        rows = []
        for slug in ('air_pressure', 'air_consumption', 'air_inlet', 'air_pressure_max'):
            spec = specs.get(slug)
            if spec and spec['value']:
                rows.append(spec)

        consumption = specs.get('air_consumption')
        hint = ''
        if consumption:
            raw = (consumption['value'] or '').replace(',', '.').replace(' ', '')
            try:
                lit_min = float(raw)
            except ValueError:
                lit_min = None
            if lit_min:
                # Compressor must exceed sustained tool draw; pad for duty cycle.
                # Receiver size is deliberately NOT estimated here: it depends on
                # the duty cycle, which we cannot know from catalog data.
                needed = lit_min * 1.2
                needed_out = int(needed / 50.0 + 0.5) * 50

                # State the bar figure only when the catalog actually has it,
                # so the hint never contradicts the product specs above it.
                pressure = specs.get('air_pressure')
                bar = ''
                if pressure:
                    try:
                        mpa = float(str(pressure['value']).replace(',', '.'))
                        value = '{:.1f}'.format(mpa * 10).rstrip('0').rstrip('.')
                        bar = f' и {value.replace(".", ",")} бар'
                    except (TypeError, ValueError):
                        bar = ''

                hint = (
                    f'Ориентир по компрессору — от {needed_out} л/мин{bar}. '
                    f'Для импульсной работы (зачистка швов, короткие проходы) '
                    f'ресивер 50–100 л загладит просадку давления. '
                    f'Точный подбор сделаем под ваше оборудование — пришлите модель компрессора.'
                )

        return {
            'rows': rows,
            'has_data': bool(rows),
            'consumption': consumption,
            'hint': hint,
        }

        
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
    image = models.ImageField(upload_to='uploads/patents/', blank=True, null=True, verbose_name='Схема', max_length=255)
    document_image = models.ImageField(upload_to='uploads/patents/', blank=True, null=True, verbose_name='Бланк патента', max_length=255)
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


class PriceRequestQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(is_handled=False)


class PriceRequest(models.Model):
    """Lead captured from the «Запросить цену» button.

    45 of 356 visible products have no price, so this is the only conversion
    path for them. The row is stored before the email is sent: a mail failure
    must never lose the lead.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='price_requests', verbose_name='Товар')
    name = models.CharField(max_length=150, verbose_name='Имя')
    email = models.EmailField(max_length=254, verbose_name='E-mail')
    phone = models.CharField(max_length=40, blank=True, default='', verbose_name='Телефон')
    comment = models.TextField(blank=True, default='', verbose_name='Комментарий')
    source_url = models.URLField(max_length=500, blank=True, default='', verbose_name='Страница')
    is_handled = models.BooleanField(default=False, verbose_name='Обработан')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    objects = PriceRequestQuerySet.as_manager()

    class Meta:
        verbose_name = 'Запрос цены'
        verbose_name_plural = 'Запросы цены'
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['is_handled', '-created_at']),
        ]

    def __str__(self):
        return f'№{self.pk} {self.product_id} — {self.name}'

    def get_specs_summary(self):
        return ', '.join(
            f"{spec['title']}: {spec['text']}" for spec in self.product.get_specs().values()
        )

    def send_office_email(self):
        """Notify the sales office. Caller decides how to handle failures."""
        from django.conf import settings
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags

        recipient = getattr(settings, 'ORDER_EMAIL_RECIPIENT', 'office@katran-pnevmo.ru')
        context = {
            'request': self,
            'product': self.product,
            'specs_summary': self.get_specs_summary(),
        }
        html_message = render_to_string('emails/price_request.html', context)
        subject = f'Запрос цены №{self.pk}: {self.product.title}'
        send_mail(
            subject,
            strip_tags(html_message),
            from_email=None,
            recipient_list=[recipient],
            html_message=html_message,
            fail_silently=True,
        )
