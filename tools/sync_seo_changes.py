# -*- coding: utf-8 -*-
"""
Перенос SEO/контентных изменений dev -> prod БД.

Использование:
  1) На dev (sqlite):  python manage.py shell-скрипт не нужен — запускать как
                       .\env\Scripts\python.exe tools\sync_seo_changes.py export changes.json
  2) На prod (mysql):  python tools/sync_seo_changes.py apply changes.json

Команда export снимает с текущей (БЕЗ ДОМАШНЕЙ) БД:
  - article для запчастей с артикулом из названия (паттерн МОП/ПТ-28А/ТП-28А/ИП-2203/ИП-4112);
  - article для лопаток (явный список sku);
  - description категорий (длина > 60 после strip тегов);
  - товар ЗПШМ-1И целиком (для создания на проде).

Команда apply применяет json по ключам sku (продукты) / slug (категории),
создавая ЗПШМ-1И, если его нет.
"""
import argparse
import json
import os
import re
import sys

import django
from decimal import Decimal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "katran.settings")
django.setup()

from django.db import transaction

from apps.store.models import Brand, Category, Product


def jnum(v):
    if isinstance(v, Decimal):
        return str(v)
    return v


def strip_html(text):
    return " ".join(re.sub(r"<[^>]+>", " ", text or "").split())


# ---- Export (dev) -------------------------------------------------------

SPARE_PART_RE = re.compile(r"^(МОП[2-4]?-\d+|МОП2-\d+[-\d]?|МОП-\d-\d|МОП[2-4]-\d+[-\d]?|"
                           r"ПТ-28А\.\d{2}\.\d{2}|ТП-28А\.\d{2}\.\d{2}(?:\.\d+)?|"
                           r"ИП-2203\.\d+|ИП-4112\.\d+|ИП-4126\.\d+)")

# Лопатки, заполненные вручную по данным поставщика: sku -> article
VANES = {
    6315: "121489",
    6614: "SJ180",
    5719: "121231",
    6017: "121488",
    6262: "ИП-2009-047",
    474: "МПС-2215М.010.05",
    2671: "ИП-2014-016",
}

ZPSHM_SKU = 6949


def cmd_export(args):
    articles = []
    for p in Product.objects.filter(is_visible=True, article__isnull=False).exclude(article=""):
        if SPARE_PART_RE.match(p.article) or p.sku in VANES:
            articles.append({"sku": p.sku, "article": p.article, "title": p.title})

    cats = []
    for c in Category.objects.all().select_related("main_category"):
        if len(strip_html(c.description)) > 60:
            cats.append({
                "slug": c.slug,
                "main_slug": c.main_category.slug if c.main_category else None,
                "description": c.description,
            })

    zpshm = None
    try:
        p = Product.objects.get(sku=ZPSHM_SKU)
        zpshm = {
            "title": p.title,
            "slug": p.slug,
            "sku": p.sku,
            "article": p.article,
            "price": jnum(p.price),
            "price_wo_tax": jnum(p.price_wo_tax),
            "in_stock": p.in_stock,
            "is_visible": p.is_visible,
            "is_features": p.is_features,
            "is_bestseller": p.is_bestseller,
            "image": p.image.name if p.image else None,
            "brand": p.brand.title if p.brand else None,
            "category": p.category.slug if p.category else None,
            "description": p.description,
            "keywords": p.keywords,
            "ordering": p.ordering,
            "has_patent": p.has_patent,
            "is_import": p.is_import,
        }
    except Product.DoesNotExist:
        pass

    payload = {"articles": articles, "categories": cats, "zpshm": zpshm}
    with open(args.file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"exported: articles={len(articles)} cats={len(cats)} zpshm={bool(zpshm)} -> {args.file}")


# ---- Apply (prod) -------------------------------------------------------

def cmd_apply(args):
    with open(args.file, encoding="utf-8") as f:
        payload = json.load(f)

    updated_art = 0
    for item in payload.get("articles", []):
        p = Product.objects.filter(sku=item["sku"]).first()
        if p is None:
            print(f"SKIP article: sku {item['sku']} not found [{item.get('title', '')}]")
            continue
        if p.article != item["article"]:
            p.article = item["article"]
            p.save(update_fields=["article"])
            updated_art += 1

    updated_cat = 0
    for cat in payload.get("categories", []):
        qs = Category.objects.filter(slug=cat["slug"])
        if cat.get("main_slug"):
            qs = qs.filter(main_category__slug=cat["main_slug"])
        c = qs.first()
        if c is None:
            print(f"SKIP category: slug {cat['slug']} not found")
            continue
        if c.description != cat["description"]:
            c.description = cat["description"]
            c.save(update_fields=["description"])
            updated_cat += 1

    zpshm = None
    with transaction.atomic():
        z = payload.get("zpshm")
        if z:
            p = Product.objects.filter(sku=z["sku"]).first()
            brand = Brand.objects.filter(title=z.get("brand")).first() if z.get("brand") else None
            category = Category.objects.filter(slug=z.get("category")).first() if z.get("category") else None
            if brand is None and z.get("brand"):
                print(f"SKIP zpshm: brand '{z.get('brand')}' not found")
            elif category is None and z.get("category"):
                print(f"SKIP zpshm: category '{z.get('category')}' not found")
            else:
                if p is None:
                    p = Product(sku=z["sku"])
                    print(f"CREATE zpshm: new product sku {z['sku']}")
                for fld in ("title", "slug", "article", "description", "keywords", "ordering",
                            "in_stock", "is_visible", "is_features", "is_bestseller",
                            "has_patent", "is_import"):
                    setattr(p, fld, z[fld])
                p.price = Decimal(z["price"] or "0")
                p.price_wo_tax = Decimal(z["price_wo_tax"] or "0")
                p.brand = brand
                p.category = category
                if z.get("image"):
                    p.image = z["image"]
                p.save()
                zpshm = p.sku

    print(f"applied: articles={updated_art} cats={updated_cat} zpshm={zpshm}")


def main():
    parser = argparse.ArgumentParser(description="Sync SEO/promo changes dev->prod")
    sub = parser.add_subparsers(dest="cmd", required=True)
    ex = sub.add_parser("export")
    ex.add_argument("file")
    ap = sub.add_parser("apply")
    ap.add_argument("file")
    args = parser.parse_args()
    if args.cmd == "export":
        cmd_export(args)
    else:
        cmd_apply(args)


if __name__ == "__main__":
    main()