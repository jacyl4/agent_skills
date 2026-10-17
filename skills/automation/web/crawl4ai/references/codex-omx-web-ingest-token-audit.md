# Codex / OMX web-ingest token audit

Use this when maintaining Codex or oh-my-codex (OMX) web-ingest configuration on this machine.

## Problem pattern

Codex and OMX share `~/.codex/config.toml`. If `scrapling` is registered as a normal MCP server there, Codex/OMX may carry the full Scrapling MCP tool schema into model calls even when Scrapling is not used.

Observed configuration shape:

```toml
[mcp_servers.qwebbridge]
command = "/usr/local/bin/qwebbridge-mcp-proxy"

[mcp_servers.crawl4ai]
command = "/usr/local/bin/crawl4ai-mcp"

[mcp_servers.scrapling]
command = "/usr/local/bin/scrapling-mcp"
```

## Measured schema footprint

Direct MCP `list_tools` measurement on this host:

| Server | Tools | Approx schema chars | Approx tokens |
|---|---:|---:|---:|
| QWebBridge | 17 | 5,904 | 1,476 |
| Crawl4AI | 5 | 1,760 | 440 |
| Scrapling | 10 | 51,010 | 12,752 |

Scrapling is the dominant cost. Crawl4AI and QWebBridge are comparatively acceptable if the user wants those capabilities available.

## Recommended Codex/OMX shape

Keep:

- `crawl4ai` MCP for ordinary public web Markdown/HTML/crawl.
- `qwebbridge` MCP for real-browser/login/UI/screenshot verification.
- `context7` MCP if already configured for library docs.

Remove or disable:

- `scrapling` MCP as an always-on Codex/OMX server.

Use a lightweight shell wrapper or small custom tool for Scrapling on demand, mirroring Hermes' `scrapling_fetch` pattern: one compact interface with modes `get`, `fetch`, and `stealth`, output capped and selector-aware.

## Commands

Inspect:

```bash
codex mcp list
codex mcp get scrapling
```

Remove Scrapling MCP from Codex/OMX:

```bash
codex mcp remove scrapling
```

Or manually remove this TOML block from `~/.codex/config.toml`:

```toml
[mcp_servers.scrapling]
command = "/usr/local/bin/scrapling-mcp"
```

Then update `~/.codex/AGENTS.md` so the web-ingest block says Scrapling is on-demand via the lightweight wrapper, not default MCP.

## Prompt wording

Preferred wording for Codex/OMX AGENTS.md:

```md
- Crawl4AI: default public-web ingest and URL-to-Markdown/HTML/crawl path. MCP command: `/usr/local/bin/crawl4ai-mcp`.
- QWebBridge: real Chrome/browser interaction, login-session pages, forms, screenshots, and UI debugging. MCP command: `/usr/local/bin/qwebbridge-mcp-proxy`.
- Scrapling: do not keep full Scrapling MCP registered by default because its schema is large. When Crawl4AI fails or JS/anti-bot validation is needed, call the lightweight Scrapling wrapper/tool with modes `get`, `fetch`, or `stealth` and capped output.
```

## Pitfalls

- Do not solve this with an extra Hermes profile; the user rejected profile-based routing for this class of optimization.
- Do not remove Crawl4AI just because web ingest exists elsewhere; its schema footprint is small and it is the default public-page reader.
- Do not harden transient setup failures into a rule. The durable rule is about schema cost and routing, not about a server being broken.
