---
name: publish-plugin
description: Move a tested Cowork plugin from the testing pipeline folder into the catalog plugins folder, then prepare a feature branch from fresh master, push and pull request to gitverse following the skill-craft publishing rules and branch regulation.
argument-hint: <alias>
disable-model-invocation: true
---

# publish-plugin — публикация плагина

Перенеси плагин из `<cfg:testing_dir>/$ARGUMENTS` в
`<cfg:plugins_dir>/$ARGUMENTS` и подготовь пуш в gitverse.

## Предусловия

- Загрузи навык `skill-craft` и прочитай
  `../skill-craft/Референсы/PUBLISHING.md`: действует «Локальное дополнение
  2026-09-11» (ветки `feature/<alias>`) и «Регламент веток 2026-10-06»;
  устаревший блок 2026-08-20 с ветками `skill-<slug>`/`plugin-<slug>`
  игнорировать.
- Настройки: `catalog_dir`, `plugins_dir`, `testing_dir`, `todo_dir`,
  `hub_repo_url`, `hub_base_branch`, `hub_pr_url` из `.skill-craft.json`
  (навык `skill-craft`, раздел «Настройки окружения»).
- Пользователь загрузил плагин в harness, прогнал сценарий на синтетических
  данных и получил ОК. Если ОК не подтверждён явно — спроси.
- Гейт вердикта: если в Testing-папке есть `evals/`, нужен
  `evals/results/<последняя дата>/вердикт.md` с итогом PASS. Нет `evals/` —
  гейта нет.

## Шаги

- [ ] 1. Прочитай `<cfg:testing_dir>/$ARGUMENTS/`. Пусто или не найдено —
      покажи доступные alias и спроси.
- [ ] 2. White-list чистового плагина: `plugin.yaml`, `skills/` (`.md` и
      ресурсы, `Референсы/` допустимы), `commands/`, `agents/`, `README.md`.
      Всё остальное («Данные агента …», `Демо/`, scratch, `.DS_Store`) —
      тестовые материалы: покажи список и спроси подтверждение удаления.
      `evals/` не переносится и остаётся в Testing как история прогонов.
- [ ] 3. `git -C <cfg:catalog_dir> status`. Есть изменения вне
      `<cfg:plugins_dir>/$ARGUMENTS` — предупреди;
      `git stash` сам не делай (stash общий между worktrees). Продолжай
      только после явного подтверждения.
- [ ] 4. Создай `<cfg:plugins_dir>/$ARGUMENTS/` (уже есть — спроси:
      перезаписать / слить / отменить, по умолчанию отменить) и скопируй
      только white-list.
- [ ] 5. После успешного копирования удали Testing-папку, кроме `evals/`.
      Спроси, удалять ли черновик из `<cfg:todo_dir>/` (по умолчанию — нет).
- [ ] 6. Git — все команды выполняй в папке `<cfg:catalog_dir>` (регламент
      веток: ветка только от свежего master, правильный upstream сразу):
      ```
      git -C <cfg:catalog_dir> checkout <cfg:hub_base_branch>
      git -C <cfg:catalog_dir> pull origin <cfg:hub_base_branch>
      git -C <cfg:catalog_dir> checkout -b feature/$ARGUMENTS
      git -C <cfg:catalog_dir> add <cfg:plugins_dir>/$ARGUMENTS
      git -C <cfg:catalog_dir> commit -m "feat: добавить плагин <name из plugin.yaml>"
      git -C <cfg:catalog_dir> push -u origin feature/$ARGUMENTS
      ```
      Не пропускай `git pull` перед созданием ветки. Никогда не пушить в
      master и не ставить ветке upstream master.
- [ ] 7. PR: выведи `<cfg:hub_repo_url>`, прямую ссылку `<cfg:hub_pr_url>`
      (`{base}` = `<cfg:hub_base_branch>`, `{branch}` = `feature/$ARGUMENTS`)
      и шаблон описания PR из PUBLISHING.md (Название / Описание /
      Категория / Задача / Как тестировать / Чек-лист).
- [ ] 8. Предложи `plugins-map` → `STATUS="remote-branch"`.
- [ ] 9. После принятия MR — в тот же день (регламент веток): удали ветку
      на gitverse (кнопка в MR или `git push origin --delete
      feature/$ARGUMENTS`), затем `git -C <cfg:catalog_dir> fetch --prune`
      и `git -C <cfg:catalog_dir> branch -D feature/$ARGUMENTS`
      (после squash-слияния `-d` не сработает — это нормально).

## Ограничения

- Никогда не пушить в `<cfg:hub_base_branch>` напрямую.
- Не выводить `git remote -v` и URL с токеном — в отчётах только
  `<cfg:hub_repo_url>`.
- Не копировать в `<cfg:plugins_dir>/` ничего вне white-list.
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
