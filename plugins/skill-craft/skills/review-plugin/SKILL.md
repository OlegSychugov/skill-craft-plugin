---
name: review-plugin
description: Review an existing Cowork plugin or skill against the skill-craft acceptance checklist and report item-by-item results with fixes, without modifying files.
argument-hint: <alias или путь к плагину>
disable-model-invocation: true
---

# review-plugin — ревизия плагина по чек-листу

Проверь плагин `$ARGUMENTS` по стандарту skill-craft. Команда только
читает: правки — после подтверждения пользователя.

## Предусловия

- Рабочий корень — репозиторий cowork_hub (есть `categories.yaml`); иначе
  спроси путь.
- Поиск плагина: путь из `$ARGUMENTS` как есть, иначе
  `backlog/02. Testing/<alias>/`, затем `plugins/<alias>/`. Не найден или
  `$ARGUMENTS` пусто — покажи доступные alias из обеих папок и спроси.

## Шаги

- [ ] 1. Загрузи навык `skill-craft`; прочитай
      `../skill-craft/Референсы/METHODOLOGY.md` и `SKILL-AUTHORING.md`;
      для пункта о тоне — чек-лист из `PUBLISHING.md`.
- [ ] 2. Прочитай все файлы плагина: `plugin.yaml`, `skills/*/SKILL.md`,
      `skills/*/Референсы/`, `commands/`, `agents/`, `README.md`.
- [ ] 3. Механические проверки:
      - frontmatter и `plugin.yaml` парсятся как YAML; `description` —
        одна plain-строка без `|-`, кавычек и «: »;
      - пять обязательных полей; `version` — целое; `tags` — slug;
      - категория есть в `categories.yaml`;
      - тело SKILL.md ≤ 500 строк; ссылки на ресурсы — существующие файлы,
        один уровень глубины;
      - нет `pip install`, `matplotlib`, файловых операций через
        `python_run`.
- [ ] 4. Содержательные проверки по остальным пунктам чек-листа
      (степень свободы, триггеры/анти-триггеры, README как описание
      витрины, тон и орфография, ничего не выдумано).
- [ ] 5. Узел в `Plugins-map.md` (путь — `Референсы/PLUGINS-MAP.md`):
      есть ли, актуальны ли STATUS и состав навыков.
- [ ] 6. Если в плагине есть `evals/` — проверь пункты eval-слоя; иначе
      пометь их «не применимо».

## Ограничения

- Ничего не менять без явного «да» пользователя. После отчёта предложи
  исправить FAIL-пункты списком.
- Существующие `agent.html` не считать дефектом и не требовать: стандарт
  отменён 2026-10-01, старые файлы не трогать.

## Формат отчёта

Таблица `Пункт | ОК/FAIL/н.п. | Где (файл:строка) | Что исправить`,
итог `N из M`, список правок по приоритету.
