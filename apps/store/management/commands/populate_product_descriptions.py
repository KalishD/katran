"""
Management command to fill Product.description for catalog products that have none.

Every sentence is built from data that already exists in the catalog (Variable
rows resolved through Product.get_specs()), so nothing is invented. Products with
no specs at all are reported and skipped rather than given filler text.

Writes go through queryset.update() on the description field only, so
Product.save() (price recalculation, image conversion, slug generation) never
runs.

Usage:
    python manage.py populate_product_descriptions --dry-run
    python manage.py populate_product_descriptions
    python manage.py populate_product_descriptions --category 15
    python manage.py populate_product_descriptions --ids 6807,6810
    python manage.py populate_product_descriptions --with-specs-only
    python manage.py populate_product_descriptions --force
    python manage.py populate_product_descriptions --sample 5
"""
import textwrap

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.html import escape, strip_tags

from apps.store.models import Product


# One sentence per spec, emitted only when that spec exists. Keys match
# SPEC_SLUG_BY_TITLE in apps.store/models.py.
SENTENCES = {
    'disc': 'Рассчитан на абразивный круг диаметром {text}.',
    'spindle': 'Посадка шпинделя — {text}.',
    'rpm': 'Частота вращения — {text}.',
    'power': 'Мощность — {text}.',
    'air_consumption': 'Расход воздуха {text}, поэтому компрессор подбирают с запасом по производительности.',
    'air_pressure': 'Рабочее давление {text}.',
    'air_pressure_max': 'Максимальное давление {text}.',
    'air_inlet': 'Присоединительная резьба штуцера — {text}.',
    'weight': 'Масса {text}.',
    'length': 'Габаритная длина {text}.',
}

# Provenance note: an earlier version appended "Характеристики указаны по
# паспорту изделия." That claim was never verified — specs come from Variable
# rows in the catalog, whose origin is unknown — so it was removed rather than
# softened. Do not reintroduce a source claim not backed by a citable record.
#
# The closing line is also conditional. It previously mentioned a disc diameter
# and compressor on every product, which is meaningless for bushings, nuts and
# fittings. It is now emitted only when the product actually carries pneumatic
# specs, and it only talks about the compressor.
CLOSING_PNEUMATIC = (
    'Если нужен подбор по производительности компрессора — напишите, '
    'поможем рассчитать.'
)

AIR_SPECS = ('air_pressure', 'air_pressure_max', 'air_consumption', 'air_inlet')

INTRO = '{title} — {brand}{category_part}.'


def _join(parts):
    return ' '.join(part for part in parts if part)


class Command(BaseCommand):
    help = 'Fill Product.description for visible products that have no description'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                            help='Overwrite descriptions that already contain text')
        parser.add_argument('--dry-run', action='store_true',
                            help='Show what would change without writing')
        parser.add_argument('--category', type=int, default=0,
                            help='Limit the run to one category id')
        parser.add_argument('--ids', default='',
                            help='Comma-separated product ids to limit the run')
        parser.add_argument('--with-specs-only', action='store_true',
                            help='Skip products that have no specs at all')
        parser.add_argument('--sample', type=int, default=0,
                            help='Print N generated descriptions in full and never write')
        parser.add_argument('--append', action='store_true',
                            help='Append the generated facts to existing text instead of '
                                 'only filling empty descriptions')
        parser.add_argument('--shorter-than', type=int, default=0,
                            help='With --append, only touch descriptions below this length')

    def build_description(self, product):
        specs = product.get_specs()
        if not specs:
            return None

        category_part = ''
        if product.category:
            category_part = f' из категории «{escape(product.category.title)}»'
        brand = escape(product.brand.title) if product.brand else ''

        intro = INTRO.format(
            title=escape(product.title),
            brand=brand,
            category_part=category_part,
        ).rstrip() if brand else f'{escape(product.title)}{category_part}.'

        facts = []
        for slug, template in SENTENCES.items():
            spec = specs.get(slug)
            if spec and spec.get('text'):
                facts.append(template.format(text=escape(spec['text'])))

        closing = ''
        if any(slug in specs for slug in AIR_SPECS):
            closing = CLOSING_PNEUMATIC

        return _join([intro, ' '.join(facts), closing])

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        sample = options['sample']
        append = options['append']
        # --sample is a preview mode: it must never write, with or without --dry-run.
        dry_run = dry_run or bool(sample)

        queryset = Product.objects.filter(is_visible=True).select_related(
            'brand', 'category').prefetch_related('variable_set__varitem')

        if options['category']:
            queryset = queryset.filter(category_id=options['category'])

        ids = [item.strip() for item in options['ids'].split(',') if item.strip()]
        if ids:
            queryset = queryset.filter(pk__in=ids)

        if not force and not append:
            queryset = queryset.filter(Q(description__isnull=True) | Q(description=''))
        elif append and options['shorter_than']:
            queryset = queryset.exclude(description__isnull=True).exclude(
                description__exact='')

        queryset = queryset.order_by('id')

        filled = 0
        skipped_no_specs = 0
        unchanged = 0
        samples = []
        limit = options['shorter_than']

        for product in queryset.iterator(chunk_size=200):
            description = self.build_description(product)
            if not description:
                skipped_no_specs += 1
                continue

            if append:
                current = (product.description or '').strip()
                if limit and len(current) >= limit:
                    unchanged += 1
                    continue
                # Never repeat facts the author already wrote.
                facts = description.split('. ', 1)[-1]
                merged = f'{current} {facts}'.strip()
                if merged == current:
                    unchanged += 1
                    continue
                description = merged

            if sample:
                samples.append((product, description))
                if len(samples) >= sample:
                    break

            if not dry_run:
                Product.objects.filter(pk=product.pk).update(description=description)
            filled += 1

        for product, description in samples:
            self.stdout.write('')
            self.stdout.write(self.style.MIGRATE_HEADING(
                '№%s %s' % (product.pk, product.title)))
            self.stdout.write(textwrap.fill(strip_tags(description), 96))
            self.stdout.write('')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no changes written'))
        if sample and samples:
            self.stdout.write(self.style.SUCCESS(
                'Sample printed for %d product(s); no changes written.' % len(samples)))
            return

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            '%s %d product(s); skipped %d without specs; left as is %d'
            % ('Would fill:' if dry_run else 'Filled:', filled, skipped_no_specs, unchanged)
        ))
