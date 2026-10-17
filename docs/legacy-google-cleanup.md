# 旧 Antigravity IDE / Gemini CLI 清理

> 后续变更：Pi/GSD 已按用户要求移除，Dexto/Witsy/Pi 候选已隐藏；Universal 保持可见。当前状态与回退见 [本轮清理](unused-agents-cleanup.md)。

保留官方 Antigravity CLI：`agy` v1.4.0 和 Skillshare 的 `antigravity-cli` Target。没有将 Google Gemini 产品本身称为停用；本次只移除这台机器上不再使用的旧入口。

## 清理结果

没有发现已安装的 Antigravity 桌面版或 Gemini CLI 包、独立程序、进程、服务或桌面启动器。以下专属残留已移出活动路径，放入私有可回退隔离区：

- `/usr/local/bin/gemini-rtk`：调用不存在的 Gemini CLI 的旧启动器。
- `~/.gemini/hooks/`：只有孤立的 `.rtk-hook.sha256`，没有 hook 脚本或活动配置引用。
- `~/.config/skillshare/extensions/gemini-commands/`：Gemini CLI TOML 命令转换器；没有活动配置引用，`agy plugin list --json` 返回空列表，不是已安装的 agy 插件。
- `~/.cache/antigravity/`：仅有空 staging 子目录。

RTK 源码中的支持适配器、技能中的通用 Gemini 文档、个人 Typora 草稿和历史备份不是应用残留，不做全盘关键字删除。

## 必须保留的共享目录

`~/.gemini/` 不等于 Gemini CLI 私有数据，不能整目录删除。

本轮保留整个 `~/.gemini/antigravity-cli/`、`~/.gemini/config/`、所有共享技能与原生配置、`agy` 可执行文件和 shell 加载块。即使 `config/mcp_config.json` 当前为空，它仍是官方支持的 CLI 全局 MCP 路径；`config/projects/` 也用于 CLI 项目配置。

官方依据：[MCP](https://antigravity.google/docs/mcp)、[CLI 变更说明](https://antigravity.google/docs/changelog?tab=cli)、[迁移兼容说明](https://antigravity.google/docs/cli/gcli-migration)。

## Skillshare 可见性

继续使用 UI `0.25.13+fwd2`，没有重新构建。现有 user service drop-in 只把环境变量改为：

```ini
Environment=SKILLSHARE_UI_HIDE_TARGETS=warp,antigravity,gemini
```

旧项目从 Targets 的发现区、新增候选及 available-target API 中排除；`antigravity-cli` 保留在 7 个真实注册 Target 中。原有域名守卫、Nginx、TLS、网络 ACL 和官方 CLI 未改。底层静态支持适配器仍保留，不代表本机安装了对应程序。

## 验证与回退

- 真实 HTTPS 反代浏览器验收 Targets 和 Add Target；旧三项不存在，`antigravity-cli` 保留。
- agy 版本与插件清单只读 smoke；保留配置、技能及原生文件 SHA 验证。
- MCP 3、Hooks 8、Plugins 9 的网页/API与只读预演；11 个既有安全拒绝用例。
- 本轮是部署配置与文件隔离，没有产品源码变更；未重复运行完整上游/仓库测试，也没有执行 AI 请求或重新登录。

私有备份路径记录于 `.omx/plans/legacy-google-backup-path`。其中 `quarantine-map.json` 是精确原路径到隔离路径映射，`dropin-before.conf` 为变更前单一 drop-in，`logs/` 保存校验与浏览器证据。

如需回退，先核对后续改动，确认原路径不存在，再按映射逐项恢复；root-owned 启动器用 sudo 恢复并保留原权限。恢复单一 drop-in 后执行 user `daemon-reload`、`restart skillshare.service`。不要覆盖整个 `~/.gemini`、恢复整套 systemd 或删除其他备份。隔离区不再属于活动安装；它含私有项目数据时不得公开。
