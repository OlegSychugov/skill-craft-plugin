---
name: test-plugin
description: Build the behavioral eval layer for a Cowork plugin (cases, graders, demo-stand protocol, fact-report prompt) or grade a finished run into a PASS/FAIL verdict, per the skill-craft evaluation method.
argument-hint: <alias> [grade <ГГГГ-ММ-ДД>]
disable-model-invocation: true
---

# test-plugin — evals: сборка и вердикт

## Цель

Проверить поведение плагина на живых формулировках: срабатывает ли
навык там, где нужно, молчит ли там, где не нужно, и не нарушает ли
границы. Итог — вердикт PASS/FAIL, каждый FAIL подкреплён уликой.

## Режимы

- `test-plugin <alias>` — собрать `evals/` в `<cfg:testing_dir>/<alias>/`.
- `test-plugin <alias> grade <дата>` — проградировать
  `evals/results/<дата>/` и записать `вердикт.md`.

Нет alias — покажи доступные и спроси.

## Опора

`Референсы/EVALUATION.md` — структура `evals/`, источники кейсов, типы
градеров, шаблоны протокола, факт-отчёта и вердикта, правила
недетерминизма.

## Границы

- Кейсы выводятся из SKILL.md и плана, а не выдумываются. Чего не хватает
  (нет анти-триггеров, нет пограничных случаев) — `<TBD>` и вопрос в
  отчёт.
- Прогон на стенде выполняет пользователь (установка — `deploy-plugin`);
  результаты прогона не имитировать.
- При расхождении отчёта агента и скачанных файлов первичны файлы.
- `evals/` остаются в Testing и в каталог не публикуются.

## Отчёт

Сборка: дерево `evals/`, кейсы с типами, открытые `<TBD>`.
Грейдинг: таблица вердикта и итог PASS/FAIL.
