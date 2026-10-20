---
name: publish-plugin
description: Move a tested Cowork plugin from the testing pipeline folder into the catalog plugins folder, then create a feature branch from the fresh base branch, push it and prepare a pull request to gitverse following the branch regulation.
argument-hint: <alias>
disable-model-invocation: true
---

# publish-plugin — публикация плагина

## Цель

Довести проверенный плагин до PR в витрину: в каталоге только чистовые
файлы, ветка правильная, описание PR готово к вставке.

## Вход и выход

- Вход: `<cfg:testing_dir>/$ARGUMENTS/`. Пусто или не найдено — покажи
  доступные alias и спроси. Пути — `../skill-craft/Референсы/CONFIG.md`.
- Выход: `<cfg:plugins_dir>/$ARGUMENTS/`, запушенная ветка
  `feature/$ARGUMENTS`, ссылка на PR и текст описания.

## Гейты (до любых действий)

- Пользователь подтвердил, что плагин работает на тест-данных. Если это
  не сказано явно — спроси.
- Агент есть, и его `skills` совпадает с `skills/`. Иначе — не
  публиковать, предложить `review-plugin`.
- Есть `evals/` — нужен PASS в последнем `evals/results/<дата>/вердикт.md`.

## Порядок

1. В каталог переносится только white-list: `plugin.yaml`, `README.md`,
   `agents/`, `skills/`, `commands/`. Остальное (`Данные агента …`,
   `Демо/`, черновые файлы) покажи списком. `evals/` остаётся в Testing.
2. `git -C <cfg:catalog_dir> status`: если есть изменения вне
   публикуемого плагина — предупреди и жди подтверждения (`git stash` не
   делать: stash общий для всех worktree).
3. Скопируй white-list в `<cfg:plugins_dir>/$ARGUMENTS/`. Если папка уже
   есть, спроси: перезаписать / слить / отменить; по умолчанию — отменить.
4. Git — всё в `<cfg:catalog_dir>`:
   ```
   git checkout <cfg:hub_base_branch>
   git pull origin <cfg:hub_base_branch>
   git checkout -b feature/$ARGUMENTS
   git add <cfg:plugins_dir>/$ARGUMENTS
   git commit -m "feat: добавить плагин <name из plugin.yaml>"
   git push -u origin feature/$ARGUMENTS
   ```
5. PR: ссылка `<cfg:hub_pr_url>` (`{base}` = `<cfg:hub_base_branch>`,
   `{branch}` = `feature/$ARGUMENTS`) и описание по шаблону
   `Референсы/PUBLISHING.md`.
6. После успешного пуша спроси, удалить ли Testing-папку (кроме
   `evals/`) и черновик (по умолчанию — нет). Предложи
   `plugins-map $ARGUMENTS`.

После принятия MR — удаление ветки в тот же день по регламенту
`Референсы/PUBLISHING.md`.

## Границы

- Никогда не пушить в `<cfg:hub_base_branch>` и не ставить её веткой
  upstream.
- Конфликт при `git pull` не разрешать самому — отдать пользователю.
- Не выводить `git remote -v` и URL с токенами; имена и контакты людей —
  тоже.

## Отчёт

Скопированные файлы, что осталось в Testing, ветка, ссылка на PR, текст
описания PR.
