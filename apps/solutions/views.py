from django.shortcuts import render, get_object_or_404
from .models import Industry, CaseStudy


def solutions_index(request):
    """Список всех отраслей."""
    industries = Industry.objects.filter(is_visible=True).order_by('ordering', 'title')
    context = {
        'industries': industries,
        'meta_title': 'Решения для промышленности | Катран-Пневмо',
        'meta_description': 'Пневматические решения для судостроения, металлургии, нефтегаза, машиностроения и других отраслей промышленности. ООО «Катран-Пневмо».',
    }
    return render(request, 'solutions/index.html', context)


def industry_detail(request, slug):
    """Отраслевая страница."""
    industry = get_object_or_404(Industry, slug=slug, is_visible=True)
    cases = CaseStudy.objects.filter(industry=industry, is_visible=True).order_by('ordering', '-created_at')
    context = {
        'industry': industry,
        'cases': cases,
        'meta_title': industry.meta_title or f'{industry.title} — пневматические решения | Катран-Пневмо',
        'meta_description': industry.meta_description or industry.short_description,
        'meta_keywords': industry.meta_keywords,
    }
    return render(request, 'solutions/industry_detail.html', context)


def cases_index(request):
    """Список всех кейсов."""
    cases = CaseStudy.objects.filter(is_visible=True).select_related('industry').order_by('ordering', '-created_at')
    context = {
        'cases': cases,
        'meta_title': 'Проекты и кейсы | Катран-Пневмо',
        'meta_description': 'Реальные проекты: пневматический инструмент для судостроения, металлургии, нефтегаза. Кейсы ООО «Катран-Пневмо».',
    }
    return render(request, 'solutions/cases_index.html', context)


def case_detail(request, slug):
    """Страница кейса."""
    case = get_object_or_404(CaseStudy, slug=slug, is_visible=True)
    related_cases = CaseStudy.objects.filter(
        industry=case.industry, is_visible=True
    ).exclude(pk=case.pk).order_by('ordering')[:3]
    context = {
        'case': case,
        'related_cases': related_cases,
        'meta_title': case.meta_title or f'{case.title} | Катран-Пневмо',
        'meta_description': case.meta_description or case.problem[:200],
    }
    return render(request, 'solutions/case_detail.html', context)
