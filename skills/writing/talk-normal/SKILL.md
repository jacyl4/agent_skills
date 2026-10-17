---
name: talk-normal
description: Maintain the always-on talk-normal block in Hermes SOUL.md.
license: MIT
metadata:
  version: 0.6.3
  hermes:
    tags: [prompt, anti-slop, concise, system-prompt, chinese, bilingual, always-on]
---

# talk-normal

## Runtime contract

`~/.hermes/SOUL.md` is the single runtime source for talk-normal. The marked block is loaded by Hermes from the active profile's `SOUL.md`; the skill supplies maintenance assets only. Keep one block between:

```text
# --- talk-normal BEGIN ---
# --- talk-normal END ---
```

Third-party source lives at `/home/jacyl4/1base/GitLab/agent_skills/skills/writing/talk-normal/`. Hermes discovers it through `skills.external_dirs`; no separate local copy or discovery symlink is required.

## Install or update

Run the marker-aware synchronizer:

```bash
python3 /home/jacyl4/1base/GitLab/agent_skills/skills/writing/talk-normal/scripts/sync-soul.py
```

It reads `prompt.md`, replaces one existing marked block or appends one block, and writes atomically. It never scans or edits `.hermes.md`, `HERMES.md`, or `AGENTS.md`.

## Reload timing

- `SOUL.md` is loaded fresh for each Hermes message in the current runtime, so the synchronized block applies on the next turn.
- Skill discovery and skill metadata are session-scoped; use `/reset` or start a new session after changing `SKILL.md` or skill directory links.

## Verify

```bash
python3 /home/jacyl4/1base/GitLab/agent_skills/skills/writing/talk-normal/scripts/sync-soul.py --check
```

A successful check reports one synchronized block. The runtime block version should match the comment at the top of `prompt.md`.

## Remove

```bash
python3 /home/jacyl4/1base/GitLab/agent_skills/skills/writing/talk-normal/scripts/sync-soul.py --remove
```

This removes only the marked block from `~/.hermes/SOUL.md`.
