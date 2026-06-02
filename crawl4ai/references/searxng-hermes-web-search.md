# Hermes SearXNG web_search integration notes

Use these notes when replacing Hermes native `web_search` with local SearXNG while keeping Crawl4AI/Scrapling as extraction backends.

## Stable shape

- SearXNG provides search only via JSON API: `http://127.0.0.1:8888/search?q=...&format=json`.
- Hermes native tool name remains `web_search`; the durable change is the backend selection:
  - `web.backend: searxng`
  - `web.search_backend: searxng`
  - `SEARXNG_URL=http://127.0.0.1:8888`
- Crawl4AI and Scrapling remain MCP extraction/rendering tools. Do not set `web.extract_backend: scrapling` unless Hermes has an explicit extract provider for it; native `web_extract` provider names differ from MCP tools.

## Environment propagation pitfall

Writing `SEARXNG_URL` to `~/.hermes/.env` makes fresh Hermes CLI/API sessions load the URL, but an already-running conversation/tool process may still fail with:

```json
{"success": false, "error": "SEARXNG_URL is not set"}
```

For gateway deployments, add an explicit systemd user drop-in so process-level env checks and gateway-spawned tool calls see the variable:

```ini
# ~/.config/systemd/user/hermes-gateway.service.d/10-searxng.conf
[Service]
Environment="SEARXNG_URL=http://127.0.0.1:8888"
```

Then reload and restart:

```bash
systemctl --user daemon-reload
systemctl --user restart hermes-gateway.service
```

For the current CLI/Web conversation, start a fresh session or reset/restart the process; tool schemas/env are captured at process/session startup.

## Verification ladder

1. SearXNG service:
   ```bash
   curl -fsS 'http://127.0.0.1:8888/search?q=hermes+agent&format=json' | jq '.results | length'
   ```
2. Hermes config/env files:
   ```bash
   grep -A5 '^web:' ~/.hermes/config.yaml
   grep '^SEARXNG_URL=' ~/.hermes/.env
   ```
3. Gateway process env:
   ```bash
   PID=$(systemctl --user show -p MainPID --value hermes-gateway.service)
   tr '\0' '\n' < /proc/$PID/environ | grep '^SEARXNG_URL='
   ```
4. Fresh Hermes process search:
   ```bash
   hermes chat -q 'Use web_search to search exactly: site:github.com NousResearch hermes-agent. Return only success and first URL.' --toolsets web -Q
   ```

If direct SearXNG and fresh Hermes succeed while the current session's tool call fails, the fix is session/process reload, not SearXNG redeployment.