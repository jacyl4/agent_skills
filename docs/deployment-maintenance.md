# Skillshare 部署安装与维护手册

> 更新：2026-10-18，Debian / 用户 `jacyl4`。适用于现有部署的维护与恢复，不是一键覆盖脚本。仓库维护版：`docs/deployment-maintenance.md`；桌面保留同内容副本。

## 1. 当前职责与分发

| 组件 | 职责 |
|---|---|
| GitLab 仓库 | 自维护 Skills 的唯一内容源与版本历史 |
| Skillshare | 技能分发、来源/审计，以及既有 8 组 hooks、9 个 Codex 插件 |
| Magpie | **MCP 与 RTK**；Skillshare 不重新接管其配置或 RTK hooks |
| Agent | 会话加载、账号、审批及原生信任 |

Skills 使用 `merge` + `target_naming: standard`，目标映射如下：

| Target | 写入位置 / 读取方式 | 受管链接基线 |
|---|---|---:|
| universal | `~/.agents/skills`，唯一共享写入方 | 104 |
| antigravity-cli | `~/.gemini/antigravity-cli/skills`，Google `agy` CLI | 104 |
| hermes | `~/.hermes/skills`，含 22 项专用技能 | 126 |
| codex、cursor、grok、opencode、zed | 关闭重复写入，`skillsReadFrom: [universal]` | 0 |

**Skills off 不表示不能读取技能。** OMX 沿用 Codex 技能入口，不单设 Target；Universal 保持可见。已清理的 Warp、Antigravity IDE、Gemini CLI、Dexto、Witsy、Pi/GSD 不重新登记。不要误删 agy 仍使用的 `.gemini` 共享目录。

原生、Magpie 和 Understand Anything 等外部技能不属于本 Source；保留其真实目录/链接，不为统一目录数量而删除。CLI/API 的 local 计数口径可能不同。

### MCP 边界

Skillshare 受管 MCP 定义及所有权记录均为 **0**；Agent 原生配置保留，日常只在 Magpie 管理。Sync 页 **MCP 默认不勾选，刷新后仍排除**；实测点击 Sync 没有 MCP 写入请求。此项是默认选择，不是服务端永久禁用，用户仍能手动勾选。

```bash
# 只读确认应无变更；不是日常 MCP 同步入口
skillshare sync mcp -g --dry-run --json
```

不要重新 import/add/edit MCP，或恢复撤销纳管前的所有权，覆盖 Magpie 后续配置。网页显示 unmanaged 只是发现已有配置。

## 2. 目录、程序与配置

```text
/home/jacyl4/1base/GitLab/agent_skills/   # Git 根，注意 GitLab 大小写
├── skills/                            # 唯一 Skills Source
│   ├── automation/  data/  documents/  engineering/
│   ├── frontend/    platforms/  writing/
│   ├── .metadata.json                 # 来源、版本、本地基线
│   └── .license-manifest.json          # 许可证声明完整性
├── tooling/{scripts,tests,patches}/     # 校验、保护同步、测试、UI 补丁
├── docs/
├── README.md
└── .gitignore
```

| 路径 | 用途 |
|---|---|
| `/opt/ai/skillshare/releases/0.25.13/skillshare` | 固定官方 CLI |
| `/opt/ai/skillshare/current` | 链接到 `releases/0.25.13` |
| `/usr/local/bin/skillshare` | 链接到 `/opt/ai/skillshare/current/skillshare` |
| `/opt/ai/skillshare/ui-releases/0.25.13+fwd2/` | 独立 UI 二进制、构建清单、源码补丁 |
| `~/.config/skillshare/config.yaml` | 全局私有配置，0600，不入 Git |
| `~/.config/skillshare/{agents,extras}` | 独立资源源目录，不是 Skills Source |
| `~/.config/systemd/user/skillshare.service` | UI user unit |
| 同目录 `skillshare.service.d/domain-allowlist.conf` | 覆盖 UI 启动路径和环境变量 |
| `~/.cache/skillshare-domain-ui/skillshare/ui/0.25.13+fwd2/` | **含本地适配的前端缓存，不能随意删除** |
| `~/.local/state/skillshare/logs/` | 操作与审计日志 |
| `~/.local/share/skillshare/backups/` | 原生分发备份 |
| `~/.local/state/skillshare-onboarding/` | 私有快照、隔离区及证据 |

```text
CLI SHA256: 54bdad8c3defc8604fc5e10c9f0a4c5b8c8cfc20834d13efd1b9429103d987d2
UI  SHA256: 3d308dbefa7e6e6a957acfeb2927a047c2074481dc8f8cfef4502de78c0d1432
UI 上游 commit: a7adb69e527c9f48eff154dce0b01c233da53004
```

```bash
skillshare version
readlink -f /usr/local/bin/skillshare
sha256sum /opt/ai/skillshare/releases/0.25.13/skillshare \
  /opt/ai/skillshare/ui-releases/0.25.13+fwd2/skillshare-ui
```

## 3. 技能日常维护

以 `jacyl4` 运行，不 sudo 整套同步：

```bash
cd /home/jacyl4/1base/GitLab/agent_skills
export PYTHONDONTWRITEBYTECODE=1
PYTHON=/home/jacyl4/.hermes/hermes-agent/.venv/bin/python

git status --short
"$PYTHON" tooling/scripts/validate_skills.py
"$PYTHON" -m unittest discover -s tooling/tests
"$PYTHON" tooling/scripts/sync_skills.py          # 默认预演
# 审查创建、替换和清理范围后再应用：
"$PYTHON" tooling/scripts/sync_skills.py --apply
skillshare doctor -g --json
skillshare status -g --json
"$PYTHON" tooling/scripts/sync_skills.py          # 检查同步后的漂移
```

保护脚本检查 Source、官方二进制版本/路径、命名、重叠及非受管冲突；只同步技能，不同步 MCP/hooks/plugins。CLI 升级后需同步审阅版本 pin 和测试，不能绕过阻断。

`linked` 是关联总量，不是本次新增数；幂等检查以链接目标、manifest managed 内容和 Doctor drift 为准，不比较更新时间。链接中的内容修改直接作用于 Source；新增、删除、改名或分发策略变化后仍需 sync。Agent 当前会话不一定即时重载。

Git 保留既有 origin/main；仅在工作区干净、分支合适时 `git pull --ff-only`。不 force/reset/clean、不批量自动提交；当前没有自动 pull/sync 定时任务。Git push 成功与部署/分发成功分别验收。

### 单技能上游更新

映射见 `skills/.metadata.json`，来源例外见 `docs/upstream-updates.md`。不把本地包装或未知来源强行绑定同名仓库。

```bash
skillshare check -g --json
# 此版本使用 Source 相对路径，不是 UI 双下划线 ID：
skillshare check -g frontend/animation/gsap-core
skillshare update -g frontend/animation/gsap-core --dry-run
# 完成备份和差异审查后，才实际更新：
skillshare update -g frontend/animation/gsap-core --diff
```

**普通技能 Update 替换整个目录，不合并本地修改，Git dirty 也不能保护它。** 先保存单技能完整目录及元数据，保留本地适配和 LICENSE/NOTICE；更新后重跑上述校验/测试/同步。dry-run 不等于新内容已审阅。不批量 `update --all`，不使用 `--force` / `--skip-audit`，不伪造来源或基线。

## 4. 常驻服务与反代

```text
https://fwd.seso.icu:34000/
  → Nginx 10.0.0.2:34000（TLS、LAN/VPN ACL）
  → http://10.0.0.186:34000（独立 UI、nft 限源）
```

**14082 是网关 SSH 端口。** 内网 DNS/hosts 应把域名指向网关；定向内网验收不证明公网 DNS/NAT 已通。

UI 使用 user systemd，enabled、`Restart=always` / 3 秒、`Linger=yes`。生命周期只由 systemd 管理，不混用 `skillshare ui start/stop` 或 Dashboard Restart/Upgrade。

```text
实际 ExecStart:
/opt/ai/skillshare/ui-releases/0.25.13+fwd2/skillshare-ui ui -g --host 10.0.0.186 --port 34000 --no-open
```

```ini
# domain-allowlist.conf 的关键变量
Environment=SKILLSHARE_UI_TRUSTED_ORIGIN=https://fwd.seso.icu:34000
Environment=SKILLSHARE_UI_TRUSTED_PROXY=10.0.0.2
Environment=SKILLSHARE_UI_HIDE_TARGETS=warp,antigravity,gemini,dexto,witsy,pi
Environment=XDG_CACHE_HOME=/home/jacyl4/.cache/skillshare-domain-ui
```

```bash
systemctl --user status skillshare.service --no-pager
systemctl --user cat skillshare.service
journalctl --user -u skillshare.service -n 100 --no-pager
loginctl show-user jacyl4 -p Linger
# 仅 unit/drop-in 改动后先 daemon-reload；日常重启直接执行 restart
systemctl --user restart skillshare.service
```

网络约束集中如下，变更域名/IP/端口时必须联动审阅：

- 本机 `/etc/nftables.d/skillshare-ui.nft` 的 `inet skillshare_ui` 表，只允许网关与本机访问该 IPv4 后端地址。不要未经审阅扩展到 0.0.0.0/IPv6。
- 系统 `skillshare-ui-firewall.service` 加载规则后创建 `/run/skillshare-ui-firewall.ready`。UI 启动检查该标记，但**实际 nft 表才是保护，不能自行 touch 标记绕过**。
- 网关 `/etc/nginx/conf.d/skillshare.conf` 放行 loopback、`10.0.0.0/24`、`172.16.66.0/24`，拒绝其他来源。沿用现有 TLS include、`$connection_upgrade`、SSE 长超时与 `proxy_buffering off`。
- Nginx 校验精确 Host `fwd.seso.icu:34000` 并转发真实 `$http_host`；UI 还检查 TCP peer、HTTPS 和同源 Origin/Fetch 信息，不伪造 localhost/Origin。
- 没有独立登录认证，ACL 不等于身份认证；不直接取消 ACL 开放公网。

```bash
systemctl status skillshare-ui-firewall.service --no-pager
sudo nft list table inet skillshare_ui
test -f /run/skillshare-ui-firewall.ready
curl --fail --show-error --silent \
  --resolve fwd.seso.icu:34000:10.0.0.2 https://fwd.seso.icu:34000/api/health
ssh -p 14082 -o IdentitiesOnly=yes \
  -i /home/jacyl4/1base/@secure/id_rsa root@10.0.0.2
# 在网关：
nginx -t
# 配置修改且测试通过后才 systemctl reload nginx
tail -n 80 /var/log/nginx/skillshare.error.log
```

TLS 检查不加 `-k`。资源管理 API 需要浏览器同源证明，裸 curl 的 403 不能替代真实浏览器验收。

## 5. 重新安装或迁机恢复

### 准备与官方 CLI

确认用户名、架构、路径、IP 与网关；变化时先适配。所需工具为 curl/tar/Git/systemd/nftables，以及带 PyYAML 的维护 Python。已有仓库直接复用；仅新机目标目录不存在时从原 remote 克隆：`https://gitlab.seso.icu:32221/jacyl4/agent_skills.git`。不要强制 init 或覆盖未提交内容。

从 [官方 v0.25.13 Release](https://github.com/runkids/skillshare/releases/tag/v0.25.13) 下载固定版本恢复包与 checksums，校验后再安装；这不是“永远不升级”的要求。

```bash
set -e
# 在新建的临时下载目录执行：
grep 'skillshare_0.25.13_linux_amd64.tar.gz$' checksums.txt > selected-checksum.txt
test "$(wc -l < selected-checksum.txt)" -eq 1
sha256sum -c selected-checksum.txt
mkdir extracted
tar -xzf skillshare_0.25.13_linux_amd64.tar.gz -C extracted
sha256sum extracted/skillshare
# 确认与第2节 hash一致，且目标没有需要保护的未知文件后：
sudo install -d -m 0755 /opt/ai/skillshare/releases/0.25.13
sudo install -m 0755 extracted/skillshare /opt/ai/skillshare/releases/0.25.13/skillshare
if [ ! -e /opt/ai/skillshare/current ] && [ ! -L /opt/ai/skillshare/current ]; then
  sudo ln -s releases/0.25.13 /opt/ai/skillshare/current
fi
test "$(readlink -f /opt/ai/skillshare/current)" = /opt/ai/skillshare/releases/0.25.13
if [ ! -e /usr/local/bin/skillshare ] && [ ! -L /usr/local/bin/skillshare ]; then
  sudo ln -s /opt/ai/skillshare/current/skillshare /usr/local/bin/skillshare
fi
test "$(readlink -f /usr/local/bin/skillshare)" = /opt/ai/skillshare/releases/0.25.13/skillshare
skillshare version
```

已有路径或检查不符就停止辨识，不强制覆盖、不 pipe-to-shell 安装。升级时只切换已确认归本部署管理的 `current` 软链接：备份旧链接，在同目录创建未占用的临时新链接，再以 `sudo mv -Tf 临时链接 /opt/ai/skillshare/current` 原子替换；不能对未知真实目录操作。之后重查解析路径、hash、版本与同步兼容性。

### 恢复部署组件

1. 备份现有目标和 manifest；恢复经审阅的全局配置（0600），校准 Source、三写入/五读取路由，保持 MCP 无受管服务器。
2. 恢复匹配的 fwd2 二进制、构建清单和**最新前端缓存**；只有官方 CLI 或 Git 仓库不足以复原当前 UI。
3. 恢复专属 nft 文件和系统 unit，daemon-reload；首次加载可 `sudo systemctl enable --now skillshare-ui-firewall.service`。已有活动表不要重复加载；检查实际规则及 ready 后才启动 UI。
4. 恢复 user unit/drop-in，用 `jacyl4` 执行 `systemctl --user daemon-reload`、`systemctl --user enable --now skillshare.service`；必要时 `sudo loginctl enable-linger jacyl4`，不要使用 root 的 user manager。
5. 网关只恢复单份经审阅的反代配置，复用现有证书和 map，`nginx -t` 后 reload。
6. 执行第3节检查及第9节验收，不运行技能脚本或批量更新作为验证。

### 可恢复快照

以下均在 `~/.local/state/skillshare-onboarding/`；需要**两份组合**恢复当前 UI：

| 相对路径 | 内容 / SHA256 |
|---|---|
| `distribution-final-20261018-120409/skillshare-program-ui-artifacts.tar.gz` | 程序与早期缓存；`6c1fec10f541d259ebb9afee9e799ead2db2ed46fa5961f1a1ed4fdfe736008c` |
| `sync-repair-20261018-135545/ui-cache-mcp-off1.tar.gz` | 最新缓存，含审计文案与 MCP 默认排除；`5ff378c3e04c16962f2eaa9f7b0417782a3e537cd981d77bddfce3f2da66317d` |

第一份同目录还保存配置、user unit/drop-in、防火墙文件及 `nginx-skillshare.conf`。先校验 hash、`tar -tzf` 检查成员，再解到新临时目录；**不要直接解到 `/` 覆盖生产**。停 UI 后精准恢复版本/缓存，程序归 root、缓存归 jacyl4，再按前述步骤启动。

同机快照不是异机灾备：应另存到可信备份介质。整个私有目录0700；文档/Git不含二进制、缓存或凭据，不把配置备份搬到公开桌面。

## 6. UI 补丁与程序升级

CLI 与 UI 是两条发布链，更新一方不会自动更新另一方。`tooling/patches/` 中当前四项为：

| 补丁文件 | 作用 |
|---|---|
| `skillshare-v0.25.13-trusted-origin.patch` | 精确域名、网关同源守卫 |
| `skillshare-v0.25.13-hide-warp-target.patch` | 隐藏已清理 Target 候选 |
| `skillshare-v0.25.13-audit-sync-label.patch` | 澄清审计阈值不阻止普通同步 |
| `skillshare-v0.25.13-sync-mcp-default-off.patch` | Sync 默认排除 MCP |

前两项在 fwd2 二进制内，后两项目前通过前端缓存适配，并更新 JS 引用及 service worker 缓存名。**删缓存或升级会丢失这些适配，只备份二进制不够。**

升级顺序：备份 → 核对官方来源/hash与迁移要求 → 干净源码 `git apply --check` → 审阅上游是否已解决、重用或移除补丁 → 隔离容器构建/测试 → 新版本目录发布 → 切换 drop-in/CLI链接 → 第9节验收 → 保留旧版本。

不在生产宿主构建，不盲套旧压缩资源。构建参数见发布目录 `build-manifest.json`；旧基线为 Go1.26.3、CGO_ENABLED=0，新版本按其要求选工具链。CLI 升级须审阅保护脚本的版本 pin 与测试；失败回退程序/缓存，不回退整个 Source/HOME。

## 7. 风险与常见提示

| 提示 / 现象 | 判断与处理 |
|---|---|
| `symlink to external location (...), kept` | 正常保留外部链接，不是失败。看 API failed、操作日志及 Doctor drift，不删除 Magpie/原生链接来清零 |
| 常驻 / on-demand 上下文预算超限 | 常驻索引与按需正文总量不同；不是每轮全量注入，不为清零而擅删技能或抬高阈值 |
| 可选 Skillshare 内建 skill 未安装 | 不影响分发，不为消除 Doctor warning盲目安装 |
| 审计非绿 / 原 `Blocked from sync` | 原文案已修正；风险不阻止普通技能同步，安装/更新审核仍保留 |
| Work Pets 删除403 | OpenAI 默认预装策略拒绝；已清 pending remove，仍安装/启用，不删缓存冒充卸载 |
| Target Skills off / 数量不同 | 对照第1节共享读取与定向分发，不全部开启重复写入 |
| preflight blocked | 保留现场，查版本pin、命名、重叠或非受管冲突，不强制覆盖 |
| UI 不启动 / 重启循环 | journal、端口、路径、实际 nft 表与ready；不伪造标记 |
| 502 / SSE卡住 | 查网关error.log、后端监听/防火墙、buffering及超时 |
| 403 / Host拒绝 | 查真实Host:端口、TCP peer、HTTPS、Origin与ACL，不伪造可信头 |
| 域名连接失败 | 核查客户端解析至10.0.0.2；内网 --resolve 验收不代表公网可达 |
| 更新后许可证/基线失败 | 对照真实声明与本地修订，不删测试或伪造来源 |

2026-10-18 审计基线：126项，5 CRITICAL、64 HIGH、3项达到安装/更新阈值，scanErrors=0。godmode按用户要求保留，风险不消失；不能把个别示例误报推成全体告警安全。详情见仓库 `docs/audit-review.md`、`docs/work-pets-removal.md`。

## 8. 备份与精准回退

需备份：仓库及未提交内容、隐藏元数据/忽略文件/许可证；私有配置、状态/所有权与目标manifest；程序/缓存、unit/drop-in、专属nft文件、网关单份反代配置。`git bundle` 只含已提交历史，不含未提交或未跟踪文件。凭据另走安全备份，不入Git或本文。

操作前在0700外置目录留存当前状态/hash；`.omx/plans/*backup-path` 指向的外置内容不会随Git迁移。回退只处理本次差异：

1. **技能：** 恢复单技能完整快照和对应元数据，再校验/测试/保护同步；Git用新revert，不改远端历史。
2. **UI：** 停user服务，恢复匹配artifact/缓存/drop-in，必要时daemon-reload再启动；退到官方原版会失去本地域名适配。
3. **防火墙：** 先停UI，只调整专属表/服务；确认实际规则与ready后再启UI。不flush全局ruleset或恢复旧Docker动态规则。
4. **反代：** 只恢复审核后的单份配置，`nginx -t` 后reload；不回滚整套Nginx或修改SSH14082。
5. 不恢复旧MCP所有权覆盖Magpie，不覆盖整个HOME，不擅自清空隔离区；保留回退前的后续修改。

## 9. 验收与日志

2026-10-18 分发基线：126项Source、334条正确受管链接、50项测试通过；Doctor 22 pass / 1 warning / 0 error / 1 info，无漂移/坏链/重名，55/55原生完整性验证。数量会变，后续应重新采集，不机械要求固定值。

每次变更按需确认：保护预演无意外清理 → 实际同步0失败 → 三写入/五读取路由正确 → MCP受管0且Sync不发MCP写入 → hooks/plugins正常 → HTTPS health200、浏览器无错误 → 服务enabled/active、Linger=yes、专属nft生效、网关`nginx -t`通过。

```bash
skillshare log -g --since 2h --status error --json
skillshare log -g --audit --tail 30 --json
skillshare doctor -g --json
skillshare status -g --json
```

分享日志前脱敏，不删除历史错误制造“全绿”。证据指针为 `.omx/plans/distribution-final-backup-path`、`.omx/plans/sync-repair-backup-path`。本轮未做整机重启、生产灾备恢复、所有Agent新会话模型调用或远端技能实际升级，不把路径/协议检查冒充完整E2E验收。
