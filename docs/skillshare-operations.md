# Skillshare 本机运维

> 最新运维基线：[日志/审计与共享写入修复](audit-review.md)。保留8项登记，仅Universal/agy/Hermes直接写技能，其他5项经Universal共享读取。

> 当前追加状态：GSD/Pi 已卸载清理，Universal 保持可见，见 [清理记录](unused-agents-cleanup.md)。下文迁移过程涉及 GSD/Pi 的描述为历史状态。

读者：维护本机 Skills 的用户和后续 Agent。目标：安全更新主源、分发变化，遇到异常时按清单恢复，不破坏其他工具的技能。

## 安装与管理边界

- 固定版本：v0.25.13；Linux amd64 Release 包已对照官方 checksums 校验。
- 程序：`/opt/ai/skillshare/releases/0.25.13/skillshare`。
- 当前版本：`/opt/ai/skillshare/current`；命令入口：`/usr/local/bin/skillshare`。
- 二进制 SHA256：`54bdad8c3defc8604fc5e10c9f0a4c5b8c8cfc20834d13efd1b9429103d987d2`。
- Git 根：`/home/jacyl4/1base/GitLab/agent_skills`；唯一 Source：该目录下的 `skills/`，注意 `GitLab` 大小写。
- 工程维护：`tooling/scripts/`、`tooling/tests/`；仓库文档：`docs/`。Source 已与这些目录物理分离。
- 配置：`~/.config/skillshare/config.yaml`；agents/extras 空资源目录也放在该配置目录下，不写入主源的父目录。
- 没有新增定时git pull或自动sync。当前已按追加要求配置持久化/反代，并原地纳管MCP、hooks和现有Codex插件；资源范围、支持边界和独立同步流程见[资源管理记录](resource-management.md)。

当前两个写入 Target：

| Target | 路径 | 消费方 |
|---|---|---|
| codex | `~/.agents/skills` | Codex；也是 Cursor、Grok 等工具的共享发现目录 |
| antigravity-cli | `~/.gemini/antigravity-cli/skills` | 独立 `agy` CLI，不是 Antigravity IDE |

两者都是 merge + standard，各管理68条主源链接。Hermes 已通过 `skills.external_dirs` 直接读取主源，不再向 Hermes 本地目录重复分发。

其他本地、系统、插件技能继续保留。共享目录中的35个工具侧真实目录、Understand Anything 的外部链接，不由本仓库接管。原生 sync 将正确的同源人工链接纳入 manifest；后续启停和筛选可能移除它们，这属于当前已采用的受控管理语义。

## 日常更新

1. 检查 `git status`，使用既有 GitLab MR/提交工作流维护源；本次施工未自动提交或 push。
2. 只在工作区干净、分支合适时执行 `git pull --ff-only`。本次分类尚未提交时不能直接套用 pull。
3. 运行 README 中的完整测试套件和源校验。
4. 运行保护入口的默认预演，逐条审查创建、清理和命名变化。预演里的 `linked: 136` 是当前链接计数，不代表又新建136条。
5. 确认变更在已批准范围，再执行 `--apply`；检查 status、链接和第二次预演。
6. 用各 Agent 新会话验证。能读取目录不等于当前会话已重载。

`include/exclude` 仍匹配源路径的 flat ID，不是 standard 目标叶名称；过滤采用 Go filepath.Match，不能把 `**` 当递归 glob。先在独立沙箱验证规则。

禁用/启用会编辑共享 `.skillignore`。个人 `.skillignore.local` 应先配置本地 Git 忽略；首次部署没有添加个人规则。当前 `skills/.skillignore` 没有忽略规则；维护目录已移出 Source，无须靠忽略规则排除。

## Dashboard：持久化与反代（当前运行方式）

当前入口：**https://fwd.seso.icu:34000/**（内网DNS/客户端hosts需将域名指向 `10.0.0.2`；当前普通公网解析下34000连接未打通），仅内网 `10.0.0.0/24` 和现有 VPN `172.16.66.0/24` 放行。TLS沿用网关现有证书。Skillshare没有登录认证，不开放未经认证的公网访问。

- 本机 `jacyl4` 的 user systemd：`~/.config/systemd/user/skillshare.service`，已enable，Linger原本就是yes；退出登录后仍运行，开机随用户manager启动。
- 前台进程绑定 `10.0.0.186:34000`，异常退出3秒后重启；保留默认全局config和既有源，不运行额外同步/Git任务。
- 后端独立防火墙：`/etc/nftables.d/skillshare-ui.nft`，由系统 `skillshare-ui-firewall.service` 在开机加载，仅允许网关 `10.0.0.2` 与本机源地址 `10.0.0.186` 访问该端口。没有flush或覆盖现有主机/Docker规则。
- user服务启动前检查root创建的 `/run/skillshare-ui-firewall.ready`；没有保护标记时不会启动UI，会继续重试。防火墙维护须先停UI，再修改/恢复专属规则，避免短暂裸露后端；其他管理员操作若flush整个ruleset，需重新加载专属规则后再启动UI。
- 网关 `10.0.0.2` 的 `/etc/nginx/conf.d/skillshare.conf`：TLS `34000` → `http://10.0.0.186:34000`；既有SSH `14082` 不变。

```bash
systemctl --user status skillshare.service
systemctl --user restart skillshare.service
systemctl --user stop skillshare.service
journalctl --user -u skillshare.service -n 80 --no-pager
sudo systemctl status skillshare-ui-firewall.service
sudo nft list table inet skillshare_ui
```

**不要再使用 `skillshare ui start/stop` 与 systemd 混管，也不要点击Dashboard Restart/Upgrade。** 该版本Restart会派生后台进程，与systemd自动拉起前台实例冲突。升级后由 `systemctl --user restart skillshare.service` 接管生命周期。旧 `127.0.0.1:19420` 临时后台入口已停止。

反代保留实际浏览器Host及端口、真实IP和Forwarded头，关闭代理缓冲并延长SSE读取超时。现已按要求通过独立UI补丁允许精确域名 `fwd.seso.icu:34000`，MCP/Plugins/Hooks可直接管理；其余域名/跨站请求仍拒绝，原ACL/nft不变。官方CLI仍原版0.25.13，UI为0.25.13+fwd1，升级须维护补丁，见[域名白名单](domain-allowlist.md)。

**内网/VPN也不是只读。** 编辑、启停、移动、安装、删除会写主源；Git Sync的Discard changes、Force Pull和自动Commit/Pull/Merge/Push不属于本部署的使用流程。GUI Sync不经过本仓库保护入口，修改策略后先用CLI预演。

完整配置、验证、备份与精确回退见[持久化与反代记录](skillshare-resident-proxy.md)。

## 安全审计与运行门禁

逐项审计时使用 `skillshare list -g --json` 中的68个内部 ID。该版本无筛选的全局 audit 还会聚合扫描顶层分类，因此扫描数量可能大于68；不要把聚合重复计数误认为新增技能。

审计器未关闭规则、未降低 HIGH 阈值，允许报告保持非零，不能称为安全全绿。原有5个 CRITICAL 全是 Cloudflare Bearer Token 请求示例，其中变量 `$URL` 必须先确认是正确官方主机，外部 PUT/POST/DELETE 需要独立确认与最小权限。其他真实能力风险包括 Sandbox 动态执行、本机截图写文件和 Turnstile 资源操作。

已逐条复核的误报包括 SDK 示例 `system:` 参数、截图的 base64 解码、字体建议、Graphify 不读取 API key 的说明等；这些与主动恶意指令不同。

导入的 Office/Morph 文档仍包含 upstream `curl | bash` / `irm | iex` 安装示例。**本机 OfficeCLI 已存在，本次没有执行这些安装器。** 后续不要照抄执行，改用固定 Release + 校验，并先审查安装行为。`caveman-compress` 仅在明确要求时使用：它会修改指定 Markdown、保留 `.original.md`，也可能将文档发送到外部模型；本轮未运行该 helper。

## 技能内容升级

GitHub来源已关联55项。请按[单项升级流程](upstream-updates.md)操作；普通skill的Update会覆盖本地内容，Git脏状态不保护这类目录。此处与下面的Skillshare二进制升级是不同操作。

## Skillshare 程序升级

保护入口固定校验 `/usr/local/bin/skillshare` 解析到本节记录的0.25.13二进制，并核对版本，不依赖PATH选择程序。升级时须经审查同步更新保护入口的版本与路径及测试，不能只改current后继续使用旧保护规则。

1. 保持版本固定；不要将 `skillshare upgrade` 当作自动更新任务。
2. 记录当前 version、二进制校验值、配置、目标 manifest、主源 Git 状态；外置备份。
3. 下载明确版本与 checksum，精确校验目标文件名，不执行远程安装脚本。
4. 新二进制放入新的 releases 子目录。先在隔离 XDG 环境测试 schema、standard 命名、启停恢复、筛选、冲突保护、同源链接纳管和重复实际 sync。
5. 通过后切换 current；逐 Target 预演，核对差异，再执行同步和实际调用验收。UI 需要停止旧进程后重启，不能只切换链接就宣称运行版本已升级。
6. 保留旧版本及对应配置，直到新版本验收结束。

## 备份、回滚与清理

最新独立 Source 布局迁移、外置备份和针对性回退见 [布局记录](source-layout-2026-10-17.md)。以下是初次部署的历史备份与回退边界，不应直接用于撤销最新布局。

初次部署备份：`/home/jacyl4/.local/state/skillshare-onboarding/20261016-201504`，根目录权限0700。

- `source-before/`：完整施工前仓库，包括 Git 数据；不是自动覆盖源的指令。
- `targets/`：施工前消费目录快照，保留软链接和权限。
- `imports-before/`：20个独立导入 bundle 的原始内容。
- `quarantine/`：被替代的旧链接、独立副本、旧消费根；没有递归删除。
- `source-map.json` / `import-map.json`：逐项迁移映射。
- `logs/consumer-migration.json`：逐项隔离原路径和备份路径，是回退清单。
- `sandbox/`：启停、定向分发、真实同步幂等、纳管、移名、删除及恢复测试；只操作模拟 Source。

回退顺序：

1. 停止 UI 和其他同步，保存当前配置、manifest、Git差异和目标目录变化。
2. 对照当前源/目标与部署验收基线；如果出现施工后的用户编辑或新文件，先另外保存，不能覆盖。
3. 配置问题：隔离本次新增 config，或恢复对应旧配置；二进制问题：切换至已校验的旧 Release。本机施工前没有 Skillshare，停用入口也可停止使用，不必动源文件。
4. 链接问题：仅移走仍指向本次映射目标、且确认由本次创建的链接；按 consumer-migration 清单逐项恢复 quarantine 中的原件。恢复旧同源链接之前，应先恢复旧 Source 布局，否则链接会断。
5. 源布局回退：将当前分类 bundle 精确移到新的外置保留区，按 source-map 从 source-before 恢复48个原目录；20项导入保留在外置区。不要复制整个 `.git` 覆盖当前仓库，不用 reset --hard/clean，不无差别覆盖 Agent 根目录。
6. 最后恢复相应 target manifest 或隔离本次新 manifest；没有验收前不要再次 sync。验证原 HEAD/分支/remote、原目录、人工链接和有效技能。

生产没有做破坏式全量回滚演练；恢复动作只在隔离沙箱验证。quarantine 中可能有已失效旧路径的链接，它是历史证据，不是活动消费目录；保留到确认无需回退后再精确清理。

旧 `.pi/agent/skills` 和 `.gemini/antigravity/skills` 已隔离：本机真实 GSD 和 agy CLI 使用不同路径。仅移除了一处已确认空的旧 IDE root-owned 容器目录；Pi 的 AGENTS、历史和其他 Agent 状态均未清除。Claude/OpenCode/Droid 未发现对应安装或目录，没有凭名称创建再删除文件。

## 故障排查

| 现象 | 检查和处理 |
|---|---|
| CLI 有链接但 Agent 看不到 | 先检查真实扫描路径、同名重复，再开新会话；不要重复分发到所有兼容目录 |
| Hermes 名称冲突 | 查本地技能与 external_dirs 是否同名，保留独有说明后隔离副本；不要再复制主源回 Hermes 本地目录 |
| Hermes JSON序列化日期失败 | frontmatter日期写成字符串，例如 `date: "2026-02-15"`；源校验已有回归测试 |
| sync 预检阻塞 | 查看具体同名真实目录、异指向链接或未纳管断链；不要用 --force 绕过 |
| doctor 提示 Git 变更 | 当前是未提交的分类/归并变更；审核 Git 差异，不点 Discard changes |
| doctor 再次提示 scripts/tests/docs 缺 SKILL.md | 检查 Source 是否被误改回仓库根；正确值为仓库下的 skills/，不要伪造 SKILL.md |
| doctor 提示 built-in skill 未安装 | 可选管理技能未添加，不影响本机CLI/分发；不要为了消警告自动执行 upgrade --skill |
| UI打不开 | 检查user服务、root防火墙服务及ready标记、Nginx配置与34000监听；不要启动第二个CLI后台实例 |
| agy/Grok要求登录 | 链接验收与账号授权分开；授权码只交给对应仍在等待的登录进程，超时后需新一轮授权；不入仓库或报告 |
| 上游安装器重新生成副本 | 更新前后复核 Agent 目录；本仓库仍为主准，系统/插件内容留在其所有者边界内 |

## 官方依据

- [固定版本](https://github.com/runkids/skillshare/releases/tag/v0.25.13)、[固定schema](https://github.com/runkids/skillshare/blob/v0.25.13/schemas/config.schema.json)、[merge/纳管实现](https://github.com/runkids/skillshare/blob/v0.25.13/internal/sync/sync.go)
- [Antigravity CLI Skills 路径](https://www.agy.dev/docs/skills/#antigravity-cli)
- [Cursor Skills](https://cursor.com/docs/skills)
- [GSD Skills](https://github.com/open-gsd/gsd-pi/blob/b8057bc253d887dc3499fac8655ece0f50899a03/docs/user-docs/skills.md)
