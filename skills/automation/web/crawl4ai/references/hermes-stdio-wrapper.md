# Crawl4AI Hermes/Codex stdio wrapper pattern

Use this when Crawl4AI's HTTP REST endpoints work but native SSE MCP or `mcp-remote` is unreliable/slow in Hermes or Codex.

## Symptom

- `curl http://127.0.0.1:11235/health` returns `status=ok`.
- `curl http://127.0.0.1:11235/mcp/schema` lists native tools.
- Direct REST calls such as `POST /md` work.
- `hermes mcp add --url http://127.0.0.1:11235/mcp/sse` or `mcp-remote http://127.0.0.1:11235/mcp/sse --allow-http` times out during `hermes mcp test`.

## Durable fix

Create a local stdio MCP wrapper that exposes a small stable tool surface and calls Crawl4AI REST internally. This avoids depending on Hermes/Codex SSE behavior while keeping Crawl4AI as the backend.

Recommended stable command:

```text
/usr/local/bin/crawl4ai-mcp
```

Recommended deployed script path:

```text
/opt/ai/crawl4ai/scripts/crawl4ai-mcp
```

## Minimal wrapper shape

Use `mcp.server.fastmcp.FastMCP`, `httpx`, and expose these tools first:

- `md(url, params=None)` -> `POST /md`
- `html(url, params=None)` -> `POST /html`
- `crawl(urls, browser_config=None, crawler_config=None, extra=None)` -> `POST /crawl`
- `health()` -> `GET /health`
- `schema()` -> `GET /mcp/schema`

Run with:

```python
if __name__ == "__main__":
    mcp.run()
```

The wrapper can reuse an existing Python environment that already has `mcp` and `httpx`, but prefer documenting that dependency explicitly in the deployment notes.

## Hermes config

```yaml
mcp_servers:
  crawl4ai:
    command: /usr/local/bin/crawl4ai-mcp
    enabled: true
```

Verify:

```bash
hermes mcp test crawl4ai
curl -fsS -X POST http://127.0.0.1:11235/md \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}' | jq -r '.markdown[0:120]'
```

Expected MCP discovery should include at least `md`, `html`, `crawl`, `health`, and `schema`.

## Codex / OMX config

```toml
[mcp_servers.crawl4ai]
command = "/usr/local/bin/crawl4ai-mcp"
```

Then verify:

```bash
codex mcp get crawl4ai
omx doctor --verbose
```

## Reporting guidance

When documenting the deployment, distinguish these states clearly:

- Crawl4AI REST is healthy.
- Crawl4AI native SSE/schema exists.
- Hermes/Codex use the stdio wrapper intentionally because it proved more reliable in local testing.

Do not record this as "Crawl4AI SSE is broken"; treat it as a stable local compatibility pattern.