# Warp 智能终端清理与 Targets 隐藏

> 后续变更：Pi/GSD 已按用户要求移除，Dexto/Witsy/Pi 候选已隐藏；Universal 保持可见。当前状态与回退见 [本轮清理](unused-agents-cleanup.md)。

本次对象是 Warp 智能终端，不是 Cloudflare WARP。

## 根因与范围

本机未发现 Warp 包、可执行文件、进程、systemd 服务、专属配置/缓存目录或桌面启动器；全局 Skillshare 配置也没有注册 Warp。无需删除不存在的应用文件。

上游 v0.25.13 的 Warp 默认技能目录是共享的 `~/.agents/skills`。该目录被 Codex、Zed 等实际工具使用，因此 Skillshare 误把 Warp 识别为 “Found on machine”。**不能删除共享目录来消除这一显示。**

本机 UI fork 增加可选环境变量：

```ini
Environment=SKILLSHARE_UI_HIDE_TARGETS=warp
```

它从 available-target API 中按精确名称排除 Warp，影响 Targets 的自动发现、“Add Target”候选和这些候选的 readBy 展示；不改已有注册 Target、官方 CLI、技能 Source、原生配置或适配器。默认未配置时保留上游目录。不是卸载器、安全权限控制或对上游适配器代码的删除；其他模块的静态“支持客户端”目录不表示安装状态。

## 当前部署

后续按用户要求同时排除了旧 Antigravity IDE、Gemini CLI；当前环境变量为 `warp,antigravity,gemini`，保留 `antigravity-cli`，见 [旧 Google 入口清理](legacy-google-cleanup.md)。

UI 独立版本为 `0.25.13+fwd2`，位于 `/opt/ai/skillshare/ui-releases/0.25.13+fwd2/`。官方 CLI 仍为 v0.25.13，域名白名单、Nginx、TLS、ACL 和 nft 规则保持原状。

服务继续使用 `~/.config/systemd/user/skillshare.service.d/domain-allowlist.conf`，仅切换 UI artifact 并增加上述环境变量。前端代码不变，资源缓存复制至同版本目录。生命周期仍由 user systemd 管理。

重建需在固定上游 commit `a7adb69e527c9f48eff154dce0b01c233da53004` 上依次应用：
1. `tooling/patches/skillshare-v0.25.13-trusted-origin.patch`
2. `tooling/patches/skillshare-v0.25.13-hide-warp-target.patch`

后者基于前者，不能颠倒顺序。隔离容器构建时设置 `main.version=0.25.13+fwd2`；与匹配缓存一起部署。版本目录含两份 patch 和 build manifest，可校验二进制 SHA。

## 验证与回退

验收包括 global/project 隐藏回归、默认行为与精确匹配、原域名守卫测试、Go vet、真实 HTTPS Targets/Add Target 浏览器和 MCP/Hooks/Plugins 及负向域名用例。没有改动或掩盖既有 OfficeCLI 嵌套重复导致的完整仓库测试失败，未运行完整上游套件。

本轮私有备份与日志：
`~/.local/state/skillshare-onboarding/warp-cleanup-20261017-225607/`。
保留完整源码、变更前 drop-in/config、文件 SHA、测试和浏览器证据。

回退前检查并保存后续修改；将本轮 `dropin-before.conf` 恢复到上述单一 drop-in，执行：

```sh
systemctl --user daemon-reload
systemctl --user restart skillshare.service
```

这会回到 `+fwd1` 并保留域名白名单，但 Warp 候选会重新出现。无需改 Nginx、防火墙或恢复技能目录。新旧 artifact/缓存保留供审计，不进行全局清理。
