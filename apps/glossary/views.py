from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page

from .models import GlossaryPage

PAGE_LABELS = {
    GlossaryPage.PageType.TERM: 'Словарь терминов',
    GlossaryPage.PageType.SCENARIO: 'Решения под задачи',
    GlossaryPage.PageType.GUIDE: 'Как выбрать',
    GlossaryPage.PageType.CATEGORY: 'Категории',
    GlossaryPage.PageType.MODEL: 'Конкретные модели',
}


@cache_page(60 * 30)  # 30 minutes
def glossary_index(request):
    pages = GlossaryPage.objects.filter(is_visible=True).select_related(
        'category').prefetch_related('related_products', 'related_categories')
    groups = []
    for ptype in GlossaryPage.PageType.choices:
        entry = GlossaryPage.PageType(ptype[0])
        items = [p for p in pages if p.page_type == entry]
        if items:
            groups.append({
                'key': entry,
                'label': PAGE_LABELS.get(entry, entry),
                'items': items,
            })
    context = {
        'groups': groups,
        'keywords': 'пневмоинструмент словарь, какие бывают пневмоинструменты, как выбрать пневмоинструмент, пневмоинструмент для задач',
        'description': 'Справочник по пневмоинструменту: словарь терминов, решения под задачи, руководства «как выбрать». Катран-Пневмо, СПб.',
    }
    return render(request, 'glossary/index.html', context)


@cache_page(60 * 60)  # 1 hour
def glossary_detail(request, slug):
    page = get_object_or_404(
        GlossaryPage.objects.filter(is_visible=True).select_related(
            'category').prefetch_related(
            'related_products__category__main_category',
            'related_products__brand',
            'related_categories__main_category',
            'related_pages'),
        slug=slug,
    )
    faq = page.faq if isinstance(page.faq, list) else []

    context = {
        'page': page,
        'faq': faq,
        'keywords': page.meta_keywords or page.title,
        'description': page.meta_description or page.short_description or page.title,
    }
    return render(request, 'glossary/detail.html', context)