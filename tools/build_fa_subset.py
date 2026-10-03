"""Собирает субсет Font Awesome Free Solid по иконкам, реально используемым в шаблонах.

Зачем: полный fa-solid-900.woff2 весит ~157 КБ и содержит 1969 глифов, из которых
в шаблонах встречается 69. Субсет — ~7.5 КБ. Заодно генерируется CSS, который
ссылается на локальный шрифт вместо CDN.

Запуск (из корня репозитория):
    python tools/build_fa_subset.py

Требуется (только для сборки, не рантайм):
    pip install fonttools brotli

Если в шаблоны добавлена новая иконка Font Awesome — пересобери субсет этой
командой, иначе глиф будет пустым.
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

DEFAULT_CSS_URL = 'https://use.fontawesome.com/releases/v6.6.0/css/all.css'
DEFAULT_FONT_URL = 'https://use.fontawesome.com/releases/v6.6.0/webfonts/fa-solid-900.woff2'
FAMILY = '"Font Awesome 6 Free"'
FONT_WEIGHT = '900'

RULE_RE = re.compile(r'([^{}]+)\{([^{}]*)\}')
CONTENT_RE = re.compile(r'content:\s*"\\([0-9a-fA-F]{1,6})"')
ICON_NAME_RE = re.compile(r'^fa-[a-z0-9-]+$')

# классы-утилиты Font Awesome, а не имена иконок
NOT_ICON_CLASSES = {
    'fa-3x', 'fa-solid', 'fa-spin', 'fa-fw', 'fa-layers', 'fa-ul', 'fa-li',
    'fa-border', 'fa-pull-left', 'fa-pull-right',
}


def download(url, dest):
    req = urllib.request.Request(url, headers={'User-Agent': 'katran-fa-subset'})
    with urllib.request.urlopen(req, timeout=90) as r, open(dest, 'wb') as f:
        f.write(r.read())
    return dest


def collect_used_classes(template_roots):
    found = set()
    for root in template_roots:
        for path in glob.glob(os.path.join(root, '**', '*.html'), recursive=True):
            text = open(path, encoding='utf-8', errors='ignore').read()
            found.update(re.findall(r'\bfa-[a-z0-9-]+\b', text))
    return found


def parse_css(css):
    """-> (code_points, icon_rules, utility_rules)"""
    code_points, icon_rules, utility_rules = {}, [], []
    for m in RULE_RE.finditer(css):
        selectors, body = m.group(1).strip(), m.group(2).strip()
        if selectors.startswith('@'):
            continue
        cm = CONTENT_RE.search(body)
        parts = [x.strip() for x in selectors.split(',')]
        names = [x[:-7].strip().lstrip('.') if x.endswith(':before') else None for x in parts]
        icon_names = [n for n in names if n and ICON_NAME_RE.match(n)]
        if cm and icon_names:
            for sel, name in zip(parts, names):
                if name and ICON_NAME_RE.match(name):
                    code_points[name] = int(cm.group(1), 16)
            icon_rules.append((parts, cm.group(1), icon_names))
        else:
            utility_rules.append('%s{%s}' % (selectors, body))
    return code_points, icon_rules, utility_rules


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--templates', nargs='+', default=['apps'])
    ap.add_argument('--out-css', default='static/css/fontawesome-subset.css')
    ap.add_argument('--out-font', default='static/fonts/fa-solid-subset.woff2')
    ap.add_argument('--css-url', default=DEFAULT_CSS_URL)
    ap.add_argument('--font-url', default=DEFAULT_FONT_URL)
    ap.add_argument('--keep-versions', default='')
    ap.add_argument('--keep-downloads', action='store_true')
    args = ap.parse_args()

    try:
        import fontTools  # noqa: F401
        import brotli     # noqa: F401
    except ImportError:
        sys.exit('Нужны fonttools и brotli:  pip install fonttools brotli')

    tmp = tempfile.mkdtemp(prefix='fa-subset-')
    css_path = download(args.css_url, os.path.join(tmp, 'all.css'))
    font_path = download(args.font_url, os.path.join(tmp, 'fa-solid-900.woff2'))
    css = open(css_path, encoding='utf-8').read()

    used = collect_used_classes(args.templates)
    code_points, icon_rules, utility_rules = parse_css(css)

    wanted = sorted(c for c in used if c not in NOT_ICON_CLASSES and c in code_points)
    unknown = sorted(c for c in used if c not in NOT_ICON_CLASSES and c not in code_points)
    if unknown:
        print('ВНИМАНИЕ: нет в CSS Font Awesome:', unknown)

    codepoints = sorted({code_points[c] for c in wanted})
    unicodes = ','.join('U+%04X' % c for c in codepoints)

    # --- субсет шрифта ---
    tmp_font = os.path.join(tmp, 'subset.woff2')
    cmd = [
        sys.executable, '-m', 'fontTools.subset', font_path,
        '--unicodes=' + unicodes,
        '--flavor=woff2',
        '--output-file=' + tmp_font,
        '--layout-features=',
        '--no-hinting',
        '--desubroutinize',
        '--name-IDs=',
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('fontTools.subset failed:\n' + r.stderr[-2000:])

    # --- CSS ---
    wanted_set = set(wanted)
    icon_css = []
    for parts, cp, names in icon_rules:
        keep = [s for s, n in zip(parts, names) if n in wanted_set]
        if keep:
            # parts уже содержит ':before' — дописывать второй раз нельзя
            assert all(s.endswith(':before') for s in keep), keep
            icon_css.append('%s{content:"\\%s"}' % (','.join(keep), cp))

    font_name = os.path.basename(args.out_font)
    head = [
        '/* Font Awesome Free 6.6.0 - solid subset, %d глифов.' % len(codepoints),
        '   Сгенерировано tools/build_fa_subset.py. Правь шрифт, а не этот файл.',
        '   После добавления новой иконки в шаблоны запусти скрипт заново. */',
        '@font-face{font-family:%s;font-style:normal;font-weight:%s;font-display:block;'
        'src:url("../fonts/%s") format("woff2")}' % (FAMILY, FONT_WEIGHT, font_name),
        '/* bare .fa (наследие v4) тоже должен брать solid-шрифт */',
        '.fa,.fas,.fa-solid{font-family:%s;font-weight:%s}' % (FAMILY, FONT_WEIGHT),
    ]
    out = '\n'.join(head) + '\n' + '\n'.join(utility_rules) + '\n' + '\n'.join(icon_css) + '\n'

    for path, content in ((args.out_css, out), (args.out_font, None)):
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)

    with open(args.out_css, 'w', encoding='utf-8') as f:
        f.write(out)
    with open(args.out_font, 'wb') as f:
        f.write(open(tmp_font, 'rb').read())

    # самопроверка результата: ловим именно тот баг с :before:before
    written = open(args.out_css, encoding='utf-8').read()
    problems = []
    if ':before:before' in written:
        problems.append('двойной :before в CSS')
    if written.count(':before{content:') != len(codepoints):
        problems.append('правил-иконок %d, ожидалось %d (уникальных кодпоинтов)'
                        % (written.count(':before{content:'), len(codepoints)))
    if written.count('@font-face') != 1:
        problems.append('@font-face должен быть ровно один')
    for c in wanted:
        if 'content:"\\%x"' % code_points[c] not in written:
            problems.append('нет кодпоинта для %s (U+%04X)' % (c, code_points[c]))
    if problems:
        print('САМОПРОВЕРКА НЕ ПРОЙДЕНА:')
        for x in problems:
            print('  -', x)
        sys.exit(1)

    from fontTools.ttLib import TTFont
    got = TTFont(args.out_font).getBestCmap()
    lost = ['U+%04X' % c for c in codepoints if c not in got]

    size_css = os.path.getsize(args.out_css)
    size_font = os.path.getsize(args.out_font)
    print('иконок использовано   : %d (кодпоинтов %d)' % (len(wanted), len(codepoints)))
    print('исходный шрифт        : %9d B' % os.path.getsize(font_path))
    print('исходный all.css      : %9d B' % len(css.encode('utf-8')))
    print('новый шрифт           : %9d B  -> %s' % (size_font, args.out_font))
    print('новый CSS             : %9d B  -> %s' % (size_css, args.out_css))
    print('было суммарно         : %9d B' % (os.path.getsize(font_path) + len(css.encode('utf-8'))))
    print('стало суммарно        : %9d B' % (size_font + size_css))
    if lost:
        print('ПОТЕРЯНЫ ГЛИФЫ:', lost)
        sys.exit(1)
    print('все глифы на месте')

    if not args.keep_downloads:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
