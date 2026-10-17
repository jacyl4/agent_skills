---
name: hermes-local-ai-stack-ops
description: Use when operating, verifying, or extending the user's local /opt/ai
  tool stack for Hermes and companion agents, including RTK, Graphify, OfficeCLI,
  wrappers, and shared skill layout.
metadata:
  targets:
  - hermes
---

# Hermes Local AI Stack Ops

Use this skill when a task touches locally installed AI tools, wrappers, shared skills, or Hermes-adjacent agent runtime integration on this machine.

## Stable layout

- AI tools live under `/opt/ai`, one project per folder.
- External skills live under `/home/jacyl4/1base/GitLab/agent_skills` with symlinks into agent-specific skill directories.

## Installed tools

### RTK

- Source/project: `/opt/ai/rtk`
- Executable: `/usr/local/bin/rtk`
- Hermes terminal proxy config:
  - `terminal.rtk_proxy_enabled=true`
  - `terminal.rtk_path=/usr/local/bin/rtk`
  - `terminal.rtk_ultra_compact=true`

Verify:

```bash
command -v rtk
rtk --help
hermes config | grep -i rtk
```

### Graphify

- Project: `/opt/ai/graphify`
- Wrappers:
  - `/usr/local/bin/graphify`
  - `/usr/local/bin/graphify-ai`
- Skills/rules deployed across local agent tools.

Verify:

```bash
command -v graphify graphify-ai
graphify --help || true
```

### OfficeCLI

- Project: `/opt/ai/officecli`
- Wrappers:
  - `/usr/local/bin/officecli`
  - `/usr/local/bin/officecli-ai`
- Default tool for Office document creation, analysis, proofreading, and modification.
- Skills/rules deployed across local agent tools.

Verify:

```bash
command -v officecli officecli-ai
officecli --help || true
```

## Operating rules

1. Install new AI tools under `/opt/ai/<tool-name>`.
2. Expose stable wrappers under `/usr/local/bin` when useful.
3. Put reusable workflows in skills; keep Hermes built-in memory as a short routing index.
4. Verify wrappers with `command -v` and a smoke command before reporting success.

## Pitfalls

- Do not store full deployment logs or one-off results in built-in memory.
- Keep exact ports, service units, and wrapper paths in skills where they can be loaded on demand.
