---
name: plugins-map
description: Update a plugin node in the cowork_hub Plugins-map.md knowledge graph — status, version, skills, cross-links — or run a merge-candidate analysis, per the skill-craft graph specification.
argument-hint: <alias> | merge
disable-model-invocation: true
---

# plugins-map — граф плагинов

- `plugins-map <alias>` — добавить или актуализировать узел плагина;
- `plugins-map merge` — анализ кандидатов на слияние.

## Предусловия

- Загрузи навык `skill-craft` и прочитай
  `../skill-craft/Референсы/PLUGINS-MAP.md` целиком: формат XML, атрибуты,
  словарь статусов, правила дедупликации и компактности.
- Файл карты — `<cfg:plugins_map_path>` (настройки — навык `skill-craft`,
  раздел «Настройки окружения»). Не найден — спроси путь, не создавай новый.

## Шаги: узел плагина

- [ ] 1. Найди плагин: `plugins/`, `backlog/02. Testing/`, `01. ToDo/`,
      `00. Ideas/`, `.Archive/`. Прочитай манифест и состав навыков.
- [ ] 2. Определи STATUS по git (`git ls-tree --name-only origin/master
      plugins/` по локальному `origin/master`). `git fetch` — только с
      разрешения пользователя.
- [ ] 3. Категория — из `categories.yaml`; узел — внутри неё.
- [ ] 4. Заполни/обнови `keywords`, `terms`, `annotation` (≤ 2 предложений),
      узлы навыков (только для живых статусов), `VERSION`, `UPDATED`
      (сегодняшняя дата).
- [ ] 5. CrossLinks — только с опорой на состав и annotation обоих узлов;
      симметричные связи — один раз.
- [ ] 6. Покажи diff узла пользователю и запиши после подтверждения.

## Шаги: merge

- [ ] 1. Рецепт анализа слияния из PLUGINS-MAP.md: `OVERLAPS_WITH` с
      RELEVANCE ≥ 7 → сравнение keywords навыков → вывод.
- [ ] 2. Только отчёт; граф не менять.

## Ограничения

- Карта внутренняя: в gitverse и в плагины не переносится.
- Имена тегов — по правилам именования; уникальность во всём документе.

## Формат отчёта

Узел до/после (XML), источник статуса. Для merge — таблица пар
`плагин A | плагин B | RELEVANCE | общие keywords | вывод`.
