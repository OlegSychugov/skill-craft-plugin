---
name: plugins-map
description: Update a plugin node in the Plugins-map.md knowledge graph — status, version, skills, cross-links — or run a merge-candidate analysis across the catalog.
argument-hint: <alias> | merge
disable-model-invocation: true
---

# plugins-map — граф плагинов

## Цель

Держать карту каталога честной: по ней ищут дубли функций и кандидатов
на слияние, а также видят, на какой стадии каждый плагин.

- `plugins-map <alias>` — добавить или актуализировать узел плагина;
- `plugins-map merge` — отчёт о кандидатах на слияние, граф не меняется.

## Вход и выход

- Карта — `<cfg:plugins_map_path>` (`../skill-craft/Референсы/CONFIG.md`).
  Не найдена — спроси путь, новую не создавай.
- Плагин ищется в `<cfg:plugins_dir>`, `<cfg:testing_dir>`,
  `<cfg:todo_dir>`, `<cfg:ideas_dir>`, `<cfg:archive_dir>`.

## Опора

`Референсы/PLUGINS-MAP.md` — формат XML, атрибуты, словарь статусов,
определение статуса по git, дедупликация, именование тегов, рецепт
анализа слияния.

## Границы

- Статус по git определяется по локальной ссылке
  `origin/<cfg:hub_base_branch>`; `git fetch` — только с разрешения
  пользователя.
- Связь ставится только с опорой на состав и annotation обоих узлов.
- Diff узла показать пользователю и записать после подтверждения.

## Отчёт

Узел до/после (XML) и источник статуса. Для merge — таблица
`плагин A | плагин B | RELEVANCE | общие keywords | вывод`.
