---
name: Katran-Pnevmo
description: Интернет-магазин пневматического инструмента для B2B
colors:
  primary: "#5B93C1"
  primary-deep: "#485FC7"
  accent: "#e41817"
  accent-warm: "#f1ac2b"
  neutral-bg: "#f5f6fa"
  neutral-surface: "#f8f6fc"
  neutral-ink: "#09131f"
  neutral-muted: "#676f79"
  neutral-border: "rgba(72, 95, 199, 0.125)"
  dark: "#34495e"
  dark-footer: "#1e272e"
  success: "#48c78e"
  info: "#5B93C1"
  light-green: "#81ecec"
  light-blue: "#74b9ff"
  lavender: "rgba(150, 176, 199, 1)"
typography:
  display:
    fontFamily: "BlinkMacSystemFont, -apple-system, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif"
    fontSize: "clamp(1.5rem, 2.5vw + 0.5rem, 2.25rem)"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  body:
    fontFamily: "BlinkMacSystemFont, -apple-system, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  label:
    fontFamily: "BlinkMacSystemFont, -apple-system, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.02em"
rounded:
  sm: "4px"
  md: "6px"
  lg: "8px"
  xl: "12px"
  "2xl": "14px"
  pill: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  "2xl": "48px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
    rounded: "{rounded.md}"
    padding: "8px 24px"
  button-primary-hover:
    backgroundColor: "{colors.primary-deep}"
    textColor: "#ffffff"
  card:
    backgroundColor: "#ffffff"
    rounded: "{rounded['2xl']}"
    padding: "1.5rem"
    boxShadow: "1px solid {colors.neutral-border}"
  input:
    backgroundColor: "{colors.neutral-surface}"
    borderColor: "{colors.neutral-border}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
  tag:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
    rounded: "{rounded.sm}"
    padding: "4px 8px"
---

## Overview

Промышленный e-commerce интерфейс для B2B-закупок пневматического инструмента. Визуальная система построена на Bulma CSS с кастомными токенами. Приоритет — функциональность и скорость поиска товара над декоративностью.

Регистр: product. Интерфейс обслуживает процесс покупки, а не является самодостаточным визуальным продуктом.

## Colors

Палитра строится на двух основных цветах: синий (primary) и красный (accent). Нейтральные оттенки — холодные серые с лёгким синим подтоном (hue ~260).

- **Primary** (`#5B93C1`) — основной интерактивный цвет: кнопки, ссылки, активные состояния, бейджи
- **Primary Deep** (`#485FC7`) — тёмный primary для hover-состояний
- **Accent** (`#e41817`) — цены, важные акценты, предупреждения
- **Warm accent** (`#f1ac2b`) — дополнительный тёплый акцент для выделения
- **Dark** (`#34495e`) — заголовки, основной текст в подвалах
- **Ink** (`#09131f`) — основной цвет текста
- **Muted** (`#676f79`) — вторичный текст, подписи, метаданные
- **Surface** (`#f5f6fa`) — фон карточек и секций
- **Paper** (`#f8f6fc`) — фон страницы, инпутов
- **Border** (`rgba(72, 95, 199, 0.125)`) — тонкие границы карточек и секций

Не использовать: pure black (`#000`), pure white (`#fff`), cream/sand/beige фоны.

## Typography

Системный sans-serif стек (BlinkMacSystemFont → Segoe UI → Roboto → Ubuntu). Без кастомных веб-шрифтов — приоритет на скорость загрузки.

- **Display / Hero** (`kp-hero-title`) — clamp(1.5rem, 2.5vw + 0.5rem, 2.25rem), weight 700, letter-spacing -0.02em, max-width 650px, margin auto (центрирован)
- **Section Heading** (`kp-section-heading`) — 1.5rem, weight 700, line-height 1.3
- **Section Subheading** (`kp-section-subheading`) — 1.2rem, weight 700, border-left 3px accent
- **Body** — 1rem, weight 400, line-height 1.5
- **Label / Tag** (`kp-about-hero__tag`) — 0.7rem, weight 700, letter-spacing 0.12em, uppercase, цвет primary

Иерархия: hero-title → section-heading → section-subheading → body → label. Не использовать serif шрифты — промышленный характер не предполагает редакционную типографику.

## Elevation

Плоский дизайн с минимальной глубиной. Тени используются для разделения уровней, не для объёма.

- **Border shadow**: `0 0 0 1px rgba(72, 95, 199, 0.125)` — основной способ отделения карточек
- **Box shadow**: `0 0 0 .125em var(--katran-shadow-color)` — для инпутов и фокуса
- **Hover shadow**: `0 8px 30px rgba(72, 95, 199, 0.1)` — подъём карточек при hover
- **Card hover lift**: `translateY(-3px)` — карточки поднимаются при наведении

Не использовать: soft wide shadows (ghost-card pattern), colored shadows как декор.

## Easing

Кастомные кривые из `:root`:

- `--ease-out`: `cubic-bezier(0.23, 1, 0.32, 1)` — вход элементов
- `--ease-in-out`: `cubic-bezier(0.77, 0, 0.175, 1)` — переходы состояний
- `--ease-spring`: `cubic-bezier(0.34, 1.56, 0.64, 1)` — пружинные анимации
- `--ease-liquid`: `cubic-bezier(0.22, 1.2, 0.36, 1)` — button press feedback

## Layout Patterns

### Hero Section
Все страницы используют единый паттерн hero:
```html
<div class="title-wrapper has-text-centered" style="padding: 1rem 0 0.5rem;">
  <p class="kp-about-hero__tag">Тег страницы</p>
  <h1 class="kp-hero-title">Заголовок страницы</h1>
  <div class="kp-solutions-divider"></div>
  <p class="subtitle is-6 mt-2" style="...">Подзаголовок</p>
</div>
```

### Section Headings
Секции используют единый паттерн:
```html
<p class="kp-section-label kp-section-label--center">Метка</p>
<h2 class="kp-section-heading" style="text-align: center;">Заголовок секции</h2>
<div class="kp-solutions-divider"></div>
```

### CTA Block
Все CTA-блоки используют единый паттерн:
```html
<div class="kp-cta-box kp-cta-box--solutions">
  <p class="kp-cta-box__title">Заголовок</p>
  <p class="kp-cta-box__text">Описание</p>
  <div class="buttons mt-3 is-justify-content-center">
    <a class="button is-info is-outlined"><strong>Основная кнопка</strong></a>
    <a class="button is-light"><strong>+7 (812) 331 79 09</strong></a>
  </div>
</div>
```

### Breadcrumbs
Навигационная цепочка `is-small` с иконкой дома и `aria-label="breadcrumbs"`.

## Components

### Button
- **Primary**: фон `--katran-blue-2`, текст white, скругление 6px, padding 8px 24px
- **Hover**: затемнение primary
- **Active**: `scale(0.95)` с liquid easing
- **Transition**: `transform 120ms var(--ease-liquid)`

### Hero Tag (`kp-about-hero__tag`)
Тег над заголовком hero-секции:
- `display: inline-flex`, centered
- 0.7rem, weight 700, uppercase, letter-spacing 0.12em
- Цвет `--katran-blue`
- Псевдоэлемент `::before` — линия 20×2px

### Hero Title (`kp-hero-title`)
- clamp(1.5rem, 2.5vw + 0.5rem, 2.25rem), weight 700
- `max-width: 650px`, `margin-left: auto`, `margin-right: auto`
- `letter-spacing: -0.02em`

### Stat Card (`kp-about-stat-card`)
Карточки со статистикой (о компании):
- Градиентный фон: `linear-gradient(135deg, --katran-blue, --katran-blue-2)`
- Белый текст, скругление 12px
- Цифры: `clamp(1.6rem, 3vw, 2.2rem)`, weight 800
- Подписи: 1rem, opacity 0.85

### Capability Card (`kp-sol-cap`)
Карточки возможностей (решения, о компании):
- Белый фон, рамка `--katran-shadow-border-color`, скругление 12px
- Hover: `translateY(-2px)` + тень
- Иконка: градиентный квадрат 40×40 с белой иконкой
- Заголовок и текст: слева от иконки через `kp-sol-cap__header`

### Solution Card (`kp-sol-card`)
Карточки отраслей (страница решений):
- Белый фон, тонкая рамка, скругление 14px
- Иконка по центру, текст центрирован
- Hover: `translateY(-3px)` + тень + иконка заливается primary
- Круглая кнопка-стрелка в правом нижнем углу (36×36px)
- Кнопка при hover: заливка primary, белая иконка, сдвиг вправо

### Catalog Card (`kp-cat-card`)
Карточки категорий (каталог):
- Фон `--katran-white-color`, рамка, скругление 8px
- Изображение: блок 160px с `--katran-wt-color` фоном
- Hover: тень + подъём 2px + масштаб изображения 1.05
- Круглая кнопка-стрелка в правом нижнем углу (36×36px)

### Round Arrow Button (`kp-sol-card__arrow`, `kp-cat-card__arrow`)
Круглая кнопка-стрелка в правом нижнем углу карточек:
- 36×36px, `border-radius: 50%`
- Белый фон, тонкая рамка, иконка primary
- Hover: заливка primary, белая иконка, `translateX(3px)`

### Process Step (`kp-sol-process`)
Этапы процесса (импортозамещение):
- Горизонтальный layout: номер + текст
- Номер: градиентный квадрат 36×36, белый текст
- Заголовок 1rem, текст 0.88rem

### Development Step (`kp-sol-dev-step`)
Этапы разработки (разработка под заказ):
- Иконка по центру в квадрате 52×52 с рамкой
- Hover: иконка заливается primary, белая
- Mobile: горизонтальный layout

### Brand Card (`kp-sol-brand`)
Карточки брендов (импортозамещение):
- Иконка + заголовок в шапке, описание ниже
- Hover: тень + подъём

### Advantage Card (`kp-sol-adv`)
Карточки преимуществ:
- Центрированный layout
- Иконка: градиентный квадрат 44×44
- Заголовок + описание

### Case Card (`kp-sol-case`)
Карточки кейсов:
- Заголовок с нижней линией
- Метки: uppercase 0.7rem, primary цвет
- Метрики: градиентный pill-бейдж

### Industry Card (dark band)
Карточки отраслей (о компании, тёмная секция):
- Тёмный фон `--katran-dark`, белый текст
- Иконки: полупрозрачный фон, primary цвет
- Hover: фон становится полупрозрачным

### Partner Card (`kp-about-partner`)
Карточки партнёров:
- Колоночный layout: логотип + название
- Рамка, скругление 12px
- Hover: тень + подъём

### CTA Box (`kp-cta-box`)
Блок призыва к действию:
- Центрированный текст
- Заголовок `kp-cta-box__title`
- Текст `kp-cta-box__text`
- Кнопки: `is-info is-outlined` + `is-light` (с телефоном)

## Page Templates

### Production (`/production/`)
- Hero: тег "Собственное производство", H1, подзаголовок, 2 кнопки
- Секции: шлифмашины, трамбовки, ПВМ-12, рубильные молотки
- Каждая секция: section-label → section-heading → divider → подзаголовок
- Карточки продуктов: grid layout с изображением и описанием
- SEO-блок перед CTA

### About (`/about/`)
- Hero: watermark "1990", тег "О компании", H1, 2 кнопки
- Stats: 4 градиентных карточки в строку
- SEO-текст
- Карты способностей: `kp-sol-cap` (3 в строку)
- Преимущества: 2 колонки с номерами
- Отрасли: тёмная секция с иконками
- Партнёры: сетка логотипов

### Solutions (`/solutions/`)
- Hero: тег "Катран-Пневмо", H1, подзаголовок
- Карточки отраслей: `kp-sol-card` с круглой кнопкой-стрелкой
- CTA

### Import Substitution (`/import-substitution/`)
- Hero: тег, H1, подзаголовок, кнопка
- SEO-текст
- Процесс: 4 этапа (`kp-sol-process`)
- Бренды: 4 карточки (`kp-sol-brand`)
- Преимущества: 3 карточки (`kp-sol-adv`)
- CTA

### Custom Development (`/custom-development/`)
- Hero: тег "Инженерное бюро", H1, подзаголовок, кнопка
- SEO-текст
- Этапы: 6 шагов (`kp-sol-dev-step`)
- Возможности: 3 карточки (`kp-sol-cap`)
- Кейсы: 3 карточки (`kp-sol-case`)
- CTA

### Catalog (`/catalog/`)
- Breadcrumbs
- Hero: тег "Каталог", H1
- Секции по main_category: section-heading + divider + сетка карточек
- Карточки: `kp-cat-card` с круглой кнопкой-стрелкой
- Media queries: desktop (1024px+) 3 в строку, fullHD (1408px+) 3 в строку крупнее
- CTA

### Catalog Main Category (`/catalog/<slug>/`)
- Breadcrumbs
- Hero: тег "Каталог", H1, подзаголовок
- Сетка подкатегорий: `kp-cat-card` с круглой кнопкой-стрелкой
- SEO-текст (если есть)
- CTA

## Do's and Don'ts

### Do
- Использовать токены из `:root` для всех цветов
- Поддерживать контраст ≥ 4.5:1 для body text (WCAG AA)
- Использовать `var(--ease-out)` и `var(--ease-liquid)` для анимаций
- Центрировать hero-заголовки через `kp-hero-title` (max-width + margin auto)
- Использовать `scale(0.95)` для feedback при нажатии кнопок
- Использовать `kp-about-hero__tag` для тегов над заголовками
- Использовать `kp-solutions-divider` для разделителей секций
- Использовать `kp-cta-box--solutions` для CTA-блоков
- Добавлять `is-variable is-2` на columns для отступов между карточками
- Добавлять `aria-current="page"` на активный breadcrumb

### Don't
- Использовать `transition: all` — указывать конкретные свойства
- Использовать `ease-in` для UI-анимаций
- Делать кнопки с `border-radius: 32px+` (card-style)
- Использовать gradient text или glassmorphism как дефолт
- Использовать serif шрифты для промышленного каталога
- Делать анимации > 300ms без обоснования
- Использовать Bulma `title is-*` классы вместо `kp-hero-title` / `kp-section-heading`
- Использовать inline-стили для тегов hero (использовать `kp-about-hero__tag`)
- Смешивать стили карточек на разных страницах (использовать общие компоненты)
