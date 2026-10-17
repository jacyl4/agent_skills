# MCP-Chrome default deployment

Use this when deploying MCP-Chrome as the default browser-control MCP server for Hermes and other AI/agent tools.

## Durable layout

- Source repo: `/opt/ai/mcp-chrome`
- Chrome unpacked extension: `/opt/ai/mcp-chrome/app`
- npm package: `mcp-chrome-bridge`
- Stdio MCP entrypoint: `/usr/local/bin/mcp-chrome-bridge` -> npm package `dist/mcp/mcp-server-stdio.js`
- Optional explicit stdio alias: `/usr/local/bin/mcp-chrome-stdio`
- Optional CLI alias: `/usr/local/bin/mcp-chrome-cli` -> npm package `dist/cli.js`
- HTTP endpoint after extension connects: `http://127.0.0.1:12306/mcp`

## Install/update

```bash
sudo apt-get update
sudo apt-get install -y nodejs npm git
sudo mkdir -p /opt/ai
if [ -d /opt/ai/mcp-chrome/.git ]; then
  sudo git -C /opt/ai/mcp-chrome pull --ff-only
else
  sudo git clone https://github.com/hangwin/mcp-chrome.git /opt/ai/mcp-chrome
fi
sudo npm install -g mcp-chrome-bridge
BRIDGE="$(npm root -g)/mcp-chrome-bridge/dist/mcp/mcp-server-stdio.js"
CLI="$(npm root -g)/mcp-chrome-bridge/dist/cli.js"
sudo ln -sf "$BRIDGE" /usr/local/bin/mcp-chrome-bridge
sudo ln -sf "$BRIDGE" /usr/local/bin/mcp-chrome-stdio
sudo ln -sf "$CLI" /usr/local/bin/mcp-chrome-cli
```

## Register Chrome native host

`mcp-chrome-bridge` is the package CLI, but this deployment may reserve `/usr/local/bin/mcp-chrome-bridge` for stdio MCP. Use the CLI alias or the package-provided `chrome-mcp-bridge` command:

```bash
chrome-mcp-bridge register
chrome-mcp-bridge doctor --json
```

A healthy pre-extension state usually has `ok=true` with warnings for connectivity/logs. The user must load `/opt/ai/mcp-chrome/app` as an unpacked Chrome extension and click Connect before HTTP connectivity is fully green.

## Hermes config

Add to `~/.hermes/config.yaml` (and root/skel if deploying defaults for all local agents):

```yaml
mcp_servers:
  chrome_mcp_stdio:
    command: node
    args:
      - /usr/local/bin/mcp-chrome-bridge
    timeout: 120
    connect_timeout: 60
```

Verify:

```bash
hermes mcp list
hermes config check
```

## Cross-agent default surfaces

For broad local default deployment, add marker-bounded instructions to each home (`$HOME`, `/root`, `/etc/skel`) in common agent files:

- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`
- `.opencode/AGENTS.md`, `.agents/AGENTS.md`, `.openclaw/AGENTS.md`
- `.cursor/rules/mcp-chrome.mdc`
- `.github/copilot-instructions.md`
- `.kiro/steering/mcp-chrome.md`

Recommended marker block:

```md
<!-- MCP_CHROME DEFAULT START -->
MCP-Chrome is installed at /opt/ai/mcp-chrome. Its Chrome extension lives at /opt/ai/mcp-chrome/app and the native bridge listens on http://127.0.0.1:12306/mcp after the extension connects.
For browser-control tasks, prefer the configured MCP server named chrome-mcp-stdio / chrome-mcp-server before ad-hoc browser automation when the agent supports MCP. Stdio config: command `node`, args [`/usr/local/bin/mcp-chrome-bridge`]. HTTP config: `http://127.0.0.1:12306/mcp`.
If MCP-Chrome tools are unavailable, open Chrome/Chromium, load the unpacked extension from /opt/ai/mcp-chrome/app, click Connect in the extension, then retry.
<!-- MCP_CHROME DEFAULT END -->
```

Also write MCP config files where supported:

```json
{
  "mcpServers": {
    "chrome-mcp-stdio": {
      "command": "node",
      "args": ["/usr/local/bin/mcp-chrome-bridge"]
    }
  }
}
```

Common paths: `.mcp.json`, `.claude/mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json`, `.openclaw/mcp.json`, `.config/Code/User/mcp.json`.

For Codex CLI, add to `.codex/config.toml`:

```toml
[mcp_servers.chrome-mcp-stdio]
command = "node"
args = ["/usr/local/bin/mcp-chrome-bridge"]
```

For OpenCode, preserve existing config and add both common shapes if unsure:

```json
{
  "mcp": {
    "chrome-mcp-stdio": {
      "type": "local",
      "command": ["node", "/usr/local/bin/mcp-chrome-bridge"],
      "enabled": true
    }
  },
  "mcpServers": {
    "chrome-mcp-stdio": {
      "command": "node",
      "args": ["/usr/local/bin/mcp-chrome-bridge"]
    }
  }
}
```

## Pitfalls

- Do not confuse the package CLI with the stdio MCP script. If `/usr/local/bin/mcp-chrome-bridge` is symlinked to `mcp-server-stdio.js`, run registration/doctor via `chrome-mcp-bridge` or a separate CLI alias.
- `chrome-mcp-bridge doctor --json` can be green enough while connectivity is warn; the extension must be loaded and connected for the HTTP endpoint.
- Root-owned `/opt/ai/mcp-chrome` may trigger Git dubious ownership for non-root verification. Add `safe.directory` for users who need to inspect the repo with git.
- Restart Hermes/gateway after MCP config changes. Existing sessions keep their startup tool registry.