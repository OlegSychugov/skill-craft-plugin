---
name: new-plugin
description: Build a Cowork plugin from its plan (or a draft) in the pipeline todo folder into the pipeline testing folder following the skill-craft standard, with synthetic test data and an acceptance checklist report.
argument-hint: <имя папки черновика>
disable-model-invocation: true
---

# new-plugin — собрать плагин по плану

## Цель

Собрать в `<cfg:testing_dir>/<alias>/` плагин, который решает цель
пользователя из плана и проходит приёмку витрины с первого раза.

## Вход и выход

- Вход: `<cfg:todo_dir>/$ARGUMENTS/ПЛАН.md` (от `design-plugin`) и
  материалы черновика рядом с ним. Если плана нет — предложи сначала
  `design-plugin`; если пользователь хочет сразу, собирай по черновику и
  принимай решения сам, отмечая их в отчёте.
- Пустой `$ARGUMENTS` — покажи подпапки `<cfg:todo_dir>/` и спроси.
  Пути — `../skill-craft/Референсы/CONFIG.md`.
- Выход: плагин по контракту (`plugin.yaml`, `README.md`, `agents/`,
  `skills/`, `commands/` по плану) и папка `Данные агента <Название>/` с
  синтетическими файлами и генератором.

## Опора

- `../skill-craft/Референсы/METHODOLOGY.md` — структура, поля, 7
  категорий, YAML-канон, стандарт агента (шаблон).
- `../skill-craft/Референсы/SKILL-MEDIUM-FREEDOM.md` — каркас тела
  навыка; `SKILL-AUTHORING.md` — конвенции каталога.
- `../skill-craft/Референсы/HARNESS-DESCRIPTION.md` — сверь каждый
  навык и скрипт с возможностями песочницы.
- `../skill-craft/Референсы/DEMO-DATA.md` — тест-данные.

## Границы

- Alias покажи пользователю и дождись подтверждения до создания файлов.
  Если `<cfg:testing_dir>/<alias>/` уже есть, спроси: перезаписать,
  объединить или отменить.
- Черновик в `<cfg:todo_dir>/` не трогать.
- Служебные референсы skill-craft в плагин не переносить: в `Референсы/`
  навыка кладётся только то, что нужно самому плагину.
- Недостающие факты помечать `<TBD: что уточнить>`, а не выдумывать.

## Отчёт

Alias и путь; список созданных файлов; агент (`name`, `skills`);
решения, принятые без плана; открытые `<TBD>`; чек-лист приёмки
skill-craft (пункт → ОК/FAIL). Следующий шаг — `review-plugin`, затем
`plugins-map <alias>`.
