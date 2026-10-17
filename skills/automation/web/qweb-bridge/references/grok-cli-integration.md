# Grok CLI QWebBridge integration

Use this when the user asks to give Grok CLI browser/QWebBridge capability.

## Known-good global setup

1. Verify QWebBridge daemon + extension first:

```bash
curl -s http://127.0.0.1:10086/health
```

Healthy shape includes `running:true` and `extensions_connected:true`.

2. Configure Grok MCP server in `~/.grok/config.toml`:

```toml
[mcp_servers.qwebbridge]
command = "/usr/local/bin/qwebbridge-mcp-proxy"
enabled = true
startup_timeout_sec = 10
tool_timeout_sec = 60
```

Prefer editing the TOML directly or verifying generated CLI output. `grok mcp add ... --args ''` can create `args = [""]`, which passes an empty argument to the proxy. Remove that line for the clean stdio proxy config.

3. Install the user-level Grok skill so Grok receives operating instructions:

```bash
mkdir -p ~/.grok/skills
rm -rf ~/.grok/skills/qweb-bridge
cp -a ~/.hermes/skills/qweb-bridge ~/.grok/skills/qweb-bridge
```

If the active Hermes skill path differs because the skill is category-scoped, copy the resolved skill directory that contains `SKILL.md`.

4. Verify MCP handshake and tool discovery:

```bash
grok mcp doctor qwebbridge
```

Expected healthy result: command found, server started, handshake OK, tools discovered.

5. In an existing Grok TUI session, refresh with `/mcps` then `r`. New Grok sessions load the server automatically.

## Rationale

Use `/usr/local/bin/qwebbridge-mcp-proxy` rather than `qweb-bridge mcp` when the persistent user-level QWebBridge daemon is active. The proxy reuses the running daemon on port 10086; starting another daemon can cause a port conflict.
