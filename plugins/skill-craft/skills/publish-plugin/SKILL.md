---
name: publish-plugin
description: Move a tested Cowork plugin from backlog/02. Testing into plugins/, then prepare a feature branch, push and pull request to gitverse following the skill-craft publishing rules.
argument-hint: <alias>
disable-model-invocation: true
---

# publish-plugin — публикация плагина

Перенеси плагин из `backlog/02. Testing/$ARGUMENTS` в `plugins/$ARGUMENTS`
и подготовь пуш в gitverse.

## Предусловия

- Загрузи навык `skill-craft` и прочитай
  `../skill-craft/Референсы/PUBLISHING.md`: действует «Локальное дополнение
  2026-09-11» (ветки `feature/<alias>`); устаревший блок 2026-08-20 с
  ветками `skill-<slug>`/`plugin-<slug>` игнорировать.
- Настройки: `hub_repo_url`, `hub_base_branch`, `hub_pr_url` из
  `.skill-craft.json` (навык `skill-craft`, раздел «Настройки окружения»).
- Пользователь загрузил плагин в harness, прогнал сценарий на синтетических
  данных и получил ОК. Если ОК не подтверждён явно — спроси.
- Гейт вердикта: если в Testing-папке есть `evals/`, нужен
  `evals/results/<последняя дата>/вердикт.md` с итогом PASS. Нет `evals/` —
  гейта нет.
- Гейт агента: в Testing-папке есть `agents/*.md`, его `skills` совпадает
  с составом `skills/` (`AGENT-MD.md`). Нет агента или расхождение —
  не публиковать, предложить `review-plugin`.

## Шаги

- [ ] 1. Прочитай `backlog/02. Testing/$ARGUMENTS/`. Пусто или не найдено —
      покажи доступные alias и спроси.
- [ ] 2. White-list чистового плагина: `plugin.yaml`, `skills/` (`.md` и
      ресурсы, `Референсы/` допустимы), `commands/`, `agents/`, `README.md`.
      Всё остальное («Данные агента …», `Демо/`, scratch, `.DS_Store`) —
      тестовые материалы: покажи список и спроси подтверждение удаления.
      `evals/` не переносится и остаётся в Testing как история прогонов.
- [ ] 3. `git status`. Есть изменения вне `plugins/$ARGUMENTS` — предупреди;
      `git stash` сам не делай (stash общий между worktrees). Продолжай
      только после явного подтверждения.
- [ ] 4. Создай `plugins/$ARGUMENTS/` (уже есть — спроси: перезаписать /
      слить / отменить, по умолчанию отменить) и скопируй только white-list.
- [ ] 5. После успешного копирования удали Testing-папку, кроме `evals/`.
      Спроси, удалять ли черновик из `backlog/01. ToDo/` (по умолчанию — нет).
- [ ] 6. Git:
      ```
      git checkout <cfg:hub_base_branch>
      git pull origin <cfg:hub_base_branch>
      git checkout -b feature/$ARGUMENTS
      git add plugins/$ARGUMENTS
      git commit -m "feat: добавить плагин <name из plugin.yaml>"
      git push origin feature/$ARGUMENTS
      ```
      Не пропускай `git pull` перед созданием ветки.
- [ ] 7. PR: выведи `<cfg:hub_repo_url>`, прямую ссылку `<cfg:hub_pr_url>`
      (`{base}` = `<cfg:hub_base_branch>`, `{branch}` = `feature/$ARGUMENTS`)
      и шаблон описания PR из PUBLISHING.md (Название / Описание /
      Категория / Задача / Как тестировать / Чек-лист).
- [ ] 8. Предложи `plugins-map` → `STATUS="remote-branch"`.

## Ограничения

- Никогда не пушить в `<cfg:hub_base_branch>` напрямую.
- Не выводить `git remote -v` и URL с токеном — в отчётах только
  `<cfg:hub_repo_url>`.
- Не копировать в `plugins/` ничего вне white-list.
- Тестовые данные не найдены — валидная ситуация, продолжай.

## Сбои

- Conflict при `git pull` — не разрешать автоматически; попроси
  пользователя разобрать `git status` вручную.
- Push отвергнут (403) — нет прав в gitverse: запросить доступ у
  администратора репозитория (PUBLISHING.md). Имена и контакты людей в
  отчёт не выводить.

## Формат отчёта

Скопированные файлы, удалённые элементы, ветка, ссылка на PR, текст
описания PR.
