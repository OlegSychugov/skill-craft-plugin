# skill-craft marketplace

Marketplace for **Claude Code** and **OpenAI Codex** with the `skill-craft` plugin — a standard for designing and building plugins for the Giga Cowork `cowork_hub` catalog (content in Russian).

How it works: the user states a goal; a capable model studies it together with the platform constraints and writes a plugin plan (`design-plugin`); then the same or a smaller model builds the plugin from that plan (`new-plugin`).

## Contents

- `skill-craft` — the standard: working model, principles, references, acceptance checklist. Loads automatically when relevant.
- Commands (explicit-only, never auto-triggered):

| Stage | Command | What it does |
|---|---|---|
| 00 Design | `design-plugin` | Turn a goal or draft into `ПЛАН.md` |
| 01 Create | `new-plugin` | Build the plugin from the plan into the pipeline testing folder |
| 01 Create | `review-plugin` | Review a plugin against the checklist (read-only) |
| 03 Test | `test-plugin` | Build the eval layer, or grade a run into a PASS/FAIL verdict |
| 03 Test | `deploy-plugin` | Deploy a plugin to the demo stand through the browser |
| 04 Marketing | `demo-video` | Record and edit a client demo video |
| 04 Marketing | `agent-page` | Publish the video and build the client HTML page of the agent |
| 02 Publish | `publish-plugin` | Move to the catalog, push `feature/<alias>`, prepare a PR |
| 02 Publish | `plugins-map` | Update the plugin node in `Plugins-map.md` or analyze merges |

Order: `design → new → review → (test) → (deploy) → (video → page) → publish → map`.

## Install — Claude Code

```
/plugin marketplace add OlegSychugov/skill-craft-plugin
/plugin install skill-craft@skill-craft-marketplace
```

Local checkout: `/plugin marketplace add ./skill-craft-plugin`. Run a command: `/skill-craft:design-plugin <draft-folder>`.

## Install — OpenAI Codex

The repository ships a Codex marketplace index at `.agents/plugins/marketplace.json` and the plugin manifest at `plugins/skill-craft/.codex-plugin/plugin.json`. Add this repository as a Codex plugin marketplace, then install `skill-craft`. Run a command: `$design-plugin <draft-folder>`. Commands carry `agents/openai.yaml` with `allow_implicit_invocation: false`.

## Configuration

Environment addresses are referenced as `<cfg:key>`; values live in `.skill-craft.json` at the workspace root. Keys and rules: `plugins/skill-craft/skills/skill-craft/Референсы/CONFIG.md`; sample: `skill-craft.config.example.json`. If the file is missing, a command asks for the keys it needs.

## Layout

```
.claude-plugin/marketplace.json        Claude Code marketplace
.agents/plugins/marketplace.json       Codex marketplace
plugins/skill-craft/
  .claude-plugin/plugin.json           Claude Code manifest
  .codex-plugin/plugin.json            Codex manifest
  skills/skill-craft/                  the standard + shared Референсы/
  skills/<command>/                    one skill per command, own Референсы/ if needed
scripts/sanitize-public.ps1            strip personal/client data before publishing
scripts/check-public.ps1               fail on anything that must not be public
```

## Maintainers

This repository is the source of truth — edit the skills here directly. It is public: before every push run `scripts/sanitize-public.ps1` and `scripts/check-public.ps1` (exit code 1 on any finding). Proprietary brand assets (`…/Съёмка демо-видео/brand/`) are kept locally and ignored by git; without them the video cards fall back to a brand-coloured gradient.
