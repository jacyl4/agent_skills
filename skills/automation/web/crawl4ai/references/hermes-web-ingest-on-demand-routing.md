# Hermes web ingest: on-demand routing and profile split

Use this note when optimizing Hermes web-ingest cost/performance with local SearXNG + Crawl4AI + Scrapling + QWebBridge.

## Durable routing pattern

- Default profile should be **research-lite**:
  - native `web_search` via SearXNG only (`search` toolset, not full `web`)
  - Crawl4AI MCP enabled for normal public page Markdown/HTML ingest
  - QWebBridge MCP enabled only if real-browser/session interaction is commonly needed
  - Scrapling MCP disabled by default so its large schemas do not ride every model call
- Create a separate **web-full** profile for validation/fallback work:
  - same SearXNG + Crawl4AI defaults
  - Scrapling MCP enabled with a small include list, usually `get`, `fetch`, `stealthy_fetch`

## Why

Scrapling tool schemas are large even after trimming. Keeping Scrapling resident increases every model API call, whether or not the model uses it. Moving Scrapling into a profile used only for dynamic/anti-bot verification preserves capability without imposing default cost.

## Verification commands

```bash
hermes mcp list
hermes --profile web-full mcp list

cd ~/.hermes/hermes-agent
venv/bin/python - <<'PY'
import json
from hermes_cli.config import load_config
from hermes_cli.tools_config import _get_platform_tools
from tools.mcp_tool import discover_mcp_tools, shutdown_mcp_servers
from model_tools import get_tool_definitions
try:
    discover_mcp_tools()
    toolsets = _get_platform_tools(load_config(), 'cli')
    schemas = get_tool_definitions(enabled_toolsets=toolsets, quiet_mode=True)
    names = [s['function']['name'] for s in schemas]
    raw = json.dumps(schemas, ensure_ascii=False)
    print('count', len(schemas), 'chars', len(raw), 'approx_tokens', len(raw)//4)
    print('scrapling_names', [n for n in names if n.startswith('mcp_scrapling')])
finally:
    shutdown_mcp_servers()
PY
```

For named-profile schema measurement from a raw Python process, set `HERMES_HOME` to the named profile root, for example:

```bash
HERMES_HOME=/home/jacyl4/.hermes/profiles/web-full \
  ~/.hermes/hermes-agent/venv/bin/python schema_probe.py
```

`HERMES_PROFILE=web-full` alone is not sufficient for direct module-level probes; the normal CLI `--profile` flag handles profile routing for Hermes commands.

## Gateway application

After changing default MCP profile configuration, restart or reload the gateway/current session. Logs should show only the expected resident MCP tools, for example Crawl4AI + QWebBridge but no Scrapling in research-lite mode.
