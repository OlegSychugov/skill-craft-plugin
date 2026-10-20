---
name: deploy-plugin
description: Manually deploy a Cowork plugin from its testing folder to the demo stand through the browser — workspace, agent, skill ZIPs, commands, bindings and verification.
argument-hint: <alias>
disable-model-invocation: true
---

# deploy-plugin — развёртывание на демо-стенде

## Цель

Сделать плагин `<cfg:testing_dir>/$ARGUMENTS/` рабочим на стенде
`<cfg:demo_stand_url>`: пространство, агент, навыки и команды привязаны
и проверены по счётчикам. Это не гейт публикации, а подготовка к прогону
evals или к записи демо.

## Вход и выход

- Вход: плагин в Testing с `plugin.yaml`, `agents/*.md`, `skills/`,
  `commands/`. Если агента нет — остановись и предложи `review-plugin`:
  инструкцию агента на стенде не сочиняют.
- Выход: URL пространства и агента, всё привязано и сохранено.

## Опора

- `Референсы/DEPLOY-STAND.md` — карта полей, путь в интерфейсе,
  проверка, грабли Playwright.
- `Референсы/pack_skill.py` — упаковка каждого навыка в ZIP (не tar и не
  Compress-Archive: они ломают пути и кириллицу).

## Границы

- Логин выполняет пользователь: креды не искать и не запрашивать,
  дождаться, пока пользователь скажет, что вошёл.
- Нет инструмента управления браузером — выдай пользователю путь из
  DEPLOY-STAND.md для ручного выполнения.
- Ничего не удалять на стенде без подтверждения; системные навыки и
  команды не трогать.
- Временные копии ZIP после загрузки удалить.

## Отчёт

URL пространства и агента; таблица «навык/команда → статус»; счётчики;
расхождения интерфейса с DEPLOY-STAND.md. Следующий шаг — прогон по
`ПРОТОКОЛ_DEMO.md` (`test-plugin`) или `demo-video`.
