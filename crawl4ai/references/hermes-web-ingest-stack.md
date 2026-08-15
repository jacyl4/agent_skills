# Hermes web ingest stack notes

Use this when maintaining the local web-ingest stack that replaced Firecrawl with Crawl4AI + Scrapling + QWebBridge.

## Intended routing

- SearXNG: search only. Prefer Hermes native `web_search` via the `search` toolset, not the full `web` toolset, when `web.extract_backend` is empty; this keeps broken native `web_extract` out of the model schema.
- QWebBridge: real Chrome/browser interaction, logged-in pages, UI forms, screenshots, localhost/LAN debugging.
- Crawl4AI: default public webpage ingest, URL-to-Markdown/HTML, documentation-site crawling, RAG/memory source capture.
- Scrapling: dynamic rendering, anti-bot/stealth, selector/XPath extraction, structured scraping when Crawl4AI is insufficient.
- Firecrawl: intentionally disabled unless the user explicitly asks to restore it.

## Token-efficient Hermes defaults

When Crawl4AI/Scrapling/QWebBridge are enabled as MCP servers, do not leave all discovered MCP tools exposed by default. Full Scrapling schemas are especially expensive. Use `mcp_servers.<name>.tools.include` plus `resources: false` and `prompts: false` to keep the always-on schema small:

```yaml
platform_toolsets:
  cli:
    # ... normal defaults ...
    - search       # web_search only; avoids native web_extract when SearXNG is search-only

mcp_servers:
  crawl4ai:
    command: /usr/local/bin/crawl4ai-mcp
    enabled: true
    tools:
      resources: false
      prompts: false
      include: [md, html, crawl, health]
  scrapling:
    command: /usr/local/bin/scrapling-mcp
    enabled: false   # keep full Scrapling MCP off by default; its schema is large
    tools:
      resources: false
      prompts: false
      include: [get, fetch, stealthy_fetch]
```

For on-demand Scrapling without the full MCP schema, use the custom lightweight Hermes tool `scrapling_fetch` in the `scrapling_lite` toolset. It exposes one small schema and proxies `/opt/ai/scrapling` modes `get`, `fetch`, and `stealth` through a subprocess.

For Codex/OMX, do not mirror Hermes' SearXNG search path by adding another search MCP: Codex has native `--search`. Keep Crawl4AI/QWebBridge MCP enabled, remove default Scrapling MCP, and use `scrapling-fetch-lite` on demand. See `references/codex-omx-web-ingest-token-optimization.md`.

After changing this, run `hermes mcp list`, restart/reload the gateway or current CLI session, and verify agent logs show Scrapling MCP is disabled while `scrapling_fetch` remains in the CLI tool schema.

## Cross-agent configuration notes

- Hermes default profile uses `search` + Crawl4AI/QWebBridge MCP + lightweight `scrapling_fetch`; full Scrapling MCP stays disabled by default.
- Codex and oh-my-codex (OMX) share `~/.codex/config.toml`. Audit them separately: a `scrapling` MCP block there can reintroduce the same schema-cost problem outside Hermes.
- See `references/codex-omx-web-ingest-token-audit.md` for measured Codex/OMX schema costs and the recommended on-demand Scrapling wrapper pattern.

## Durable deployment shape

- Crawl4AI root: `/opt/ai/crawl4ai`
- Crawl4AI REST: `http://127.0.0.1:11235`
- Crawl4AI stable wrappers:
  - `/usr/local/bin/crawl4ai-stack`
  - `/usr/local/bin/crawl4ai-health`
  - `/usr/local/bin/crawl4ai-mcp`
- Scrapling root: `/opt/ai/scrapling`
- Scrapling stdio MCP: `/usr/local/bin/scrapling-mcp`
- Scrapling HTTP MCP service: `scrapling-mcp-http.service` on `127.0.0.1:18000`
- QWebBridge MCP proxy: `/usr/local/bin/qwebbridge-mcp-proxy`

## Hermes doctor pitfall after disabling Firecrawl

Hermes' native `web` toolset may still be enabled even when operational web ingest is handled by Crawl4AI/Scrapling. If Firecrawl keys are removed and no Exa/Tavily/Parallel/etc. key is configured, `hermes doctor` can show a generic final issue about missing API keys for full tool access.

Preferred fix that keeps Firecrawl disabled:

1. Install/use a non-Firecrawl native backend if native `web_search` should remain available. A simple local option is `ddgs` in the Hermes venv.
2. Configure:

```bash
hermes config set web.backend ddgs
hermes config set web.search_backend ddgs
hermes config set web.extract_backend ''
```

3. Verify:

```bash
hermes doctor
hermes mcp test crawl4ai
hermes mcp test scrapling
```

If Hermes doctor still promotes optional unused toolsets like `moa` or `x_search` into a final issue, inspect whether they are actually enabled in `platform_toolsets`. Warnings for unconfigured optional integrations are acceptable; final issues should be reserved for enabled surfaces the user expects to work.

## Smoke tests

```bash
crawl4ai-health
curl -fsS -X POST http://127.0.0.1:11235/md \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'
hermes mcp test crawl4ai
hermes mcp test scrapling
```
