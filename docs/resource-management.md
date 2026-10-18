# MCP、Hooks、Plugins 纳管（2026-10-17）

> **当前职责调整（2026-10-18）：MCP 已交由 Magpie 管理。** Skillshare 对 context7、crawl4ai、qwebbridge 使用 `mcp remove --keep-files` 撤销纳管，并清除 4 条绑定的所有权记录；Agent 原生配置内容及权限不变。现有 Hooks、Plugins 和技能管理保持。以下 MCP 导入／同步记录属于历史部署说明，不再是当前操作流程；不要重新导入 MCP 或用 Skillshare 覆盖 Magpie 的配置。
>
> 当前验证：MCP 受管定义 0、所有权条目 0、`skillshare sync mcp -g --dry-run --json` 变更 0。网页仍可能发现原生 MCP 并显示为 unmanaged，不代表重新接管。备份及验证证据由 `.omx/plans/mcp-handoff-backup-path` 指向；回退前需协调 Magpie，不能直接恢复旧所有权和配置覆盖其后续修改。

> 后续界面适配：Sync 页默认不勾选 MCP，刷新后仍排除；真实点击 Sync 已确认不发送 MCP 写入请求。此项为前端默认值，不是禁止用户以后手动勾选的服务端策略。源码补丁为 `tooling/patches/skillshare-v0.25.13-sync-mcp-default-off.patch`；当前生产缓存和回退证据由 `.omx/plans/sync-repair-backup-path` 指向。

## 已完成的实际管理范围

配置源：**`~/.config/skillshare/config.yaml`**（0600）。MCP、hooks、plugins 是结构化主机配置，不是 `SKILL.md`，不放进 `skills/` 或本 Git 仓库。Skillshare 程序仍为固定 v0.25.13。

| 类型 | 已纳管 | 原生接收方 |
|---|---|---|
| MCP | context7、crawl4ai、qwebbridge，共3个定义、4个绑定 | Codex三项；Grok仅qwebbridge |
| Hooks | 8组原有事件 | Codex：PostCompact、PostToolUse、PreCompact、PreToolUse、SessionStart、Stop、UserPromptSubmit；Cursor：sessionStart |
| Plugins | 9个已有原生安装 | Codex，保留原marketplace、版本、enabled与scope |

九个插件：gmail、github、app-6a314a73f8ac819195b0d55e36b9c609、app-69ef18c674308191a2f952431f91ea61、finances、openai-templates、sites、plugin-management、work-pets，均来自既有 `openai-curated-remote`。

这是**原地认领已有配置/注册**，不是重新安装。没有新增MCP服务器、跨Agent推广资源、执行hook、调用MCP工具、执行插件安装脚本或升级插件。没有复制OAuth会话或重置native授权。

## 哪些原生设置保持不动

- Codex `~/.codex/config.toml`、`hooks.json` 和 Cursor `hooks.json` 的文件字节及权限与本轮备份一致。
- Codex qwebbridge 的10项 `tools.*.approval_mode=approve` 原样保留；Grok qwebbridge 的启动/工具超时字段原样保留。
- 仅将公共qwebbridge command归为一个定义，绑定Codex/Grok；客户端独有字段仍由各自native配置承载。今后命令/URL/env若分化，不可强行合并同名定义。
- OMX 的内联 `[hooks.state]`、信任数据、hook脚本、matcher、timeout、顺序、重复次数保持；内联hooks并未转移所有权，仍显示unmanaged是正常边界。
- 账号鉴权、工具审批、hook trust仍由Agent处理。纳管不意味着Skillshare能替人批准信任。
- Codex插件原生ID、版本、启用状态与scope逐项前后一致。未做插件sync/install/update/enable/disable操作。
- 技能源与分发targets没有改变，两个Target各68条原有受管链接仍有效。

OMX与Herdr仍维护它们生成的hook命令/脚本；Skillshare登记当前部署版本并管理同步。上游工具更新hook后，先检查冲突、审阅并重新import认领新版本，不用旧Source强制覆盖上游生成结果。

## 保留原管理渠道的部分

- **Hermes MCP**：Skillshare v0.25.13 MCP adapter不支持Hermes。其qwebbridge、crawl4ai、hermes-studio-use仍由Hermes配置读取；scrapling、hermes-studio-api/devices/browser等禁用项继续禁用，未搬动或开启。
- **Hermes plugin**：herdr-agent-state仍为Hermes原生插件；当前Skillshare只声明Hermes discovery-only，不伪装已可写管理。
- **GSD**：`~/.gsd/agent/extensions` 的20个工具自管扩展（含mcp-client等）不等于Pi marketplace插件；没有改包管理器、加载路径或迁移到旧 `.pi` 目录。
- **Cursor IDE软件扩展**、未安装Agent、空MCP配置、插件内建MCP均不凭名称创建、合并或接管。
- MCP可执行程序、stdio代理、systemd服务仍由原安装/服务渠道维护。Skillshare管理连接配置，不管理服务驻留或二进制升级。
- 导入的Codex插件没有审核过的Git源码快照；原生marketplace/账号仍是版本与权限来源。不要把它们当成GitHub技能那样安全地逐项源码更新；marketplace更新可能影响多个插件，先由原生管理器审阅。

## 使用入口

```bash
skillshare mcp list -g --json
skillshare mcp check -g --no-dns --json    # 静态检查，不启动/调用服务器
skillshare sync mcp -g --dry-run --json
skillshare hooks list -g --json
skillshare hooks sync -g --dry-run --json
skillshare plugin list -g --json
skillshare plugin inspect github -g --json
```

真正同步MCP或hooks前，先审查dry-run的具体路径与动作；使用预演返回的revision提交，例如：

```bash
skillshare sync mcp -g --revision <预演revision> --json
skillshare hooks sync -g --revision <预演revision> --json
```

`revision`变化意味着源或原生状态变化，重新预演，不绕过。遇到conflict/blocked停止并核对native归属；不使用 `--replace` 强接管。

普通 `tooling/scripts/sync_skills.py` 仍准确调用 `skillshare sync -g [--dry-run]`，**只同步skills**。新增两项回归测试锁定此行为；没有改成不存在的 `sync skills`。`sync --all`包含MCP/hooks但不包含plugins，本部署不使用它作为无审查的一键发布入口。

不要为“验证”执行 `mcp check --live`、hook命令、插件安装器或批量更新。静态检查成功仅证明配置可表达/本地命令存在，不等于远端账号认证与所有工具调用均成功。

## 网页管理与原有网络边界

**当前已按后续要求增加 `fwd.seso.icu:34000` 精确白名单**：MCP/Hooks/Plugins可通过现有域名直接访问，见[专用UI补丁与安全边界](domain-allowlist.md)。白名单仅限实际网关和同源HTTPS请求；原ACL/nft不变，没有伪造localhost或Origin。

以下SSH转发保留为原生备用入口，不再是当前域名访问这三页的前提。

如需备用localhost入口，可在**运行浏览器的本机**建立经过认证的SSH本地转发：

```bash
ssh -N -p 14082 -o IdentitiesOnly=yes -o ExitOnForwardFailure=yes \
  -i /home/jacyl4/1base/@secure/id_rsa \
  -L 127.0.0.1:19422:10.0.0.186:34000 root@10.0.0.2
```

随后访问 `http://127.0.0.1:19422/mcp`、`/hooks`、`/plugins`。这个localhost是运行上述SSH命令那台机器，不是任意设备的localhost；不要绑定 `0.0.0.0`。不需要时结束SSH进程。本轮已临时验证三页及API全部200、无页面JS错误，测试隧道已关闭，没有新增持久化隧道服务。

## 验收与既有问题

- MCP静态check：0 errors / 0 warnings。
- MCP/hooks scoped同步后，第二次预演全部unchanged，无冲突；native配置/脚本字节和权限保持。
- 14项同步保护测试通过（原12项+新增2项），新增测试证明有MCP/hooks/plugins配置时仍只同步skills。
- **完整仓库测试不是全绿**：本轮施工前30 tests已有56个失败条目；施工后32 tests保持同样56个失败条目，新增失败0。现有OfficeCLI目录包含11份嵌套重复SKILL.md，以及此前升级后的元数据与旧回归断言不匹配；本轮未改动、隐藏或放宽这些检查。
- 当前源实际79个SKILL.md，其中11个为上述嵌套重复；不宣称源仍是无重复的68项。原有136条分发链接均存在，但去重修复应另行审阅后施工。
- 九个插件的原生注册/版本/开启状态已前后比较；没有取得插件缓存树的**导入前**完整hash基线，故不宣称缓存每字节前后一致。导入后已保存348个缓存文件的hash/stat基线用于后续比对。
- user systemd服务与既有代理保持；不保证已运行的所有Agent会话即时重载，按各工具原生方式刷新/新开会话。

## 备份与精准回退

外置备份：`/home/jacyl4/.local/state/skillshare-onboarding/resources-20261017-182530`（根目录0700）。

- `skillshare-before/`：本轮前全局配置目录；`native-before/`：原生配置及hook脚本（不公开、不提交）。
- `logs/*-preview-current.json`、`*-applied.json`、`adoption-summary.json`：逐项revision与纳管证据。
- `logs/*-sync-second-preview.json`：同步幂等；`mcp-check.json`：静态检查。
- `logs/plugins-before.json` / `plugins-after.json`：原生插件状态；`plugin-cache-post-adoption-baseline.json`：明确为导入后缓存基线。
- `logs/tests-before.txt` / `tests-after.txt`：既有失败对比；`ui-resource-verification.json`：临时安全隧道网页验证。

撤销纳管优先用原生命令停止管理但保留现有文件：MCP `mcp remove <name> --keep-files`、hooks `hooks remove <name> --keep-files`，先逐项预演。插件 `remove` 会卸载，**不得拿来撤销本轮import**；若要取消插件登记，先停UI与其他写入，另存当前全局配置/Skillshare状态，对照本轮新增package与binding精确恢复，或在确认本轮后无其他资源更改时恢复对应备份。不要整体恢复旧native配置覆盖后续编辑，不恢复旧 `.git`，不删除Agent目录或插件cache。

原生Agent文件本轮未改，无须恢复它们来撤销登记。ownership/manifest状态也要按准确资源恢复，未核清前不要sync。回退后重跑只读预演、native配置比较，再启动既有UI服务。

官方依据：[MCP](https://skillshare.runkids.cc/docs/how-to/daily-tasks/sharing-mcp/)、[Plugins](https://skillshare.runkids.cc/docs/how-to/daily-tasks/sharing-plugins/)、[固定版Hooks实现](https://github.com/runkids/skillshare/tree/v0.25.13/internal/hooks)。
