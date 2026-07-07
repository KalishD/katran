---
name: Katran-Pnevmo
description: Интернет-магазин пневматического инструмента для B2B
colors:
  primary: "#5B93C1"
  primary-deep: "#4878A3"
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
    backgroundColor: "{colors.neutral-bg}"
    rounded: "{rounded.md}"
    padding: "16px"
    boxShadow: "0 0 0 1px {colors.neutral-border}"
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
- **Accent** (`#e41817`) — цены, важные акценты, предупреждения
- **Warm accent** (`#f1ac2b`) — дополнительный тёплый акцент для выделения
- **Dark** (`#34495e`) — заголовки, основной текст в подвалах
- **Ink** (`#09131f`) — основной цвет текста
- **Muted** (`#676f79`) — вторичный текст, подписи, метаданные
- **Surface** (`#f5f6fa`) — фон карточек и секций
- **Paper** (`#f8f6fc`) — фон страницы, инпутов

Не использовать: pure black (`#000`), pure white (`#fff`), cream/sand/beige фоны.

## Typography

Системный sans-serif стек (BlinkMacSystemFont → Segoe UI → Roboto → Ubuntu). Без кастомных веб-шрифтов — приоритет на скорость загрузки.

- **Display** — clamp(1.5rem, 2.5vw + 0.5rem, 2.25rem), weight 700, letter-spacing -0.02em
- **Body** — 1rem, weight 400, line-height 1.5
- **Label** — 0.75rem, weight 600, letter-spacing 0.02em

Иерархия: title → subtitle → body → label. Не использовать serif шрифты — промышленный характер не предполагает редакционную типографику.

## Elevation

Плоский дизайн с минимальной глубиной. Тени используются для разделения уровней, не для объёма.

- **Border shadow**: `0 0 0 1px rgba(72, 95, 199, 0.125)` — основной способ отделения карточек
- **Box shadow**: `0 0 0 .125em var(--katran-shadow-color)` — для инпутов и фокуса
- **Elevated shadow**: `0 2px 8px rgba(0,0,0,0.15)` — для уведомлений, модальных окон

Не использовать: soft wide shadows (ghost-card pattern), colored shadows как декор.

## Components

### Button
- Primary: фон `--katran-blue-2`, текст white, скругление 6px, padding 8px 24px
- Hover: затемнение primary
- Active: `scale(0.95)` с liquid easing
- Transition: `transform 120ms var(--ease-liquid)`

### Card
- Фон: `--katran-white-color` (`#f5f6fa`)
- Граница: `1px solid --katran-shadow-border-color`
- Скругление: 6px
- Padding: 1rem

### Input
- Фон: `--katran-white-color`
- Граница: `--katran-shadow-border-color`
- Фокус: `box-shadow: 0 0 0 .125em --katran-shadow-color`
- Скругление: 6px

### Tag / Badge
- Primary: фон `--katran-blue-2`, текст white
- Active: фон `--katran-blue-2`
- Скругление: 4px

### Notification (Toast)
- Фон: `--katran-blue-2` (`#5B93C1`)
- Текст: white
- Скругление: 12px
- Max-width: 480px
- Позиция: `top: 60px`, центрировано
- Анимация: `transform 400ms var(--ease-liquid)`

## Do's and Don'ts

### Do
- Использовать токены из `:root` для всех цветов
- Поддерживать контраст ≥ 7:1 для body text (WCAG AAA)
- Использовать `var(--ease-out)` и `var(--ease-liquid)` для анимаций
- Центрировать уведомления, делать их компактными
- Использовать `scale(0.95)` для feedback при нажатии кнопок

### Don't
- Использовать `transition: all` — указывать конкретные свойства
- Использовать `ease-in` для UI-анимаций
- Делать кнопки с `border-radius: 32px+` (card-style)
- Использовать gradient text или glassmorphism как дефолт
- Использовать serif шрифты для промышленного каталога
- Делать анимации > 300ms без обоснования
