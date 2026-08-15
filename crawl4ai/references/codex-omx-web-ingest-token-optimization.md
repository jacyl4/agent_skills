# Codex / OMX web-ingest token optimization

Use this note when maintaining Codex CLI / oh-my-codex (OMX) web-ingest tooling on this machine.

## Durable lesson

Codex already has a native web-search capability via `codex --search`, which exposes the Responses `web_search` tool. Do not add a separate SearXNG MCP/tool to Codex/OMX just to duplicate search.

Keep the always-on Codex/OMX MCP surface focused on tools that add capabilities not covered by native search:

- `crawl4ai` MCP: keep enabled for URL-to-Markdown/HTML/crawl extraction. Its schema is small.
- `qwebbridge` MCP: keep enabled for real Chrome, login/session pages, UI interaction, screenshots, and browser verification.
- `scrapling` MCP: do **not** keep enabled by default. Its schema is large; use an on-demand shell wrapper instead.

## Observed schema sizes from this setup

Approximate raw MCP schemas measured from the local servers:

| Server | Tools | Approx schema tokens | Guidance |
|---|---:|---:|---|
| qwebbridge | 17 | ~1.5k | acceptable when browser validation matters |
| crawl4ai | 5 | ~0.4k | keep enabled |
| scrapling | 10 | ~12.7k | too large for default Codex/OMX MCP |

## Current preferred Codex/OMX routing

```text
Search/current facts:
  codex --search native web_search

Normal public webpage extraction:
  crawl4ai MCP

Real browser/login/UI/screenshot validation:
  qwebbridge MCP

Dynamic / anti-bot / selector fallback after Crawl4AI fails:
  scrapling-fetch-lite get|fetch|stealth URL
```

## Config shape

`~/.codex/config.toml` should keep Crawl4AI and QWebBridge but omit Scrapling:

```toml
[mcp_servers.qwebbridge]
command = "/usr/local/bin/qwebbridge-mcp-proxy"

[mcp_servers.crawl4ai]
command = "/usr/local/bin/crawl4ai-mcp"
```

Do not include this by default:

```toml
[mcp_servers.scrapling]
command = "/usr/local/bin/scrapling-mcp"
```

## On-demand Scrapling wrapper

Use the lightweight shell wrapper instead of MCP:

```bash
scrapling-fetch-lite get https://example.com --output markdown --max-chars 6000
scrapling-fetch-lite fetch https://example.com --output text --wait 1000
scrapling-fetch-lite stealth https://example.com --selector main --max-chars 4000
```

The wrapper should emit compact JSON on stdout and send Scrapling logs to stderr so Codex/OMX can parse the result.

## AGENTS.md guidance

`~/.codex/AGENTS.md` should explicitly say:

- Codex native `--search` handles broad/current web search.
- Crawl4AI remains the default URL extraction path.
- Scrapling MCP is intentionally not registered by default because its schema is large.
- Use `scrapling-fetch-lite` only when Crawl4AI is insufficient.

## Verification commands

```bash
codex mcp list
# Expected: crawl4ai and qwebbridge enabled; no scrapling MCP.

scrapling-fetch-lite get https://example.com --max-chars 800 --timeout 20 \
  > /tmp/sfl.out 2>/tmp/sfl.err
python3 -m json.tool /tmp/sfl.out >/dev/null

omx doctor
# Warnings unrelated to web ingest are acceptable; ensure no MCP failure is introduced.
```
