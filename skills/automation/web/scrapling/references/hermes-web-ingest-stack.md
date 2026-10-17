# Scrapling in the local Firecrawl-free web ingest stack

Use these notes when Scrapling is deployed alongside Crawl4AI and QWebBridge under `/opt/ai`.

## Role boundary

- Crawl4AI handles ordinary public URL-to-Markdown/HTML and documentation crawl jobs.
- Scrapling handles dynamic rendering, stealth/anti-bot, adaptive selector relocation, persistent browser sessions, and structured extraction.
- QWebBridge handles real Chrome/user-session operations.
- Firecrawl stays disabled unless the user explicitly requests restoring it.

## Durable service shape

- Root: `/opt/ai/scrapling`
- CLI wrapper: `/usr/local/bin/scrapling-ai`
- Stdio MCP wrapper: `/usr/local/bin/scrapling-mcp`
- HTTP MCP wrapper: `/usr/local/bin/scrapling-mcp-http`
- User service: `scrapling-mcp-http.service`
- HTTP endpoint: `http://127.0.0.1:18000/mcp`

## Verification

```bash
systemctl --user is-enabled scrapling-mcp-http.service
systemctl --user is-active scrapling-mcp-http.service
scrapling-ai --help
hermes mcp test scrapling
```

Functional smoke from a Hermes session can call Scrapling's MCP `get` against `https://example.com` and expect HTTP 200 plus markdown/text content.

## Doctor pitfall

If Hermes doctor reports a generic final issue after Firecrawl removal, the issue is usually Hermes' native `web`, `moa`, or `x_search` optional API-key checks — not Scrapling. Keep Scrapling unchanged and fix native `web` separately, e.g. with a non-Firecrawl backend such as `ddgs` if the native web toolset is enabled.
