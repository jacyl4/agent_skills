---
name: local-web-research-stack
description: 'Use when choosing, configuring, verifying, or troubleshooting the user''s
  local web search and web ingestion stack: SearXNG, Crawl4AI, QWebBridge, Scrapling,
  and Firecrawl-disabled routing.'
metadata:
  targets:
  - hermes
---

# Local Web Research Stack

Use this skill when a task involves web search, public page extraction, dynamic browser automation, logged-in browser sessions, or scraping fallbacks on this machine.

## Routing order

1. `web_search` / SearXNG for broad search.
2. Crawl4AI for public page Markdown/HTML extraction.
3. QWebBridge for real-browser, dynamic, logged-in, or user-session pages.
4. Scrapling Lite as a specialized scraping fallback.
5. Firecrawl is disabled.

## Components

### SearXNG

- Hermes official `web_search` is configured for self-hosted SearXNG.
- Endpoint/container: `http://127.0.0.1:8888`, container `ai-searxng`.

Verify:

```bash
curl -s 'http://127.0.0.1:8888/search?q=hermes&format=json' | head
```

### Crawl4AI

- Project: `/opt/ai/crawl4ai`
- Docker service exposed on `127.0.0.1:11235`
- Wrapper: `/usr/local/bin/crawl4ai-mcp`

Verify:

```bash
curl -s http://127.0.0.1:11235/health || true
command -v crawl4ai-mcp
```

### QWebBridge

- Project: `/opt/ai/qwebbridge`
- Persistent daemon endpoint: `http://127.0.0.1:10086`
- MCP proxy wrapper: `/usr/local/bin/qwebbridge-mcp-proxy`
- Use the proxy wrapper for Hermes, Codex/OMX, Grok, and other MCP clients when the persistent daemon is active.
- Grok CLI has QWebBridge configured in `~/.grok/config.toml` as `[mcp_servers.qwebbridge]` with command `/usr/local/bin/qwebbridge-mcp-proxy`; skill copied to `~/.grok/skills/qweb-bridge`.

Verify:

```bash
curl -s http://127.0.0.1:10086/health
command -v qwebbridge-mcp-proxy
grok mcp doctor qwebbridge || true
```

### Scrapling

- Project: `/opt/ai/scrapling`
- venv-based install
- Wrapper: `/usr/local/bin/scrapling-mcp`
- HTTP service: `scrapling-mcp-http.service` at `127.0.0.1:18000`

Verify:

```bash
command -v scrapling-mcp
systemctl --user status scrapling-mcp-http.service --no-pager || true
curl -s http://127.0.0.1:18000/health || true
```

## Hermes profile sync

When aligning another Hermes profile with this stack, use `references/hermes-profile-web-stack-sync.md` as the repeatable recipe. Preserve the target profile's unrelated config, copy only the web research chain settings, create timestamped backups, and verify with both `hermes config` and `HERMES_PROFILE=<profile> hermes config`.

Recommended parity settings for research-heavy profiles:

```yaml
web:
  backend: searxng
  search_backend: searxng
  extract_backend: ""
  use_gateway: false
tool_output:
  max_bytes: 50000
  max_lines: 2000
  max_line_length: 2000
```

Profiles have isolated skill libraries. When the user wants this stack available in a second profile, copy this class-level skill directory to `~/.hermes/profiles/<profile>/skills/devops/local-web-research-stack/` and verify the copied `SKILL.md` checksum matches the source.

## Pitfalls

- Use QWebBridge for pages that need the user's Chrome login/session state.
- Use Crawl4AI for clean Markdown from public docs and articles.
- Firecrawl is intentionally disabled in this environment.
- MCP/tool schema changes usually require a new session or `/reset` before the active agent sees newly synchronized tools or skills.
