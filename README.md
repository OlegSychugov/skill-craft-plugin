# GigaCowork Create Plugin

Marketplace for **Claude Code** and **OpenAI Codex** with one plugin, `create-plugin` — the standard and procedure for building plugins for the GigaCowork catalog (content in Russian).

A plugin built with it works reliably and talks to a **non-technical user** in plain words: no internal skill IDs, paths or tool names in the chat, no streams of failed attempts, no scary confirmations for housekeeping, no manual technical steps, no markup leaking into documents.

## What is inside

```
.claude-plugin/marketplace.json            Claude Code marketplace
.agents/plugins/marketplace.json           Codex marketplace
plugins/create-plugin/
  .claude-plugin/plugin.json               Claude Code manifest
  .codex-plugin/plugin.json                Codex manifest
  skills/create-plugin/
    SKILL.md                               behaviour: how the agent works and talks to the user
    agents/openai.yaml                     explicit invocation only
    skill-craft.config.example.json        sample workspace settings
    Референсы/
      METHODOLOGY.md                       formatting: what the catalog import checks
      HARNESS-DESCRIPTION.md               context: what the GigaCowork sandbox can and cannot do
      CONFIG.md                            `<cfg:…>` keys
  skills/publish-plugin/
    SKILL.md                               publish a tested plugin to the catalog: industry tags, branch, PR
    agents/openai.yaml                     explicit invocation only
    Референсы/PUBLISHING.md                branch regulation, industry tags, PR template
scripts/check-public.ps1                   fail on personal or client data before a push
scripts/sanitize-public.ps1                replace it by local rules
```

The three files of the skill have one role each:

| File | Role |
|---|---|
| `SKILL.md` | **Behaviour.** Layers (platform, agent, skill, script, command), degrees of freedom per step, how the agent names skills, files and tools, talking to the user, working files versus results, commands, build procedure and acceptance checklist |
| `Референсы/METHODOLOGY.md` | **Formatting.** Catalog layout, the 7 categories, YAML canon, skill, command and agent templates, facts that must not come from model memory |
| `Референсы/HARNESS-DESCRIPTION.md` | **Context.** Sandbox capabilities and known tool pitfalls. Not a source of names to copy into prompts |

## Install — Claude Code

```
/plugin marketplace add OlegSychugov/gigacowork-create-plugin
/plugin install create-plugin@gigacowork-create-plugin
```

Local checkout: `/plugin marketplace add ./gigacowork-create-plugin`.

Run: `/create-plugin:create-plugin <draft-folder>`.

## Install — OpenAI Codex

Add this repository as a Codex plugin marketplace (`.agents/plugins/marketplace.json`), then install `create-plugin`. Run: `$create-plugin <draft-folder>`. The skill is explicit-only (`allow_implicit_invocation: false`).

## Usage

The input is a draft folder with `ПЛАН.md`, or with a brief, a task description and sample files. Without a plan the skill first collects the minimum — goal and user, skills and their results, data sources, 3–5 checkable outcomes — writes `ПЛАН.md` and shows it before building. Unknowns stay marked `<TBD>`.

The output is a plugin folder (`plugin.yaml`, `README.md`, `agents/`, `skills/`, `commands/`) ready for the catalog.

Publish a tested plugin: `/create-plugin:publish-plugin <alias>` (Codex: `$publish-plugin <alias>`). The skill asks for confirmation that the plugin works on test data, adds the **«Индустриальные теги»** section at the end of `README.md` (closed list: `#Недвижимость`, `#АПК`, `#Ритейл`, `#Промышленность`, `#Госсектор`), copies the white-listed files to the catalog, creates `feature/<alias>` from the fresh base branch, pushes it and prepares the PR description.

## Configuration

Paths are referenced as `<cfg:key>`; values live in `.skill-craft.json` at the workspace root (the name is kept for compatibility). `create-plugin` uses `todo_dir` and `testing_dir`; `publish-plugin` also uses `catalog_dir`, `plugins_dir`, `hub_repo_url`, `hub_base_branch` and `hub_pr_url`. Keys and rules: `plugins/create-plugin/skills/create-plugin/Референсы/CONFIG.md`; sample: `skill-craft.config.example.json`. If the file is missing, the skill asks for the keys it needs.

## Known platform limitations

Some behaviour cannot be fixed by prompts and should be handled by the platform: English reasoning in the activity feed, failed tool calls shown even when a retry succeeds, internal skill paths in the feed, command parameter fields, saving results back to workspace documents.

## Version

3.1.0 — `publish-plugin` skill: publishing to the catalog with industry tags in README.

3.0.0 — successor of `skill-craft` 3.0.0: split by operations, user-facing behaviour rules, degrees of freedom per step, working files versus results, commands without parameters, facts-not-from-memory policy.

## Maintainers

This repository is public. Before every push run:

```
powershell -ExecutionPolicy Bypass -File scripts/sanitize-public.ps1
powershell -ExecutionPolicy Bypass -File scripts/check-public.ps1
```

`check-public.ps1` exits with code 1 on any finding. Local sanitize rules (`scripts/*.local.json`) are gitignored.
