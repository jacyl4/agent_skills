# Hermes profile web research stack sync

Use when a user asks to align another Hermes profile with the default web research chain.

## Target chain

- `web_search` uses self-hosted SearXNG.
- Public page extraction uses Crawl4AI.
- Dynamic, logged-in, or user-session pages use QWebBridge.
- Scrapling is retained as a specialized fallback definition.
- Firecrawl stays disabled.

## Config fields to align

For the target profile config, usually `~/.hermes/profiles/<profile>/config.yaml`:

```yaml
web:
  backend: searxng
  search_backend: searxng
  extract_backend: ""
  use_gateway: false
```

Copy these `mcp_servers` entries from the source profile when present:

- `qwebbridge` → `/usr/local/bin/qwebbridge-mcp-proxy`, enabled, include browser tools only.
- `crawl4ai` → `/usr/local/bin/crawl4ai-mcp`, enabled, include `md`, `html`, `crawl`, `health`.
- `scrapling` → `/usr/local/bin/scrapling-mcp`, retained as fallback; the default profile keeps it disabled.

When requested for long research/tool output parity, set both source and target profiles:

```yaml
tool_output:
  max_bytes: 50000
  max_lines: 2000
  max_line_length: 2000
```

## Safe update sequence

1. Load both YAML configs and make timestamped backups beside each file.
2. Patch the target `web` block from the source/default profile.
3. Patch only the web-research MCP server entries (`qwebbridge`, `crawl4ai`, `scrapling`), preserving unrelated MCP servers in the target profile.
4. Apply requested `tool_output` limits to each named profile.
5. Verify each profile with `hermes config` and `HERMES_PROFILE=<profile> hermes config`.
6. Tell the user that a new session or `/reset` is normally needed for MCP/tool schema changes to appear.

## Skill-library sync across profiles

Profiles have isolated skill libraries. If the user asks whether this skill exists in another profile, check for:

```text
~/.hermes/profiles/<profile>/skills/devops/local-web-research-stack/SKILL.md
```

If missing, copy the class-level skill directory from the default profile to the target profile path and verify the copied `SKILL.md` checksum matches the source. Keep it as the same class-level skill, not a profile-specific one-off skill.
