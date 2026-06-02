---
name: crawl4ai
description: "Use Crawl4AI for public web ingest: clean Markdown/HTML from URLs, documentation/site crawling, screenshots/PDFs through the local Crawl4AI server, and RAG/memory source capture. Prefer it over Firecrawl; Firecrawl is disabled on this machine."
---

# Crawl4AI

Use Crawl4AI when a task needs public webpages converted into clean Markdown/HTML or crawled for RAG, memory, code/documentation analysis, or source-grounded summaries.

## Local deployment

- Root: `/opt/ai/crawl4ai`
- Docker service: container `crawl4ai`, image `unclecode/crawl4ai:latest`, restart `unless-stopped`
- REST server: `http://127.0.0.1:11235`
- Health: `crawl4ai-health` or `curl -fsS http://127.0.0.1:11235/health`
- Stack wrapper: `crawl4ai-stack <docker compose args>`
- MCP stdio wrapper for agents: `/usr/local/bin/crawl4ai-mcp`
- Native Crawl4AI SSE endpoint exists at `http://127.0.0.1:11235/mcp/sse`, but Hermes/Codex use the local stdio wrapper because `mcp-remote` timed out against this server during deployment.
- Compatibility note: when REST and `/mcp/schema` are healthy but SSE/`mcp-remote` times out in Hermes/Codex, keep Crawl4AI as the backend and expose a local FastMCP stdio wrapper instead of declaring the server broken. See `references/hermes-stdio-wrapper.md`.

## Tool choice

Prefer Crawl4AI for:
- public docs, blogs, articles, news pages
- converting a URL or URL list into Markdown
- documentation-site crawls
- RAG/memory ingestion with `source_url`, timestamp, and tool metadata

Do not use Crawl4AI for:
- localhost/LAN pages
- logged-in pages or human browser sessions
- clicking, forms, uploads, UI debugging, or screenshots of a user's actual browser state
- pages requiring cookies/tokens unless the user explicitly provides disposable credentials

## REST examples

```bash
curl -s -X POST http://127.0.0.1:11235/md \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}' | jq .

curl -s -X POST http://127.0.0.1:11235/html \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}' | jq .
```

## Hermes / Firecrawl replacement notes

- Firecrawl is intentionally disabled on this machine; do not restore it as the default fallback.
- If `hermes doctor` reports a generic missing-API-key issue after Firecrawl removal, check whether Hermes' native `web` toolset is enabled. On this machine, prefer local SearXNG for native search (`web.backend: searxng`, `web.search_backend: searxng`, `SEARXNG_URL=http://127.0.0.1:8888`) while keeping Crawl4AI as the primary ingest path. `ddgs` remains a lightweight fallback for machines without SearXNG.
- When SearXNG-backed `web_search` fails with `SEARXNG_URL is not set`, distinguish config-file state from running-process environment. `~/.hermes/.env` helps fresh Hermes sessions, but gateway/systemd processes may need an explicit user-service drop-in and restart; the current conversation may need `/reset` or process restart. See `references/searxng-hermes-web-search.md` for the verification ladder and drop-in recipe.
- For the detailed deployment/debug pattern, see `references/hermes-web-ingest-stack.md`.

## Safety

Never pass cookies, session tokens, passwords, Authorization headers, or browser profile secrets to Crawl4AI unless the user explicitly requests it and the credentials are disposable. Firecrawl is intentionally disabled; do not configure or use it as a fallback.
