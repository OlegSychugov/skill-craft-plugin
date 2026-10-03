# skill-craft marketplace

Marketplace for **Claude Code** and **OpenAI Codex** with the `skill-craft` plugin — a quality standard for authoring skills and plugins plus explicit commands for the whole plugin lifecycle (content in Russian, built for the Giga Cowork `cowork_hub` catalog).

## Contents

- `skill-craft` — the standard: reference map, acceptance checklist, naming, descriptions, progressive disclosure. Loads automatically when relevant.
- Commands (explicit-only, never auto-triggered):

| Command | What it does |
|---|---|
| `new-plugin` | Build a plugin from a draft in `backlog/01. ToDo` into `backlog/02. Testing` |
| `review-plugin` | Review a plugin against the acceptance checklist (read-only) |
| `test-plugin` | Build the eval layer, or grade a run into a PASS/FAIL verdict |
| `deploy-plugin` | Deploy a plugin to the demo stand through the browser |
| `demo-video` | Record and edit a 1:20–1:40 demo video with subtitles |
| `agent-page` | Build the client-facing HTML page of the agent |
| `publish-plugin` | Move to `plugins/`, push `feature/<alias>`, open a PR |
| `plugins-map` | Update the plugin node in `Plugins-map.md` or analyze merges |

Lifecycle: `new-plugin → review-plugin → (test-plugin) → (deploy-plugin) → (demo-video → agent-page) → publish-plugin → plugins-map`.

## Install — Claude Code

```
/plugin marketplace add OlegSychugov/skill-craft-plugin
/plugin install skill-craft@skill-craft-marketplace
```

Local checkout: `/plugin marketplace add ./skill-craft-plugin`.

Run a command: `/skill-craft:new-plugin <draft-folder>`.

## Install — OpenAI Codex

The repository ships a Codex marketplace index at `.agents/plugins/marketplace.json` and the plugin manifest at `plugins/skill-craft/.codex-plugin/plugin.json`. Add this repository as a Codex plugin marketplace, then install `skill-craft` from the plugin picker.

Run a command: `$new-plugin <draft-folder>`. Commands carry `agents/openai.yaml` with `allow_implicit_invocation: false`, so Codex runs them only when named explicitly.

## Configuration

Environment addresses are not hardcoded: the skills reference them as `<cfg:key>`. Put the values into `.skill-craft.json` at the root of your hub repository (see `plugins/skill-craft/skills/skill-craft/skill-craft.config.example.json`): repository and PR URLs, base branch, demo stand, video file share, path to `Plugins-map.md`. If the file is missing, a command asks for the keys it needs, creates the file and adds it to `.git/info/exclude`.

## Layout

```
.claude-plugin/marketplace.json        Claude Code marketplace
.agents/plugins/marketplace.json       Codex marketplace
plugins/skill-craft/
  .claude-plugin/plugin.json           Claude Code manifest
  .codex-plugin/plugin.json            Codex manifest
  skills/skill-craft/                  the standard + Референсы/
  skills/<command>/SKILL.md            one skill per command
scripts/sync-from-source.ps1           refresh content from the source of truth
```

## Maintainers

The source of truth is `.kilo/skills/skill-craft/` in `cowork_hub`. To refresh the plugin content (everything except the marketplace `SKILL.md`):

```
powershell -ExecutionPolicy Bypass -File scripts/sync-from-source.ps1
```

If the source `SKILL.md` changed, port the changes to `plugins/skill-craft/skills/skill-craft/SKILL.md` by hand and bump the version in all four manifests.

This repository is public. The sync runs `scripts/sanitize-public.ps1` (strips personal names, client workspace and file-share links, real company names, injected scripts) and then `scripts/check-public.ps1`, which exits with code 1 on any finding. Run `check-public.ps1` before every push; when it reports something new, add a rule to `sanitize-public.ps1`.
