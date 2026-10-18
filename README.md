# Agent Skills 主源

本仓库的 `skills/` 是自维护 Skills 的唯一内容主源；仓库根仅负责 Git 和工程维护。GitLab 管版本，Skillshare 管本机发现、展示和分发；不要再在各 Agent 目录中维护独立副本。

当前主源为 **126项不重名技能**：原有68项，加上本轮从各Agent本地归集的58项。已消除OfficeCLI的11份嵌套重复；正文与附件按来源校验。详见[归集记录](docs/skill-collection.md)。

| 分类 | 内容 | 数量 |
|---|---|---:|
| automation | 本机工具、浏览器、技能与工作流 | 13 |
| data | Honker / SQLite 事件引擎 | 1 |
| documents | OfficeCLI、Morph 与文档专项 | 11 |
| engineering | 规划、开发、测试、审查与维护 | 38 |
| frontend | 设计、质量、React、GSAP | 28 |
| platforms | Cloudflare、Hermes 专项 | 32 |
| writing | 中文写作、文档、Hermes SOUL 维护 | 3 |

当前管理入口：**https://fwd.seso.icu:34000/**（内网/VPN，域名需内网解析到网关，systemd持久运行）。[反代与服务运维](docs/skillshare-resident-proxy.md)。

## 目录结构

```text
agent_skills/
├── skills/                  # Skillshare 唯一 Source
│   ├── automation/
│   ├── data/
│   ├── documents/
│   ├── engineering/
│   ├── frontend/
│   ├── platforms/
│   ├── writing/
│   ├── .skillignore         # 技能启停规则
│   ├── .metadata.json       # Skillshare 原生 GitHub 来源与版本
│   └── .license-manifest.json # 已核实版权声明的完整性清单
├── tooling/
│   ├── scripts/             # 校验与受保护同步入口
│   └── tests/               # test_sync_skills.py / test_validate_skills.py
├── docs/                    # 维护文档与迁移记录
├── README.md
└── .gitignore
```

Git 根不变；Skillshare 和 Hermes 仅扫描 `skills/`，不会把 `tooling/` 或 `docs/` 当成技能。`.omx/` 等忽略的运行状态不属于内容目录，保留原有状态，不参与分发。

## 维护约定

- 每项放在 `skills/<分类>/[子分类/]<技能名>/SKILL.md`，叶目录名与 frontmatter `name` 一致，名称全局唯一。
- Skillshare 使用 **merge + standard**：目标目录用 `name`，分类目录不会改变 Agent 调用名。
- Skillshare 清单/UI 中的内部 ID 仍按源路径展平，管理命令不要把内部 ID 与调用名混用。
- 修改已有内容可经链接即时可见；新增、删除、移动、启停或筛选变化后需要重新同步。Agent 是否热加载独立验证，优先新会话。
- 保留来源标记、许可证和有效附件；不因技能相似就合并，兼容旧版有独立用途时保留。许可证缺失/变化会阻止保护同步；见[声明保留记录](docs/third-party-notices.md)。
- 系统、OMX、插件及 Hermes 自带/WebUI/Hub 托管技能仍由原安装渠道负责，见归集例外。GSD/Pi运行时已按要求移除，普通技能文档保留。
- 安装、编辑、移动、启停都会影响主源；先检查 Git 差异。不要使用 Dashboard 的 Git 自动提交、强制拉取或丢弃更改。

## 验证与同步

需要 Python + PyYAML。此次部署使用已有的 Hermes Python 环境，没有新增 Python 依赖。

```bash
PYTHON=/home/jacyl4/.hermes/hermes-agent/.venv/bin/python
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -m unittest discover -s tooling/tests
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" tooling/scripts/validate_skills.py
# 默认只预演：校验源、命名、重叠和目标同名冲突
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" tooling/scripts/sync_skills.py
# 审核预演后才应用
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" tooling/scripts/sync_skills.py --apply
```

两个脚本默认固定使用本仓库 `skills/`，不依赖调用时的工作目录；校验器仍支持显式传入测试源路径。

此脚本是本仓库的保守保护入口，不是 Skillshare 的替代实现。它会连当前已过滤名称也一起检查；不自动解决冲突，不支持 `--force`。GUI 和直接调用原生 `sync` 不经过这层检查。

- [本机部署、维护、升级、回滚与排障](docs/skillshare-operations.md)
- [Warp 智能终端清理、Targets 隐藏与回退](docs/warp-cleanup.md)
- [旧 Antigravity IDE / Gemini CLI 清理与保留边界](docs/legacy-google-cleanup.md)
- [Dexto / Witsy / Pi / GSD 清理与 Universal 保留](docs/unused-agents-cleanup.md)
- [日志、原生审计和共享写入修复](docs/audit-review.md)
- [部署验收与已知缺口](docs/deployment-2026-10-17.md)
- [分类迁移和来源记录](docs/layout-migration.json)

- [独立 Source 布局迁移与回退](docs/source-layout-2026-10-17.md)

## GitHub 上游与升级

已为55项技能关联6个GitHub上游，支持Skillshare原生来源展示、检查与单项更新；原13项与本轮新增58项先保留本地管理；不猜测远程来源。**本轮未升级内容。普通技能升级会覆盖本地修改，不会自动合并。** 先备份并单项审核，不批量更新。

- [来源关联、例外项和升级流程](docs/upstream-updates.md)
- [逐项来源与本地适配证据](docs/upstream-sources.json)

## MCP、Hooks 与 Plugins

MCP 现交由 **Magpie** 管理，Skillshare 已撤销原3个定义、4个绑定的纳管，保留 Agent 原生配置不动。Skillshare 继续管理8组Codex/Cursor hooks和9个现有Codex插件。结构化主源位于本机 `~/.config/skillshare/config.yaml`，不进入本Git仓库或 `skills/`。鉴权、原生信任和工具自管扩展仍归原渠道。

[纳管范围、网页安全入口、维护与回退](docs/resource-management.md)。现有域名已追加精确白名单，三项可直接访问；见[域名白名单与维护说明](docs/domain-allowlist.md)。未配置的其他域名及跨站请求仍拒绝。

**当前验收**：50项工具测试通过，8个Target保留；Universal/agy/Hermes直接同步，其他5项经Universal共享读取（网页Skills off仅关闭重复写入）。安全审计仍有CRITICAL/HIGH告警，不等同安全全绿，见[归集与风险记录](docs/skill-collection.md)。
