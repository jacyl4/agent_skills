# Dexto / Witsy / Pi / GSD 清理

按用户最新要求移除 Dexto、Witsy、Pi、GSD；**Universal 保持可见**，没有注册、移除或修改它的 Target 配置，`~/.agents/skills` 及共享规则完整保留。

## 活动路径变更

- Dexto、Witsy：未发现包、命令、专属配置/缓存、服务或桌面入口；原先只是共享技能目录导致的误识别，无虚构卸载。
- Pi：没有安装独立 `pi` 命令；仅有 `~/.pi/agent/AGENTS.md`（通用 ParaSpeech 说明），将整个旧 `~/.pi` 隔离，未删除 ParaSpeech 服务或共享说明。
- GSD：通过 npm 精确卸载全局 `@opengsd/gsd-pi@1.22.0`，四个入口 `gsd`、`gsd-cli`、`gsd-mcp-server`、`gsd-pi` 一并移除；`~/.gsd` 用户数据、会话和凭据整体进入私有隔离备份。没有运行中的 GSD/Pi 进程或待清理服务。
- 同时移除 npm allow-scripts 中仅属于 GSD 的 `@opengsd/gsd-pi`、`@opengsd/gsd-browser` 两项，其他脚本白名单不变；原 npmrc 私有备份已保留。
- 不执行 npm 全局 prune、APT autoremove 或缓存大扫除；不触碰其他项目内的 `.gsd` 工作记录。
- 共享 Source 的 `create-gsd-extension` 等普通技能文档不是应用安装文件，保持原状；未因关键字删除其他 Agent 的文件。

## Targets 显示

复用现有 UI `0.25.13+fwd2`，没有改源码或重新构建：

```ini
Environment=SKILLSHARE_UI_HIDE_TARGETS=warp,antigravity,gemini,dexto,witsy,pi
```

以上项从发现列表、Add Target 和 available-target API 中排除。Universal 不在隐藏名单中，仍可按需配置；共享目录不能为了清理误识别而删除。保留用户当前的全部注册 Target（包括本轮用户新增的 Universal），安全策略不变。

## 验证

- 真实 HTTPS 反代浏览器验证 Targets / Add Target：旧项消失，Universal 存在，antigravity-cli 保留。
- npm 全局清单前后逐项比较：仅移除 `@opengsd/gsd-pi`，其他顶层包的版本和路径不变；GSD 四个命令以及 Pi/Dexto/Witsy 均不存在。
- 85 份 Source/原生配置 SHA 和 agy、共享规则等额外文件摘要一致。
- MCP 3、Hooks 8、Plugins 9 的页面/API与只读预演正常；11 个安全拒绝用例仍通过。
- 本次没有源码变更，不重复运行完整源码构建/测试；不声称执行了所有其他 CLI 的交互式启动测试。

## 私有备份与回退

路径见仓库忽略的 `.omx/plans/unused-agents-backup-path`，对应
`~/.local/state/skillshare-onboarding/unused-agents-cleanup-<timestamp>/`（0700）。

- `gsd-pi-package/`：卸载前完整 npm 包及依赖的回退副本，不在活动 npm 路径。
- `quarantine/`、`quarantine-map.json`：旧 Pi/GSD 用户目录原样隔离；可能含凭据，禁止公开。
- `npm-bin-links.json`：四个原入口的精确符号链接目标。
- `dropin-before.conf`、`logs/`：原服务配置、npm 清单、校验和浏览器证据。
- `verification-tools/`：只从卸载包中复制的 Playwright 浏览器验收依赖，供本轮测试使用；不是重新安装 GSD，不加入 PATH。

回退前核对后续修改与路径冲突。可恢复精确包目录及四个链接，再逐项恢复隔离用户目录；或者按正常维护流程重新安装固定包版本后恢复用户数据。恢复单一 drop-in 后执行 user daemon-reload/restart 并验证。不要恢复整套 npm、覆盖所有 Agent 目录或删除全局备份。

本次替代先前“保留 GSD/Pi”的讨论结论；此前清理记录作为历史保留，不代表当前仍安装。
