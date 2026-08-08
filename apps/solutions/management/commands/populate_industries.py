"""
Management command to populate industries with recommended data.

Usage:
    python manage.py populate_industries          # Create only missing industries
    python manage.py populate_industries --force   # Update all industries

Safe for production: idempotent by default, uses --force to overwrite.
"""
from django.core.management.base import BaseCommand
from apps.solutions.models import Industry


INDUSTRIES = [
    {
        'title': 'Судостроение',
        'slug': 'sudostroenie',
        'icon_class': 'fa-solid fa-ship',
        'short_description': 'Зачистка сварных швов, обработка корпусов, клёпка, шлифовка металлоконструкций',
        'ordering': 1,
        'meta_title': 'Пневматический инструмент для судостроения | Катран-Пневмо',
        'meta_description': 'Пневмоинструмент для судостроительных предприятий: шлифмашины, молотки, дрели. Зачистка швов, обработка корпусов, клёпка. Поставки по России.',
        'meta_keywords': 'пневмоинструмент судостроение, шлифмашина для судостроения, пневмодрель судостроение, зачистка сварных швов',
        'description': """<h2>Пневматический инструмент для судостроения</h2>

<p>Судостроение — одна из ключевых отраслей, где пневматический инструмент незаменим. Контакт с металлом, сварные швы, ограниченные пространства корпусов судов — всё это требует надёжного, безопасного и производительного инструмента.</p>

<h3>Почему пневматика?</h3>
<ul>
<li><strong>Безопасность</strong> — отсутствие искр критично при работе в замкнутых объёмах корпусов судов</li>
<li><strong>Надёжность</strong> — пневмоинструмент не перегревается при непрерывной работе</li>
<li><strong>Производительность</strong> — высокая мощность при малом весе</li>
<li><strong>Взрывобезопасность</strong> — допуск для работы во взрывоопасных зонах</li>
</ul>

<h3>Основные операции в судостроении</h3>
<ul>
<li>Зачистка сварных швов (внутренние и наружные поверхности)</li>
<li>Шлифовка и полировка корпусных деталей</li>
<li>Клёпка и винтование</li>
<li>Сверление и зенковка</li>
<li>Демонтаж и ремонт</li>
</ul>

<h3>Рекомендуемый инструмент</h3>

<table class="table is-fullwidth kp-industry-table">
<thead>
<tr><td><strong>Операция</strong></td><td><strong>Инструмент</strong></td><td><strong>Модели</strong></td></tr>
</thead>
<tbody>
<tr>
<td>Зачистка сварных швов</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-radialnye-priamye/">Пневмошлифмашина прямая</a></td>
<td>МП-011, МП-006</td>
</tr>
<tr>
<td>Полировка поверхностей</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-orbitalnye/">Пневмошлифмашина орбитальная</a></td>
<td>ПШМ-150</td>
</tr>
<tr>
<td>Резка и шлифовка</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-uglovye-pnevmobolgarki/">Пневмоболгарка</a></td>
<td>УШМ-125, УШМ-180</td>
</tr>
<tr>
<td>Демонтаж, удаление окалины</td>
<td><a href="/catalog/pnevmaticheskij-instrument/molotki-otboinye-i-betonolomy/">Пневмомолоток отбойный</a></td>
<td>МО-2К, МО-2Б</td>
</tr>
<tr>
<td>Удаление наплавленного металла</td>
<td><a href="/catalog/pnevmaticheskij-instrument/molotki-rubilnye-i-pnevmozubila/">Пневмомолоток рубильный</a></td>
<td>РМ-8, РМ-12, РМ-16</td>
</tr>
<tr>
<td>Клёпка конструкций</td>
<td><a href="/catalog/pnevmaticheskij-instrument/molotki-klepalnye/">Пневмомолоток клепальный</a></td>
<td>МПК-1, МПК-2</td>
</tr>
<tr>
<td>Сверление и зенковка</td>
<td><a href="/catalog/pnevmaticheskij-instrument/sverlilnye-mashiny-pnevmodreli/">Пневматическая дрель</a></td>
<td>ИП-2014, ИП-2106</td>
</tr>
</tbody>
</table>

<p>«Катран-Пневмо» поставляет инструмент для крупнейших судостроительных предприятий России. Разрабатываем специальные решения под конкретные технологические задачи — с изменённой геометрией, особенными характеристиками.</p>

<p><a href="/custom-development/" class="button is-info is-outlined mt-2"><strong>Заказать специальный инструмент</strong></a></p>""",
        'recommended_tools': '',
    },
    {
        'title': 'Машиностроение',
        'slug': 'mashinostroenie',
        'icon_class': 'fa-solid fa-gear',
        'short_description': 'Шлифовка, полировка, заточка, сборка узлов, обработка металлов',
        'ordering': 2,
        'meta_title': 'Пневмоинструмент для машиностроения | Катран-Пневмо',
        'meta_description': 'Пневматический инструмент для машиностроительных предприятий: шлифмашины, гайковерты, дрели. Шлифовка, полировка, сборка. Поставки по России.',
        'meta_keywords': 'пневмоинструмент машиностроение, шлифмашина машиностроение, гайковерт промышленный',
        'description': """<h2>Пневматический инструмент для машиностроения</h2>

<p>Машиностроение — крупнейший потребитель пневматического инструмента. От обработки заготовок до финальной сборки узлов — на каждом этапе требуется надёжный и производительный инструмент.</p>

<h3>Применение в машиностроении</h3>
<ul>
<li><strong>Обработка металлов</strong> — шлифовка, полировка, зачистка отливок и поковок</li>
<li><strong>Сборка узлов</strong> — затяжка резьбовых соединений, фиксация компонентов</li>
<li><strong>Сверление и нарезание резьбы</strong> — в металле, пластике, композитах</li>
<li><strong>Заточка инструмента</strong> — восстановление режущих кромок</li>
<li><strong>Демонтаж и ремонт</strong> — разборка узлов, замена компонентов</li>
</ul>

<h3>Почему пневматика предпочтительнее</h3>
<ul>
<li>Малый вес при высокой мощности — снижение утомляемости оператора</li>
<li>Отсутствие электрических контактов — безопасность в пыльной среде</li>
<li>Возможность непрерывной работы без перегрева</li>
<li>Простота обслуживания и ремонтопригодность</li>
</ul>

<h3>Рекомендуемый инструмент</h3>

<table class="table is-fullwidth kp-industry-table">
<thead>
<tr><td><strong>Операция</strong></td><td><strong>Инструмент</strong></td><td><strong>Модели</strong></td></tr>
</thead>
<tbody>
<tr>
<td>Точечная обработка поверхностей</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-radialnye-priamye/">Пневмошлифмашина прямая</a></td>
<td>МП-011, МП-006</td>
</tr>
<tr>
<td>Полировка, шлифовка плоскостей</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-orbitalnye/">Пневмошлифмашина орбитальная</a></td>
<td>ПШМ-150</td>
</tr>
<tr>
<td>Затяжка и откручивание</td>
<td><a href="/catalog/pnevmaticheskij-instrument/gaikoverty/">Пневмогайковерт</a></td>
<td>ГМ-100, ГМ-200</td>
</tr>
<tr>
<td>Сверление, зенковка</td>
<td><a href="/catalog/pnevmaticheskij-instrument/sverlilnye-mashiny-pnevmodreli/">Пневматическая дрель</a></td>
<td>ИП-2014, ИП-2106</td>
</tr>
<tr>
<td>Резка, шлифовка</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-uglovye-pnevmobolgarki/">Пневмоболгарка</a></td>
<td>УШМ-125, УШМ-180</td>
</tr>
<tr>
<td>Сборка мелких узлов</td>
<td><a href="/catalog/pnevmaticheskij-instrument/vintoverty-pnevmootvertki/">Пневматическая отвёртка</a></td>
<td>ОП-1, ОП-2</td>
</tr>
</tbody>
</table>

<p><a href="/catalog/" class="button is-info is-outlined mt-2"><strong>Смотреть весь каталог</strong></a></p>""",
        'recommended_tools': '',
    },
    {
        'title': 'Нефтегаз',
        'slug': 'neftegaz',
        'icon_class': 'fa-solid fa-oil-well',
        'short_description': 'Работы во взрывоопасных зонах, обслуживание трубопроводов, ремонт оборудования',
        'ordering': 3,
        'meta_title': 'Пневмоинструмент для нефтегазовой отрасли | Катран-Пневмо',
        'meta_description': 'Пневматический инструмент для нефтегазовой отрасли: взрывобезопасный, для АС, НПЗ, ГПК. Сертифицированное оборудование. Поставки по России.',
        'meta_keywords': 'пневмоинструмент нефтегаз, взрывобезопасный инструмент, инструмент для НПЗ, пневмоинструмент для АС',
        'description': """<h2>Пневматический инструмент для нефтегазовой отрасли</h2>

<p>Нефтегазовая отрасль — среда с повышенными требованиями к безопасности. Взрывоопасные зоны, агрессивные среды, высокие нагрузки — здесь пневматический инструмент является единственным допустимым решением.</p>

<h3>Почему пневматика обязательна</h3>
<ul>
<li><strong>Взрывобезопасность</strong> — отсутствие электрических контактов и искр</li>
<li><strong>Допуск для АС</strong> — соответствие требованиям ГОСТ для атомных станций</li>
<li><strong>Коррозионная стойкость</strong> — алюминиевый корпус устойчив к агрессивным средам</li>
<li><strong>Надёжность</strong> — работают в пыли, влаге, перепадах температур</li>
</ul>

<h3>Области применения</h3>
<ul>
<li>Обслуживание трубопроводов — зачистка, шлифовка, сверление</li>
<li>Ремонт оборудования на НПЗ, ГПК, АС</li>
<li>Монтаж и демонтаж трубных систем</li>
<li>Подготовка поверхностей под покрытия</li>
<li>Работы во взрывоопасных зонах</li>
</ul>

<h3>Рекомендуемый инструмент</h3>

<table class="table is-fullwidth kp-industry-table">
<thead>
<tr><td><strong>Задача</strong></td><td><strong>Инструмент</strong></td><td><strong>Модели</strong></td></tr>
</thead>
<tbody>
<tr>
<td>Зачистка труб и фитингов</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-radialnye-priamye/">Пневмошлифмашина прямая</a></td>
<td>МП-011</td>
</tr>
<tr>
<td>Шлифовка трубопроводов</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-orbitalnye/">Пневмошлифмашина орбитальная</a></td>
<td>ПШМ-150</td>
</tr>
<tr>
<td>Сверление в стальных конструкциях</td>
<td><a href="/catalog/pnevmaticheskij-instrument/sverlilnye-mashiny-pnevmodreli/">Пневматическая дрель</a></td>
<td>ИП-2014, ИП-2106</td>
</tr>
<tr>
<td>Затяжка фланцевых соединений</td>
<td><a href="/catalog/pnevmaticheskij-instrument/gaikoverty/">Пневмогайковерт</a></td>
<td>ГМ-100, ГМ-200</td>
</tr>
<tr>
<td>Демонтаж оборудования</td>
<td><a href="/catalog/pnevmaticheskij-instrument/molotki-otboinye-i-betonolomy/">Пневмомолоток отбойный</a></td>
<td>МО-2К</td>
</tr>
<tr>
<td>Резка и шлифовка</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-uglovye-pnevmobolgarki/">Пневмоболгарка</a></td>
<td>УШМ-125</td>
</tr>
</tbody>
</table>

<p><a href="/contacts/" class="button is-info is-outlined mt-2"><strong>Запросить сертификаты</strong></a></p>""",
        'recommended_tools': '',
    },
    {
        'title': 'Металлургия',
        'slug': 'metallurgiya',
        'icon_class': 'fa-solid fa-fire',
        'short_description': 'Зачистка отливок, трамбовка, обслуживание печей, обработка металлов',
        'ordering': 4,
        'meta_title': 'Пневмоинструмент для металлургии | Катран-Пневмо',
        'meta_description': 'Пневматический инструмент для металлургических предприятий: трамбовки, шлифмашины, молотки. Зачистка, обработка, обслуживание. Поставки по России.',
        'meta_keywords': 'пневмоинструмент металлургия, трамбовка пневматическая, шлифмашина металлургия',
        'description': """<h2>Пневматический инструмент для металлургии</h2>

<p>Металлургическое производство — экстремальные условия: высокие температуры, abrasiveная пыль, тяжёлые металлы. Пневматический инструмент выдерживает эти условия лучше электрического.</p>

<h3>Применение в металлургии</h3>
<ul>
<li><strong>Зачистка отливок и поковок</strong> — удаление окалины, заусенцев, прибылей</li>
<li><strong>Трамбовка формовочных смесей</strong> — уплотнение песчаных форм</li>
<li><strong>Обслуживание печей</strong> — очистка подин, ремонт футеровки</li>
<li><strong>Обработка проката</strong> — зачистка поверхности, удаление дефектов</li>
<li><strong>Ремонт оборудования</strong> — разборка, сборка, сверление</li>
</ul>

<h3>Преимущества пневматики в металлургии</h3>
<ul>
<li>Устойчивость к высоким температурам — алюминиевый корпус не деформируется</li>
<li>Пылезащищённость — работает в abrasiveной среде</li>
<li>Простота ремонта — быстрая замена лопаток ротора</li>
<li>Отсутствие электрических контактов — безопасность в запылённой среде</li>
</ul>

<h3>Рекомендуемый инструмент</h3>

<table class="table is-fullwidth kp-industry-table">
<thead>
<tr><td><strong>Операция</strong></td><td><strong>Инструмент</strong></td><td><strong>Модели</strong></td></tr>
</thead>
<tbody>
<tr>
<td>Уплотнение формовочных смесей</td>
<td><a href="/catalog/pnevmaticheskij-instrument/trambovki/">Пневматическая трамбовка</a></td>
<td>ТП-28А, ТПВ-3А</td>
</tr>
<tr>
<td>Зачистка отливок</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-radialnye-priamye/">Пневмошлифмашина прямая</a></td>
<td>МП-011, МП-006</td>
</tr>
<tr>
<td>Удаление окалины, прибылей</td>
<td><a href="/catalog/pnevmaticheskij-instrument/molotki-otboinye-i-betonolomy/">Пневмомолоток отбойный</a></td>
<td>МО-2К, МО-2Б</td>
</tr>
<tr>
<td>Резка и шлифовка проката</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-uglovye-pnevmobolgarki/">Пневмоболгарка</a></td>
<td>УШМ-180</td>
</tr>
<tr>
<td>Ремонт формовочного оборудования</td>
<td><a href="/catalog/pnevmaticheskij-instrument/sverlilnye-mashiny-pnevmodreli/">Пневматическая дрель</a></td>
<td>ИП-2014</td>
</tr>
</tbody>
</table>

<p><a href="/catalog/" class="button is-info is-outlined mt-2"><strong>Смотреть весь каталог</strong></a></p>""",
        'recommended_tools': '',
    },
    {
        'title': 'Литейное производство',
        'slug': 'liteinoe-proizvodstvo',
        'icon_class': 'fa-solid fa-industry',
        'short_description': 'Трамбовка форм, зачистка отливок, обработка литниковой системы',
        'ordering': 5,
        'meta_title': 'Пневмоинструмент для литейного производства | Катран-Пневмо',
        'meta_description': 'Пневматический инструмент для литейных цехов: трамбовки, шлифмашины, молотки. Формовка, зачистка, обработка отливок. Поставки по России.',
        'meta_keywords': 'пневмоинструмент литейное производство, трамбовка литейная, зачистка отливок',
        'description': """<h2>Пневматический инструмент для литейного производства</h2>

<p>Литейное производство требует специализированного инструмента: от уплотнения форм до зачистки готовых отливок. Пневматика здесь — основной тип привода.</p>

<h3>Этапы применения</h3>
<ul>
<li><strong>Формовка</strong> — трамбовка песчаных смесей в формах и стержнях</li>
<li><strong>Заливка</strong> — подготовка литниковой системы</li>
<li><strong>Разливка</strong> — обработка отливок после извлечения из формы</li>
<li><strong>Зачистка</strong> — удаление литниковой системы, прибылей, окалины</li>
<li><strong>Контроль качества</strong> — шлифовка для визуального осмотра</li>
</ul>

<h3>Рекомендуемый инструмент</h3>

<table class="table is-fullwidth kp-industry-table">
<thead>
<tr><td><strong>Операция</strong></td><td><strong>Инструмент</strong></td><td><strong>Модели</strong></td></tr>
</thead>
<tbody>
<tr>
<td>Трамбовка песчаных форм</td>
<td><a href="/catalog/pnevmaticheskij-instrument/trambovki/">Пневматическая трамбовка</a></td>
<td>ТП-28А, ТПВ-3А</td>
</tr>
<tr>
<td>Зачистка отливок</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-radialnye-priamye/">Пневмошлифмашина прямая</a></td>
<td>МП-011</td>
</tr>
<tr>
<td>Удаление литниковой системы</td>
<td><a href="/catalog/pnevmaticheskij-instrument/molotki-otboinye-i-betonolomy/">Пневмомолоток отбойный</a></td>
<td>МО-2К</td>
</tr>
<tr>
<td>Шлифовка для контроля</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-orbitalnye/">Пневмошлифмашина орбитальная</a></td>
<td>ПШМ-150</td>
</tr>
</tbody>
</table>

<p><a href="/catalog/" class="button is-info is-outlined mt-2"><strong>Смотреть весь каталог</strong></a></p>""",
        'recommended_tools': '',
    },
    {
        'title': 'Энергетика',
        'slug': 'energetika',
        'icon_class': 'fa-solid fa-bolt',
        'short_description': 'Обслуживание турбин, ремонт оборудования, монтаж трубопроводов',
        'ordering': 6,
        'meta_title': 'Пневмоинструмент для энергетики | Катран-Пневмо',
        'meta_description': 'Пневматический инструмент для энергетических предприятий: ТЭЦ, ГЭС, АЭС. Турбины, котлы, трубопроводы. Поставки по России.',
        'meta_keywords': 'пневмоинструмент энергетика, инструмент для ТЭЦ, инструмент для АЭС',
        'description': """<h2>Пневматический инструмент для энергетики</h2>

<p>Энергетические предприятия — ТЭЦ, ГЭС, АЭС — требуют надёжного инструмента для обслуживания турбин, котлов, трубопроводов и другого оборудования.</p>

<h3>Применение</h3>
<ul>
<li><strong>Обслуживание турбин</strong> — шлифовка лопаток, зачистка рабочих поверхностей</li>
<li><strong>Ремонт котлов</strong> — очистка теплообменников, зачистка труб</li>
<li><strong>Монтаж трубопроводов</strong> — сверление, зенковка, зачистка фланцев</li>
<li><strong>Демонтаж оборудования</strong> — откручивание, разборка</li>
<li><strong>Подготовка поверхностей</strong> — под покрытия и изоляцию</li>
</ul>

<h3>Рекомендуемый инструмент</h3>

<table class="table is-fullwidth kp-industry-table">
<thead>
<tr><td><strong>Задача</strong></td><td><strong>Инструмент</strong></td><td><strong>Модели</strong></td></tr>
</thead>
<tbody>
<tr>
<td>Шлифовка лопаток турбин</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-radialnye-priamye/">Пневмошлифмашина прямая</a></td>
<td>МП-011</td>
</tr>
<tr>
<td>Затяжка фланцев</td>
<td><a href="/catalog/pnevmaticheskij-instrument/gaikoverty/">Пневмогайковерт</a></td>
<td>ГМ-100, ГМ-200</td>
</tr>
<tr>
<td>Сверление трубных решёток</td>
<td><a href="/catalog/pnevmaticheskij-instrument/sverlilnye-mashiny-pnevmodreli/">Пневматическая дрель</a></td>
<td>ИП-2014, ИП-2106</td>
</tr>
<tr>
<td>Демонтаж оборудования</td>
<td><a href="/catalog/pnevmaticheskij-instrument/molotki-otboinye-i-betonolomy/">Пневмомолоток отбойный</a></td>
<td>МО-2К</td>
</tr>
<tr>
<td>Шлифовка поверхностей</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-orbitalnye/">Пневмошлифмашина орбитальная</a></td>
<td>ПШМ-150</td>
</tr>
</tbody>
</table>

<p><a href="/contacts/" class="button is-info is-outlined mt-2"><strong>Обсудить поставку</strong></a></p>""",
        'recommended_tools': '',
    },
    {
        'title': 'ОПК',
        'slug': 'opk',
        'icon_class': 'fa-solid fa-shield-halved',
        'short_description': 'Специальное производство, оборонные предприятия, атомная отрасль',
        'ordering': 7,
        'meta_title': 'Пневмоинструмент для ОПК | Катран-Пневмо',
        'meta_description': 'Пневматический инструмент для оборонно-промышленного комплекса: специальные решения, допуски, сертификация. Поставки по России.',
        'meta_keywords': 'пневмоинструмент ОПК, инструмент для оборонных предприятий, специальный пневмоинструмент',
        'description': """<h2>Пневматический инструмент для ОПК</h2>

<p>Оборонно-промышленный комплекс предъявляет повышенные требования к качеству, надёжности и допускам оборудования. «Катран-Пневмо» имеет опыт поставок специализированного инструмента для предприятий ОПК и атомной отрасли.</p>

<h3>Особенности работы с ОПК</h3>
<ul>
<li><strong>Специальные требования</strong> — инструмент под конкретные технологические процессы</li>
<li><strong>Допуски и сертификация</strong> — соответствие ГОСТ и отраслевым стандартам</li>
<li><strong>Конфиденциальность</strong> — работа с закрытой документацией</li>
<li><strong>Надёжность</strong> — инструмент должен работать безотказно</li>
</ul>

<h3>Наш опыт</h3>
<ul>
<li>Разработка специальных пневмошлифмашин для атомных станций</li>
<li>Поставка инструмента для судостроительных предприятий ОПК</li>
<li>Изготовление нестандартного инструмента под ТЗ</li>
</ul>

<h3>Рекомендуемый инструмент</h3>

<table class="table is-fullwidth kp-industry-table">
<thead>
<tr><td><strong>Задача</strong></td><td><strong>Решение</strong></td></tr>
</thead>
<tbody>
<tr>
<td>Специальные шлифмашины</td>
<td><a href="/custom-development/">Разработка под заказ</a> — модификации под конкретные задачи</td>
</tr>
<tr>
<td>Специальные молотки</td>
<td><a href="/custom-development/">Разработка под заказ</a> — с изменёнными характеристиками</td>
</tr>
<tr>
<td>Комплексные решения</td>
<td><a href="/custom-development/">Разработка под заказ</a> — привод + инструмент + управление</td>
</tr>
<tr>
<td>Стандартный инструмент</td>
<td><a href="/catalog/">Каталог</a> — шлифмашины, молотки, дрели</td>
</tr>
</tbody>
</table>

<p><a href="/custom-development/" class="button is-info is-outlined mt-2"><strong>Обсудить ТЗ</strong></a></p>""",
        'recommended_tools': '',
    },
    {
        'title': 'Железнодорожное машиностроение',
        'slug': 'zhd-mashinostroenie',
        'icon_class': 'fa-solid fa-train',
        'short_description': 'Ремонт вагонов и локомотивов, обработка металлоконструкций',
        'ordering': 8,
        'meta_title': 'Пневмоинструмент для ж/д машиностроения | Катран-Пневмо',
        'meta_description': 'Пневматический инструмент для железнодорожного машиностроения: ремонт вагонов, локомотивов, обработка конструкций. Поставки по России.',
        'meta_keywords': 'пневмоинструмент ж/д, инструмент для вагоностроения, ремонт локомотивов',
        'description': """<h2>Пневматический инструмент для ж/д машиностроения</h2>

<p>Железнодорожное машиностроение — это ремонт и производство вагонов, локомотивов, железнодорожного оборудования. Здесь пневмоинструмент применяется широко.</p>

<h3>Применение</h3>
<ul>
<li><strong>Ремонт вагонов</strong> — зачистка, шлифовка, сверление, затяжка</li>
<li><strong>Производство вагонов</strong> — сборка кузовов, монтаж оборудования</li>
<li><strong>Ремонт локомотивов</strong> — обслуживание тягового оборудования</li>
<li><strong>Обработка рельсов</strong> — шлифовка, зачистка стыков</li>
<li><strong>Ремонт путевого оборудования</strong> — сверление, зенковка</li>
</ul>

<h3>Рекомендуемый инструмент</h3>

<table class="table is-fullwidth kp-industry-table">
<thead>
<tr><td><strong>Операция</strong></td><td><strong>Инструмент</strong></td><td><strong>Модели</strong></td></tr>
</thead>
<tbody>
<tr>
<td>Затяжка болтовых соединений</td>
<td><a href="/catalog/pnevmaticheskij-instrument/gaikoverty/">Пневмогайковерт</a></td>
<td>ГМ-100, ГМ-200</td>
</tr>
<tr>
<td>Обработка поверхностей</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-radialnye-priamye/">Пневмошлифмашина прямая</a></td>
<td>МП-011</td>
</tr>
<tr>
<td>Сверление, зенковка</td>
<td><a href="/catalog/pnevmaticheskij-instrument/sverlilnye-mashiny-pnevmodreli/">Пневматическая дрель</a></td>
<td>ИП-2014, ИП-2106</td>
</tr>
<tr>
<td>Резка металла</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-uglovye-pnevmobolgarki/">Пневмоболгарка</a></td>
<td>УШМ-125, УШМ-180</td>
</tr>
</tbody>
</table>

<p><a href="/catalog/" class="button is-info is-outlined mt-2"><strong>Смотреть каталог</strong></a></p>""",
        'recommended_tools': '',
    },
    {
        'title': 'Горнодобывающая промышленность',
        'slug': 'gornodobycha',
        'icon_class': 'fa-solid fa-mountain',
        'short_description': 'Бурение, разработка породы, обслуживание горного оборудования',
        'ordering': 9,
        'meta_title': 'Пневмоинструмент для горнодобывающей промышленности | Катран-Пневмо',
        'meta_description': 'Пневматический инструмент для горнодобывающей промышленности: буры, молотки, перфораторы. Шахты, карьеры, разработки. Поставки по России.',
        'meta_keywords': 'пневмоинструмент горнодобыча, инструмент для шахт, пневмобур горный',
        'description': """<h2>Пневматический инструмент для горнодобывающей промышленности</h2>

<p>Горнодобывающая промышленность — экстремальные условия: пыль, влага, взрывоопасная среда. Пневматический инструмент здесь — основной тип привода.</p>

<h3>Применение</h3>
<ul>
<li><strong>Бурение</strong> — горизонтальное и вертикальное бурение скважин</li>
<li><strong>Разработка породы</strong> — отбойные молотки для рыхления</li>
<li><strong>Обслуживание оборудования</strong> — ремонт, сборка, разборка</li>
<li><strong>Транспортировка</strong> — обработка рельсов и путей</li>
<li><strong>Вентиляция</strong> — монтаж вентиляционных систем</li>
</ul>

<h3>Почему пневматика в горнодобыче</h3>
<ul>
<li><strong>Взрывобезопасность</strong> — критично в шахтах с газовыделением</li>
<li><strong>Пылезащищённость</strong> — работает в abrasiveной среде</li>
<li><strong>Простота ремонта</strong> — быстрое восстановление в полевых условиях</li>
<li><strong>Надёжность</strong> — минимальные простои</li>
</ul>

<h3>Рекомендуемый инструмент</h3>

<table class="table is-fullwidth kp-industry-table">
<thead>
<tr><td><strong>Задача</strong></td><td><strong>Инструмент</strong></td><td><strong>Модели</strong></td></tr>
</thead>
<tbody>
<tr>
<td>Рыхление породы</td>
<td><a href="/catalog/pnevmaticheskij-instrument/molotki-otboinye-i-betonolomy/">Пневмомолоток отбойный</a></td>
<td>МО-2К, МО-2Б</td>
</tr>
<tr>
<td>Бурение скважин</td>
<td><a href="/catalog/pnevmaticheskij-instrument/sverlilnye-mashiny-pnevmodreli/">Пневматическая дрель</a></td>
<td>ИП-2014, ИП-2106</td>
</tr>
<tr>
<td>Обслуживание оборудования</td>
<td><a href="/catalog/pnevmaticheskij-instrument/gaikoverty/">Пневмогайковерт</a></td>
<td>ГМ-100</td>
</tr>
<tr>
<td>Зачистка и шлифовка</td>
<td><a href="/catalog/pnevmaticheskij-instrument/shlifmashiny-radialnye-priamye/">Пневмошлифмашина прямая</a></td>
<td>МП-011</td>
</tr>
</tbody>
</table>

<p><a href="/contacts/" class="button is-info is-outlined mt-2"><strong>Запросить предложение</strong></a></p>""",
        'recommended_tools': '',
    },
]


class Command(BaseCommand):
    help = 'Populate industries with recommended data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update existing industries',
        )

    def handle(self, *args, **options):
        force = options['force']
        created = 0
        updated = 0
        skipped = 0

        for data in INDUSTRIES:
            slug = data['slug']
            industry, was_created = Industry.objects.get_or_create(
                slug=slug,
                defaults=data,
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  + Created: {data["title"]}'))
            elif force:
                for key, value in data.items():
                    if key != 'slug':
                        setattr(industry, key, value)
                industry.save()
                updated += 1
                self.stdout.write(self.style.WARNING(f'  ~ Updated: {data["title"]}'))
            else:
                skipped += 1
                self.stdout.write(f'  - Exists:  {data["title"]} (use --force to update)')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done: {created} created, {updated} updated, {skipped} skipped'
        ))
