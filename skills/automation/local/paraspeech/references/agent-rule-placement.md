# Agent rule placement and cleanup

Use this when ParaSpeech default rules were deployed broadly and the user wants home-directory clutter cleaned up.

## Preferred locations

Avoid leaving global rule files directly in the user home directory unless the user explicitly wants `$HOME` to behave as a project/workspace context. Prefer tool-specific dot-directories:

- Claude: `~/.claude/CLAUDE.md`
- Gemini: `~/.gemini/GEMINI.md`
- Agents/Codex/OpenClaw-style rules: `~/.agents/AGENTS.md` and/or the tool's own directory such as `~/.codex/AGENTS.md`
- Cursor/Kiro style always-apply rules: `~/.cursor/rules/*.mdc`, `~/.kiro/steering/*.md`

Root-level `~/AGENTS.md`, `~/CLAUDE.md`, and `~/GEMINI.md` are useful as a crude fallback but can pollute the user's home directory and make every session launched from `$HOME` inherit a project context.

## Safe merge pattern

When moving a deployed rule block out of `$HOME`:

1. Back up both source and target files first, e.g. under `~/.agent-rule-backups/<timestamp>/`.
2. Extract the marker-bounded ParaSpeech block:
   - `<!-- PARASPEECH DEFAULT START -->`
   - `<!-- PARASPEECH DEFAULT END -->`
3. Upsert the block into the destination file: replace an existing ParaSpeech block if present, otherwise append with a blank-line separator.
4. Only delete the root-level source file after verifying the destination exists and contains exactly one start marker and one end marker.
5. Verify root clutter is gone with file existence checks for `~/AGENTS.md`, `~/CLAUDE.md`, `~/GEMINI.md`; ignore similarly named files inside real projects or dependency caches.

## Pitfall

Do not blindly append the root file contents into the dotdir file: this creates duplicate marker blocks and repeated instructions. Use marker-aware upsert.
