# Hermes web ingest stack notes

Use this when maintaining the local web-ingest stack that replaced Firecrawl with Crawl4AI + Scrapling + QWebBridge.

## Intended routing

- QWebBridge: real Chrome/browser interaction, logged-in pages, UI forms, screenshots, localhost/LAN debugging.
- Crawl4AI: default public webpage ingest, URL-to-Markdown/HTML, documentation-site crawling, RAG/memory source capture.
- Scrapling: dynamic rendering, anti-bot/stealth, selector/XPath extraction, structured scraping when Crawl4AI is insufficient.
- Firecrawl: intentionally disabled unless the user explicitly asks to restore it.

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
