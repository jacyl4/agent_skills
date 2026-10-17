# MCP-Chrome full uninstall checklist

Use when the user wants MCP-Chrome removed completely from local AI/agent tooling.

## Scope

Remove all of the following if present:

- Source/build tree: `/opt/ai/mcp-chrome`
- Shared config dir: `/etc/mcp-chrome`
- Global npm package/artifacts:
  - npm package `mcp-chrome-bridge`
  - `/usr/local/lib/node_modules/mcp-chrome-bridge`
  - `/usr/local/bin/mcp-chrome-bridge`
  - `/usr/local/bin/mcp-chrome-stdio`
  - `/usr/local/bin/mcp-chrome-cli`
  - `/usr/local/bin/chrome-mcp-bridge`
- Chrome Native Messaging manifests:
  - `~/.config/google-chrome/NativeMessagingHosts/com.chromemcp.nativehost.json`
  - `/root/.config/google-chrome/NativeMessagingHosts/com.chromemcp.nativehost.json`
  - `/etc/opt/chrome/native-messaging-hosts/com.chromemcp.nativehost.json`
  - `/etc/chromium/native-messaging-hosts/com.chromemcp.nativehost.json`
- Chrome profile data for extension id `hbdgbgagpkpjffpklnamcljpakneikee` under `~/.config/google-chrome/**/`.
- Agent config/instruction surfaces under active user, `/root`, and `/etc/skel`:
  - `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`
  - `.mcp.json`, `.claude/mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json`, `.openclaw/mcp.json`, `.config/Code/User/mcp.json`
  - `.opencode/opencode.json`
  - `.codex/config.toml`
  - `.github/copilot-instructions.md`
  - `.cursor/rules/mcp-chrome.mdc`
  - `.kiro/steering/mcp-chrome.md`
  - `.hermes/config.yaml` entries under `mcp_servers.chrome_mcp_stdio`

## Removal pattern

1. Remove npm/global binaries first:

```bash
npm uninstall -g mcp-chrome-bridge || true
sudo rm -f /usr/local/bin/mcp-chrome-bridge \
  /usr/local/bin/mcp-chrome-stdio \
  /usr/local/bin/mcp-chrome-cli \
  /usr/local/bin/chrome-mcp-bridge
sudo rm -rf /usr/local/lib/node_modules/mcp-chrome-bridge
```

2. Remove source/config/native host:

```bash
sudo rm -rf /opt/ai/mcp-chrome /etc/mcp-chrome
rm -f ~/.config/google-chrome/NativeMessagingHosts/com.chromemcp.nativehost.json
sudo rm -f /root/.config/google-chrome/NativeMessagingHosts/com.chromemcp.nativehost.json \
  /etc/opt/chrome/native-messaging-hosts/com.chromemcp.nativehost.json \
  /etc/chromium/native-messaging-hosts/com.chromemcp.nativehost.json
```

3. Remove the extension profile id if present:

```bash
find ~/.config/google-chrome -path '*hbdgbgagpkpjffpklnamcljpakneikee*' -print -exec rm -rf {} +
```

4. Clean agent surfaces with structured edits, not blind whole-file deletion:

- Remove marker blocks bounded by `<!-- MCP_CHROME DEFAULT START -->` and `<!-- MCP_CHROME DEFAULT END -->`.
- Remove JSON keys whose names or values contain `mcp-chrome`, `chrome-mcp`, or `chrome_mcp_stdio`.
- Remove TOML sections such as `[mcp_servers.chrome-mcp-stdio]`.
- Remove YAML `mcp_servers.chrome_mcp_stdio`.

## Verification

```bash
for p in /opt/ai/mcp-chrome /etc/mcp-chrome \
  /usr/local/bin/mcp-chrome-bridge /usr/local/bin/mcp-chrome-stdio \
  /usr/local/bin/mcp-chrome-cli /usr/local/bin/chrome-mcp-bridge \
  /usr/local/lib/node_modules/mcp-chrome-bridge \
  ~/.config/google-chrome/NativeMessagingHosts/com.chromemcp.nativehost.json; do
  [ -e "$p" ] || [ -L "$p" ] && echo "STILL_EXISTS $p" || echo "absent $p"
done
npm list -g --depth=0 2>/dev/null | grep -i 'mcp-chrome' || echo 'npm package absent'
hermes mcp list
```

Expected result: all checked paths absent, npm package absent, and `hermes mcp list` has no `chrome_mcp_stdio` entry.
