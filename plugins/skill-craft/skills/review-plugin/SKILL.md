---
name: review-plugin
description: Review an existing Cowork plugin or skill against the skill-craft acceptance checklist and the user's goal, and report item-by-item results with concrete fixes, without modifying files.
argument-hint: <alias или путь к плагину>
disable-model-invocation: true
---

# review-plugin — ревизия плагина

## Цель

Сказать честно, готов ли плагин: проходит ли он витрину и решает ли
цель пользователя. Каждое замечание указывает файл, строку и правку.

## Вход и выход

- Вход: путь из `$ARGUMENTS`, иначе `<cfg:testing_dir>/<alias>/`, затем
  `<cfg:plugins_dir>/<alias>/`. Не найден — покажи доступные alias и
  спроси. Если рядом с черновиком есть `ПЛАН.md`, сверь плагин с ним.
- Выход: отчёт в чате, файлы не меняются.

## Опора

- Чек-лист приёмки — навык `skill-craft`; чек-лист агента —
  `../skill-craft/Референсы/METHODOLOGY.md` §5.
- Механику (YAML разбирается, 5 полей, категория из 7, ссылки на файлы
  существуют, `skills` агента ↔ `skills/`) проверяй кодом, а не на глаз.
- Harness — по чек-листу `../skill-craft/Референсы/HARNESS-DESCRIPTION.md` §7.
- Тело навыков — по `../skill-craft/Референсы/SKILL-MEDIUM-FREEDOM.md`:
  цель вместо сценария, вопрос по условию, без служебных файлов.
- Узел в `<cfg:plugins_map_path>`: есть ли он и актуален ли.
- `evals/` есть — проверь последний вердикт; нет — пункт «не применимо».

## Границы

- Ничего не менять без явного «да». После отчёта предложи исправить
  FAIL-пункты списком.
- Старые `agent.html` в корне плагина дефектом не считать.

## Отчёт

Таблица `Пункт | ОК/FAIL/н.п. | Где (файл:строка) | Что исправить`,
итог `N из M`, правки по приоритету.
