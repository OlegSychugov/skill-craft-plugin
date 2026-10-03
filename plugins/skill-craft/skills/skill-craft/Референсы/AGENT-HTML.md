# Стандарт итоговой HTML-страницы агента

> **Источники:** шаблон — `Сборка HTML агента/page_template.html`, эталон
> нового формата — `Сборка HTML агента/Примеры/ИИ_агент_финансового_контролёра.html`
> (оба лежат в `Референсы/Сборка HTML агента/`, рядом с этим файлом);
> референс-вёрстка — `cowork_hub/ИИ_агент_по_работе_с_отзывами_и_обращениями.html`
> (корень cowork_hub, не менять). Дизайн-токены — `Сборка HTML агента/template.json`
> и `Сборка HTML агента/gigacowork.css` (Official GigaCowork Design System
> v0.1). Токены и скрипты встроены ниже дословно — референс самодостаточен.
>
> Два старых эталона в `Сборка HTML агента/Примеры/` (дески на 7 и 9
> слайдов) — исторические: только источник готовых CSS-паттернов, по ним
> страницы не собирать.
>
> Файл лежит в `.kilo/` (Референсы навыка `skill-craft`), в gitverse не
> переносится (рабочий документ области, как METHODOLOGY/PUBLISHING).

Содержание

- 1. Контракт
- 2. Технические требования
- 3. Дизайн-токены
- 4. Каркас — 6 слайдов
- 5. Контент
- 6. Чек-лист приёмки страницы

## 1. Контракт

- Файл: `Демо/ИИ_агент_<имя>.html` — итоговая клиентская страница агента;
  лежит в папке `Демо/` рядом с артефактами демо-видео (эталон:
  `backlog/02. Testing/financial-controller/Демо/ИИ_агент_финансового_контролёра.html`).
  Имя файла — с подчёркиваниями, как в эталоне.
- Собирается только по явному запросу пользователя («собери страницу по
  агенту», «сделай презентацию») и только когда есть обе реальные ссылки:
  публичная на видеоролик и на workspace. Без ссылок страницу не собирать.
- Не артефакт сборки плагина: при сборке или ревизии плагина HTML-страница
  в его корне не создаётся.
- Историческая справка: до 2026-10-01 стандарт требовал
  `plugins/<alias>/agent.html` — витринную страницу плагина для gitverse
  (валидатор 2026-09-11 относился к нему). Существующие `agent.html` не
  трогать и не переделывать; новый стандарт действует на будущие сборки.
- Конвейер: публикация видео — `DEMO-VIDEO.md` §7; стандарт самой
  страницы — здесь.

## 2. Технические требования

- Один самодостаточный файл: все стили инлайном в `<style>`, скрипты
  инлайном в `<script>`; никаких внешних картинок, шрифтов и библиотек.
  Единственное допустимое исключение — SheetJS CDN
  `https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js`
  (экспорт формы обратной связи, слайд 6). Ссылки на пространство и видео
  — обычные `<a href>`, внешних запросов не создают.
- Шрифтовой стек `"SB Sans Display", Arial, sans-serif` **без**
  `@font-face`: шрифтового ассета нет, работает fallback на Arial.
- `<html lang="ru">`, `<meta charset="UTF-8">`; `<title>` = `Имя агента —
  GigaCowork`.
- Деск слайдов 1280×720: `.gc-slide` с паддингами `24px 32px 80px`
  (24 сверху, 32 по бокам, 80 снизу — нижний ряд оставлен под
  `gc-footer` и навигацию).
- Структура деки: `.deck` → `.slide` (полноэкранный контейнер; видимость
  переключается классами `.active` / `.prev`) → `.gc-slide` (лист
  1280×720). Первый слайд получает класс `active` прямо в разметке.
- Навигация: кнопки ←/→ (у крайних слайдов — `disabled`), клавиатура
  (ArrowLeft, ArrowRight, Space, PageUp, PageDown, Home, End), тач-свайп
  с порогом 50px, счётчик «N / M», градиентный прогресс-бар внизу.
- На контентных слайдах — `gc-footer` (нижняя строка) с градиентным
  «GigaCowork» в правой ячейке (на слайде «Решение» правая ячейка пустая
  — как в эталоне).

### Каркас деки

```html
<body>
  <div class="deck">
    <div class="slide layout-cover active gc-bg-hero"><!-- слайд 1 -->
      <div class="gc-slide">…</div>
    </div>
    <div class="slide gc-bg-default"><!-- контентный слайд -->
      <div class="gc-slide">…</div>
    </div>
  </div>

  <div class="slide-counter"><span id="current">1</span> / <span id="total">6</span></div>
  <div class="keyboard-hint">Стрелки ← → для навигации</div>
  <div class="progress-bar" id="progress"></div>
  <div class="nav-controls">
    <button class="nav-btn" id="prevBtn" onclick="changeSlide(-1)" aria-label="Previous">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><polyline points="15 18 9 12 15 6"></polyline></svg>
    </button>
    <button class="nav-btn" id="nextBtn" onclick="changeSlide(1)" aria-label="Next">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><polyline points="9 18 15 12 9 6"></polyline></svg>
    </button>
  </div>
  <script>…</script>
</body>
```

### JS-паттерн навигации

Копировать дословно из шаблона `page_template.html` (число слайдов скрипт
берёт сам):

```html
<script>
  const slides = document.querySelectorAll('.slide');
  const currentEl = document.getElementById('current');
  const totalEl = document.getElementById('total');
  const progressEl = document.getElementById('progress');
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  let current = 0; const total = slides.length; totalEl.textContent = total;
  function updateSlide() {
    slides.forEach((slide, i) => {
      slide.classList.remove('active', 'prev');
      if (i === current) slide.classList.add('active');
      else if (i < current) slide.classList.add('prev');
    });
    currentEl.textContent = current + 1;
    progressEl.style.width = ((current + 1) / total * 100) + '%';
    prevBtn.disabled = current === 0;
    nextBtn.disabled = current === total - 1;
  }
  function changeSlide(dir) {
    const next = current + dir;
    if (next >= 0 && next < total) { current = next; updateSlide(); }
  }
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { e.preventDefault(); changeSlide(1); }
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); changeSlide(-1); }
    else if (e.key === 'Home') { e.preventDefault(); current = 0; updateSlide(); }
    else if (e.key === 'End') { e.preventDefault(); current = total - 1; updateSlide(); }
  });
  let touchStartX = 0, touchEndX = 0;
  document.addEventListener('touchstart', (e) => { touchStartX = e.changedTouches[0].screenX; }, { passive: true });
  document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    const diff = touchStartX - touchEndX;
    if (Math.abs(diff) > 50) changeSlide(diff > 0 ? 1 : -1);
  }, { passive: true });
  updateSlide();
</script>
```

## 3. Дизайн-токены

Блок `:root` — дословно (как в шаблоне и эталоне):

```css
:root {
  --gc-font: "SB Sans Display", Arial, sans-serif;
  --gc-text: #121212;
  --gc-white: #ffffff;
  --gc-state: #e0e1e7;
  --gc-teal: #1ab3b0;
  --gc-teal-alt: #13b3a7;
  --gc-blue: #51b8ee;
  --gc-blue-alt: #61b8ff;
  --gc-periwinkle: #a3b5f3;
  --gc-periwinkle-alt: #b0b4f0;
  --gc-muted: #a09d99;
  --gc-pale-blue: #d0e7f3;
  --gc-space-3: 12px;
  --gc-space-4: 16px;
  --gc-space-5: 24px;
  --gc-space-6: 32px;
  --gc-radius-card: 20px;
  --gc-radius-pill: 999px;
  --gc-card-fill: rgba(255, 255, 255, 0.7);
  --gc-card-border: rgba(255, 255, 255, 0.88);
  --gc-card-shadow: 0 12px 32px rgba(76, 102, 130, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.75);
}
```

Ключевые значения:

- Фирменный градиент `#1AB3B0 → #51B8EE → #A3B5F3` (teal → blue →
  periwinkle, точки останова 0% / 47% / 100%); фон `#fafafa`; текст
  `#121212`; state `#E0E1E7`; muted `#a09d99`.
- Радиусы: карточка 20px, pill 999px.
- Карточки — glassmorphism: заливка `rgba(255,255,255,0.7)`,
  `backdrop-filter: blur(20px)`, граница `rgba(255,255,255,0.88)`, тень
  `--gc-card-shadow`.
- Отступы — только из шкалы 4–96px (4/8/12/16/24/32/40/48/56/64/80/96).
- Типографика — один шрифт Regular 400, иерархия через размер:
  `gc-kicker` 13.333px uppercase, `gc-h1` 64px, `gc-h2` 40px,
  `gc-body-l` 24px, `gc-body` 17.333px, `gc-caption` 13.333px.

Канон классов этого формата (CSS копировать из шаблона
`page_template.html` или эталона как есть — не «нормализовать» и не
переизобретать):

- Фоны слайдов: `gc-bg-default` (стандартный), `gc-bg-neutral`
  (спокойный для плотного контента), `gc-bg-hero` (выраженный — титул и
  «Эффекты»); радиальные градиенты поверх `#fafafa`.
- `gc-grid` — сетка 12 колонок, gap 24px; карточки раскладываются через
  `style="grid-column: span N"`.
- `gc-card` (модификаторы `--compact`, `--large`, `--container`,
  `--accent`, `--metric`) с элементами `gc-card__title` / `gc-card__body`;
  `gc-card--metric` содержит `.gc-card__value` — 64px, цвет
  `var(--gc-blue-alt)`.
- `gc-pill` (модификаторы `--current`, `--positive`, `--category`).
- `gc-footer` — нижняя строка контентного слайда; элементы `__notes`
  (центр) и `__brand` («GigaCowork» градиентным текстом).
- `brand-logo` — «GigaCowork» градиентным текстом в правом верхнем углу
  титульного слайда.
- Helper-классы: `two-columns` (две равные колонки, gap 24px),
  `feature-list` (список), `small-body` (15px), `compact-card`
  (паддинг 18px).
- Навигация: `nav-controls`, `nav-btn`, `slide-counter`, `progress-bar`,
  `keyboard-hint`.

Паттерны старых эталонов (`Примеры/*.html`, исторические) — только как
источник CSS-приёмов (`step-num`, `result-box`, `link-card`, `data-table`,
`status-pill`, `timeline-mini`); состав слайдов и вёрстку собирать по
шаблону и эталону нового формата.

Запрещено (из `Сборка HTML агента/template.json` → `avoid_for`): тёмные
темы; другие шрифты кроме SB Sans Display; произвольные цвета, отступы и
эффекты — всё только из токенов выше.

## 4. Каркас — 6 слайдов

Состав слайдов фиксирован — ровно 6, порядок как в эталоне:

| # | Слайд | Фон | Содержание |
|---|---|---|---|
| 1 | Титул | `gc-bg-hero` + `layout-cover` | `brand-logo`; kicker с категорией; `gc-h1` — имя агента; body-l «Создан на базе платформы GigaCowork»; карточка `--accent` «Назначение: …» |
| 2 | Проблематика | `gc-bg-default` | до 4 карточек `gc-card--accent compact-card` (span 6): pill `--current` «Проблема N», заголовок, `small-body` |
| 3 | Решение | `gc-bg-neutral` | карточка «Назначение агента» (`--large --accent`); навыки — `gc-card compact-card` с pill `--positive` «Навык N»; span 6 при ≤4 навыках, span 4 при 5–7 |
| 4 | Применение | `gc-bg-default` | `two-columns`: «Когда применять агента» (pill `--category`) / «Как применять агента» (pill `--positive`); под каждым — карточка `--accent compact-card` со списком `feature-list` |
| 5 | Эффекты | `gc-bg-hero` | 3 карточки `gc-card--metric` (span 4, только счётные факты); ниже — «Качественные преимущества» и «Дополнительные материалы» (обе `--accent compact-card`, span 6; во второй — ссылки на пространство и видео) |
| 6 | Обратная связь | `gc-bg-neutral` | форма 6 вопросов + кнопка «Скачать ответы в Excel» |

Правила компоновки: на каждом контентном слайде `gc-kicker` (раздел) →
`gc-h2` (заголовок) → контент.

### Слайд 6 — форма обратной связи

Разметку формы, JS-подсветку выбранной оценки и `exportToExcel()`
копировать дословно из шаблона `page_template.html` (в эталоне они
идентичны) — не переизобретать. Имена полей фиксированы — их читает
экспорт:

1. `overall_rating` — общая оценка, радио 1–5 (пилл-кнопки, «5»
   изначально `--positive`);
2. `likes_dislikes` — что понравилось / не понравилось, textarea;
3. `client_customization` — потребность в доработке на данных клиента,
   радио Да/Нет;
4. `not_interested_reason` — почему агент не интересен, textarea;
5. `universality` — универсальность для отрасли, select 1–5;
6. `scaling_improvements` — доработки для масштабирования, textarea.

## 5. Контент

- Только факты из материалов плагина: `plugin.yaml`, `README.md`,
  `skills/`, `commands/`, черновики из `Draft/`. Ничего не выдумывать —
  дополнения без источника запрещены.
- Ссылки — только реальные: ролик — публичная ссылка файлообменника
  (выгрузка и проверка — `DEMO-VIDEO.md` §7), пространство — workspace, в
  котором записывалось демо. Полный URL — в `href`, видимый текст —
  краткая форма. Ссылки нет — задать **один** `question` пользователю;
  без ответа страницу не собирать, URL не изобретать.
- Метрики слайда 5 — только счётные факты из материалов (число навыков,
  число команд, режим работы — как «7 / 10 / Assist» в эталоне);
  маркетинговые проценты не выдумывать.
- Форму и JS слайда 6 копировать дословно из шаблона.

## 6. Чек-лист приёмки страницы

- [ ] Ровно 6 слайдов в порядке раздела 4; паддинги `.gc-slide` —
      `24px 32px 80px`.
- [ ] `@font-face` отсутствует; шрифтовой стек с fallback на Arial.
- [ ] Единственный внешний ресурс — SheetJS CDN (слайд 6); остальное —
      самодостаточно.
- [ ] Токены и классы — из раздела 3; запрещённые приёмы не используются.
- [ ] Обе ссылки реальны: видео — публичная (в чистой вкладке открывается
      без редиректа на логин), пространство — workspace демо; полный URL
      в `href`.
- [ ] Навигация работает: кнопки, клавиатура, свайп, счётчик «N / 6»,
      прогресс-бар; на крайних слайдах кнопки `disabled`.
- [ ] Экспорт формы даёт alert + скачивание `.xlsx`; подсветка выбранной
      оценки работает; имена полей не переименованы.
- [ ] Факты и метрики не выдуманы — из материалов плагина.
