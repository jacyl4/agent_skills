---
name: hermes-agent-ops
description: Manages and operates various aspects of Hermes agent functionality, including
  backup migration, deployment optimization, and runtime operations.
commands:
- agent-backup-migration-audit: Handles auditing backup directories and outlining
    migration paths.
- agent-tool-opt-ai-deployment: Focuses on deploying and optimizing AI agent tools
    and skill bundles.
maintainer_notes: 'This umbrella skill consolidates various operations related to
  Hermes agent management and deployment. It aims to provide a central point for managing
  agent-related tasks and configurations.

  '
pinned: false
tags:
- agent
- devops
- hermes
- operations
metadata:
  targets:
  - hermes
---

# Hermes Agent Operations

This skill consolidates various operations related to managing and optimizing Hermes agents.

## Agent Backup Migration and Auditing

### `agent-backup-migration-audit`

This skill provides functionality to audit Hermes/AI-agent backup directories and produce selective migration outlines. It is designed to help manage and maintain agent data integrity and facilitate migrations without compromising current state or leaking secrets.

## AI Agent Tool Deployment and Optimization

### `agent-tool-opt-ai-deployment`

This skill focuses on deploying AI/agent companion tools and skill/plugin bundles. It ensures these components are correctly integrated into agent environments (e.g., /opt/ai) and are discoverable by agent frameworks.

## Community Skill Installation and Reinstall Operations

When reinstalling Hermes skills from community sources, verify the install from Hermes output and the skill list rather than trusting the process exit code. Some scanner-blocked installs may print `Installation blocked` even with exit code 0, and `--force` may not override a `DANGEROUS` community-source verdict. If the user explicitly requested the source, review/fetch the upstream skill and install manually into `~/.hermes/skills/<skill-name>/`, preserving support files and script executable bits, then verify with `hermes skills list` and `/skill <name>`.

Reference: `references/community-skill-dangerous-install.md` covers the exact blocked-output shape, cleanup pattern, and safe manual-install workaround.

## Hermes-Scoped Always-On Prompt Rules

For this user, do not place Hermes-only default behavior in `/home/jacyl4/AGENTS.md` or other user-root context files unless they explicitly ask for a cross-tool/workspace rule. For high-frequency Hermes defaults, integrate under the active Hermes profile instead:

- Put global Hermes identity/style rules in `~/.hermes/SOUL.md`; Hermes loads this from `HERMES_HOME` independent of cwd.
- Keep installed skill assets under `~/.hermes/skills/<name>/`.
- If a tool installer creates a root-level `AGENTS.md` containing only the managed block, move it into `~/.hermes/backups/` before migrating the block to `SOUL.md`.
- Verify with Hermes code path, e.g. `agent.prompt_builder.load_soul_md()`, not only file existence.

## Hermes Auxiliary Model Routing

When tuning Hermes `auxiliary.*` routes for this user, use a Grok-first policy: route tasks to Grok wherever the route works, because Grok cost is currently secondary. Use Gemini selectively for explicit economy-first cases or when a task specifically benefits from Gemini's cost profile. Always back up `~/.hermes/config.yaml`, use `hermes config set`, verify router resolution plus real `call_llm()` smoke tests, then restart the gateway for runtime sessions.

Reference: `references/auxiliary-grok-routing.md` contains the current Grok-first routing pattern, validated tasks, smoke-test script, and pitfalls.

## Hermes Media Tool Configuration

For Hermes image/video setup questions, separate four routes explicitly: image analysis uses `vision_analyze` and `auxiliary.vision`; image generation uses `image_gen` / `image_generate`; video generation uses `video_gen` / `video_generate`; video analysis uses the `video` toolset / `video_analyze`. For xAI setups, prefer the `hermes tools` interactive backend picker when available because plugin/provider key names can shift across Hermes releases; then verify with `hermes tools list`, `hermes config`, and a new session or `/reset` so tool schemas refresh.

When debugging "image generation failed", test both active routes independently before changing config: (1) call the built-in `image_generate` tool with a tiny diagnostic prompt and verify the output file with `file`/`stat`; (2) if the `apikey-image-gen` skill or Web UI media endpoint is involved, POST to `/api/hermes/media/apikey-image-generate` with `X-Hermes-Profile` and capture the JSON error. A `missing_fun_codex_provider` response means the selected profile lacks `custom_providers[].name: fun-codex`; the built-in xAI image route may still be healthy.

Reference: `references/media-tools-grok-routing.md` captures the Grok image/video/vision distinction and config-check pattern. Reference: `references/image-generation-route-debugging.md` captures the dual-route diagnostic procedure for built-in xAI vs Web UI `fun-codex` failures.

## Linux Runtime Maintenance

For Dashboard/Web UI/Gateway memory pressure, stale TUI/MCP children, DNS failures, SQLite WAL-reset warnings, or swap recovery, use `references/linux-runtime-maintenance.md`. It records the verified cgroup sampler, safe process-group cleanup, MCP log rotation, Gateway exit classification, encrypted dual-resolver pattern, SQLite 3.51.3 + FTS5 runtime override, and swap safety checks.

## Related Skills

*   `hermes-runtime-debugging`: For debugging Hermes Agent runtime issues.
*   `shared-agent-memory-ops`: For managing shared agent memory layers.
