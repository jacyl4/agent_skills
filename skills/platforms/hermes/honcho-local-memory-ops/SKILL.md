---
name: honcho-local-memory-ops
description: Use when operating, verifying, tuning, or integrating the user's local
  Honcho long-term memory service with Hermes, Codex, OMX, or other agents.
metadata:
  targets:
  - hermes
---

# Honcho Local Memory Ops

Use this skill when a task involves local Honcho, Hermes external memory providers, Codex/OMX memory integration, semantic memory, or long-term memory routing.

## Local service

- Repo/project: `/opt/ai/honcho/repo`
- Runtime: Docker Compose + `honcho-local.service`
- API: `http://127.0.0.1:8000`
- API version observed: `v3.0.9`, git `f75b336`
- Hermes memory provider: `honcho`

Verify:

```bash
hermes memory status
hermes honcho status || true
curl -s http://127.0.0.1:8000/health || true
systemctl status honcho-local.service --no-pager || true
```

## Hermes tuning currently used

- Context: `400/5`
- Dialectic: `12 low`
- Async writes enabled
- Deriver batch: `512`
- Vector sync: `120s`
- Embedding model: `gemini-embedding-001`
- Embedding dimensions: `1536d`

## Codex / OMX integration

- `~/.codex/config.toml` exports `HONCHO_*` env.
- `~/.codex/AGENTS.md` documents local Honcho usage.
- `~/.codex/skills/honcho-memory/SKILL.md` documents workflow.
- `/usr/local/bin/honcho-memory` wraps Hermes Honcho tools for:
  - search
  - conclude
  - profile
  - context
  - reason

Verify:

```bash
test -f ~/.codex/config.toml && grep -n 'HONCHO' ~/.codex/config.toml || true
test -x /usr/local/bin/honcho-memory && honcho-memory --help || true
```

## Memory architecture

- Hermes built-in memory is a short routing index injected at session start.
- Honcho is the long-term semantic memory layer.
- `session_search` is for verbatim past-session recall.
- Skills hold reusable procedures, deployment manuals, and tool-specific facts.
- For cross-agent memory architecture and built-in memory triage, prefer the umbrella skill `shared-agent-memory-ops`; keep this skill focused on this machine's local Honcho details.

## Pitfalls

- Keep one-off task outcomes and stale IDs out of built-in memory.
- Store operational procedures in skills.
- Store durable behavioral/profile conclusions in Honcho.
