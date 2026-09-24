from django.core.management.base import BaseCommand

from apps.glossary.models import GlossaryPage
from apps.store.models import Category, Product

from apps.glossary.seed_data_scenarios import SCENARIOS
from apps.glossary.seed_data_guides import GUIDES
from apps.glossary.seed_data_terms import TERMS
from apps.glossary.seed_data_categories import CATEGORIES
from apps.glossary.seed_data_bestsellers_1 import BESTS1
from apps.glossary.seed_data_bestsellers_2 import BESTS2
from apps.glossary.seed_data_katran_1 import KATRAN1
from apps.glossary.seed_data_katran_2 import KATRAN2
from apps.glossary.seed_data_categories_thin import CATS
from apps.glossary.seed_data_categories_b import CATS_B
from apps.glossary.seed_data_categories_c import CATS_C
from apps.glossary.seed_data_models_guides import MODELS, MODELS_GUIDES

ALL_PAGES = SCENARIOS + GUIDES + TERMS + CATEGORIES + BESTS1 + BESTS2 + KATRAN1 + KATRAN2 + CATS + CATS_B + CATS_C + MODELS + MODELS_GUIDES

# Прод-слаги категорий переименованы; seed использует локальные слаги.
CATEGORY_SLUG_ALIASES = {
    'gaikoverty': 'gajkoverty-pnevmaticheskie',
    'molotki-otboinye-i-betonolomy': 'molotki-otbojnye-i-betonolomy-pnevmaticheskie',
    'molotki-rubilnye-i-pnevmozubila': 'molotki-rubilnye-pnevmaticheskie-i-pnevmozubila',
    'perforatory': 'perforatory-pnevmaticheskie',
    'pily': 'pily-pnevmaticheskie',
    'shlifmashiny-orbitalnye': 'shlifmashiny-orbitalnye-pnevmaticheskie',
    'shlifmashiny-radialnye-priamye': 'shlifmashiny-radialnye-pryamye-pnevmaticheskie',
    'shlifmashiny-tortsevye-vertikalnye': 'shlifmashiny-torcevye-vertikalnye-pnevmaticheskie',
    'shlifmashiny-uglovye-pnevmobolgarki': 'shlifmashiny-uglovye-pnevmobolgarki-pnevmaticheskie',
    'trambovki': 'trambovki-pnevmaticheskie',
}


def _resolve_category_slug(categories, seed_slug):
    """Находит slug категории в текущей БД по seed-слагу (прямой или через алиас)."""
    if seed_slug in categories:
        return seed_slug
    prod_slug = CATEGORY_SLUG_ALIASES.get(seed_slug)
    if prod_slug and prod_slug in categories:
        return prod_slug
    return None


def _has_image(product):
    for field in (product.image, product.brand.image if product.brand else None):
        if field:
            try:
                if not field.storage.exists(field.name):
                    return False
            except Exception:
                return False
    return True


class Command(BaseCommand):
    help = 'Наполняет справочник SEO-страницами из seed_data_*.py (сценарии, «как выбрать», wiki, категории).'

    def handle(self, *args, **options):
        products = [p for p in Product.objects.filter(is_visible=True) if _has_image(p)]
        categories = {c.slug: c for c in Category.objects.all()}

        created = updated = skipped = 0

        for data in ALL_PAGES:
            category = None
            if data.get('category_slug'):
                resolved = _resolve_category_slug(categories, data['category_slug'])
                category = categories.get(resolved) if resolved else None
                if category is None:
                    self.stderr.write('Нет категории %s (страница %s) — пропуск' % (
                        data['category_slug'], data['slug']))
                    skipped += 1
                    continue

            page, was_created = GlossaryPage.objects.update_or_create(
                slug=data['slug'],
                defaults={
                    'page_type': data['type'],
                    'title': data['title'],
                    'category': category,
                    'short_description': data['short_description'],
                    'body': data['body'],
                    'faq': data['faq'],
                    'meta_title': data['meta_title'],
                    'meta_description': data['meta_description'],
                    'meta_keywords': data['meta_keywords'],
                    'is_visible': True,
                },
            )

            rel_categories = []
            for slug in (data.get('categories') or data.get('related') or []):
                resolved = _resolve_category_slug(categories, slug)
                if resolved:
                    rel_categories.append(categories[resolved])
            page.related_categories.set(rel_categories)

            wanted = []
            prod_cats = set()
            for token in (data.get('product_categories') or []):
                resolved = _resolve_category_slug(categories, token)
                if resolved:
                    prod_cats.add(resolved)
            for token in data.get('products', []):
                token_l = token.lower()
                for p in products:
                    if token_l in p.title.lower() and p not in wanted:
                        if prod_cats and p.category.slug not in prod_cats:
                            continue
                        wanted.append(p)
            page.related_products.set(wanted)

            if was_created:
                created += 1
            else:
                updated += 1

        self._link_pages()
        self.stdout.write(self.style.SUCCESS(
            'Готово: создано %d, обновлено %d, пропущено %d (всего %d).' % (
                created, updated, skipped, len(ALL_PAGES))))

    def _link_pages(self):
        pages = list(GlossaryPage.objects.filter(is_visible=True).prefetch_related(
            'related_categories', 'related_products'))
        scores = {p.id: {} for p in pages}
        for p in pages:
            p_cats = {c.id for c in p.related_categories.all()}
            p_products = {pr.id for pr in p.related_products.all()}
            for q in pages:
                if q.id == p.id:
                    continue
                q_cats = {c.id for c in q.related_categories.all()}
                s = 2 * len(p_cats & q_cats)
                if p.category_id and p.category_id == q.category_id:
                    s += 4
                s += len(p_products & {pr.id for pr in q.related_products.all()})
                if s == 0:
                    continue
                if q.page_type == p.page_type:
                    s *= 0.6
                scores[p.id][q.id] = s

        top = {}
        for pid, sc in scores.items():
            ranked = sorted(sc.items(), key=lambda kv: -kv[1])[:5]
            top[pid] = {cid for cid, _ in ranked}

        for pid, targets in top.items():
            for cid in targets:
                top.setdefault(cid, set()).add(pid)

        limit = 6
        by_type = {}
        for p in pages:
            by_type.setdefault(p.page_type, []).append(p)
        for pid, targets in top.items():
            if targets:
                continue
            p = GlossaryPage.objects.get(pk=pid)
            fallback = [q.id for q in by_type.get(p.page_type, [])
                        if q.id != pid][:4]
            for cid in fallback:
                top.setdefault(cid, set()).add(pid)
            targets.update(fallback)

        for pid, targets in top.items():
            ranked = sorted(
                targets, key=lambda cid: -scores[pid].get(cid, 0))[:limit]
            page = GlossaryPage.objects.get(pk=pid)
            page.related_pages.set(ranked)
