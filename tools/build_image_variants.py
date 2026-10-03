"""Готовит WebP-варианты статических картинок и ужимает явно завышенные исходники.

Зачем:
  * partlist_gear_only.png весит 569 КБ при размере 2553x2552, а выводится
    в боксе Bulma is-16x16, то есть 16x16 пикселей;
  * остальные картинки — обычные фото, для них WebP даёт основную экономию.

Что делает:
  1. для каждой картинки из MANIFEST пишет соседний .webp;
  2. если указан max_px и исходник больше, ужимает И PNG (и .webp) до этого
     размера — fallback тоже не должен быть тяжёлым;
  3. печатает экономию и PSNR, чтобы качество не ухудшилось незаметно.

Запуск (из корня репозитория):
    python tools/build_image_variants.py

Требуется: Pillow с поддержкой WebP (в проекте уже есть, Pillow 10.4).
"""

import os
import shutil
import sys
import tempfile

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(ROOT, 'static')

# (путь внутри static, максимальный размер стороны, quality webp, сжать ли PNG, lossless, цветов)
# max_px=None -> размер не трогаем, только webp
# lossless=True -> точная копия в webp (для иконок с альфа-каналом)
# colors=N -> перед сохранением свести к палитре из N цветов (FASTOCTREE умеет с альфой)
#
# images/kp-logo-text.png обрабатывается ОСОБО: это палитровый PNG 4186x499
# (101 цвет) весом 91054 B, который рисуется максимум 648x77. Просто конвертнуть
# его в webp нельзя - получится 136152 B, хуже оригинала. Помогает только
# связка "уменьшить + свести к палитре": 1300x155 / 128 цветов = 20492 B.
# Сам PNG НЕ трогаем: на него ссылаются og:image и JSON-LD logo, там нужен
# большой файл для краулеров соцсетей.
MANIFEST = [
    # выводится в 16x16: 2553x2552 -> 64x64 это запас 4x для retina
    ('images/icons/partlist_gear_only.png', 64, None, True, True, None),
    ('images/icons/partlist_gear.png', None, None, False, True, None),
    ('images/icons/patent.png', None, None, False, True, None),

    # логотип: 4186x499 -> 1300x155 + палитра 128 (PSNR 41.5 dB)
    ('images/kp-logo-text.png', 1300, None, False, True, 128),

    ('images/frontpage/home-page-banner-cogwheel.jpg', 256, 82, False, False, None),
    ('images/frontpage/home-page-banner-shield.jpg', 256, 82, False, False, None),
    ('images/frontpage/home-page-banner-delivery.jpg', 256, 82, False, False, None),

    ('images/production/mp-006.jpg', None, 82, False, False, None),
    ('images/production/mp-011.jpg', None, 82, False, False, None),
    ('images/production/mps-2215m.jpg', None, 82, False, False, None),
    ('images/production/pvm-12.jpg', None, 82, False, False, None),
    ('images/production/rm.jpg', None, 82, False, False, None),
    ('images/production/tp-28a.jpg', None, 82, False, False, None),
    ('images/production/tpv-3a.jpg', None, 82, False, False, None),
]

MIN_PSNR = 30.0  # dB; ниже 30 разница заметна глазом на фотографии


def psnr(a, b):
    import math
    if a.size != b.size:
        a = a.resize(b.size)
    av = list(a.convert('RGB').tobytes())
    bv = list(b.convert('RGB').tobytes())
    mse = sum((x - y) ** 2 for x, y in zip(av, bv)) / len(av)
    if mse == 0:
        return 99.0
    return 20 * math.log10(255.0) - 10 * math.log10(mse)


def webp_kwargs(img, quality, lossless):
    kw = {'format': 'WEBP', 'method': 6}
    if lossless:
        kw['lossless'] = True
    else:
        kw['quality'] = quality
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        kw['exact'] = True
    return kw


def main():
    backup_dir = os.path.join(tempfile.gettempdir(), 'opencode', 'img-backup')
    os.makedirs(backup_dir, exist_ok=True)

    print('%-46s %10s %10s %10s  %s' % ('FILE', 'WAS', 'PNG NOW', 'WEBP', 'NOTE'))
    print('-' * 96)

    tot_before = tot_after = 0
    problems = []

    for rel, max_px, quality, shrink_png, lossless, colors in MANIFEST:
        src = os.path.join(STATIC, rel.replace('/', os.sep))
        if not os.path.isfile(src):
            problems.append('нет файла: ' + rel)
            continue

        was = os.path.getsize(src)
        # бэкап делаем только один раз: иначе повторный прогон затёр бы
        # оригинал уже сжатой версией
        bak = os.path.join(backup_dir, os.path.basename(rel))
        if not os.path.exists(bak):
            shutil.copy2(src, bak)

        with Image.open(src) as im:
            im.load()
            base = im.copy()
            fmt = im.format
            mode = im.mode
            ow, oh = im.size

        note = ''
        if max_px and (ow > max_px or oh > max_px):
            scale = min(max_px / ow, max_px / oh)
            nw, nh = max(1, round(ow * scale)), max(1, round(oh * scale))
            base = base.resize((nw, nh), Image.LANCZOS)
            note = 'resize %dx%d -> %dx%d' % (ow, oh, nw, nh)
        else:
            nw, nh = ow, oh

        # PNG: перезаписываем только если реально ужимаем
        if shrink_png and (nw, nh) != (ow, oh):
            if fmt == 'PNG':
                out = base
                if out.mode == 'P':
                    out = out.convert('RGBA')
                out.save(src, 'PNG', optimize=True)
            elif fmt in ('JPEG', 'WEBP'):
                base.convert('RGB').save(src, 'PNG', optimize=True)
            note += ' + png shrunk'

        # WebP всегда
        webp_path = os.path.splitext(src)[0] + '.webp'
        wp = base
        if wp.mode == 'P':
            wp = wp.convert('RGBA' if 'transparency' in wp.info else 'RGB')
        elif wp.mode == 'LA':
            wp = wp.convert('RGBA')

        # Сведение к палитре. Нужно там, где исходник палитровый: перевод в
        # RGBA теряет его преимущество, и без квантования webp выходит БОЛЬШЕ
        # оригинала. Считаем PSNR до квантования, иначе метрика всегда 99.
        ref_for_psnr = wp.copy()
        if colors:
            wp = wp.quantize(colors=colors, method=Image.FASTOCTREE,
                             dither=Image.NONE).convert('RGBA')
            note += ' + palette %d' % colors

        wp.save(webp_path, **webp_kwargs(wp, quality, lossless))

        png_now = os.path.getsize(src)
        webp_sz = os.path.getsize(webp_path)
        tot_before += was
        tot_after += png_now + webp_sz

        # контроль качества: webp против того, что увидит пользователь
        with Image.open(webp_path) as w:
            q = psnr(ref_for_psnr, w)
        if q < MIN_PSNR:
            problems.append('низкий PSNR %s: %.1f dB' % (rel, q))

        print('%-46s %10d %10d %10d  %s PSNR=%.1f'
              % (rel[-46:], was, png_now, webp_sz, note, q))

    print()
    print('БЫЛО суммарно            : %10d B' % tot_before)
    print('СТАЛО (png-фолбэк + webp): %10d B' % tot_after)
    if tot_after < tot_before:
        print('ЭКОНОМИЯ                : %10d B (%.1f%%)' % (tot_before - tot_after,
                                                            (tot_before - tot_after) * 100.0 / tot_before))
    else:
        print('ВНИМАНИЕ: вес вырос (это нормально, если webp-фолбэк хранится рядом)')

    if problems:
        print()
        print('ПРОБЛЕМЫ:')
        for x in problems:
            print('  -', x)
        sys.exit(1)
    print()
    print('бэкап оригиналов: %s' % backup_dir)


if __name__ == '__main__':
    main()
