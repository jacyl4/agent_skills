# Skillshare 部署安装与维护手册

> 本机实测基线：2026-10-18，Debian / 用户 `jacyl4`。本文面向日后维护者，覆盖安装恢复、技能分发、服务与反代、更新、备份、回退和排障。
> **这是已经部署系统的维护手册，不是可直接覆盖现有配置的一键安装脚本。** 历史文档中的 68 项技能、两个写入 Target、临时端口 19420 等描述已过时，以本文及实时检查为准。桌面副本来自仓库 `docs/deployment-maintenance.md`；更新时应同步两份。

## 1. 当前结论与职责

本轮检查并实际执行受保护同步成功：**126 项 Source 技能，3 个直接写入 Target，共 334 条正确主源链接**。Doctor：22 pass、1 warning、0 error、1 info；无同步漂移、坏链接或重名。50 项仓库维护测试通过。

| 组件 | 职责 / 当前状态 |
|---|---|
| GitLab 仓库 | Skills 唯一内容源及版本历史 |
| Skillshare CLI | 固定官方 v0.25.13；发现、校验、受控分发、来源与审计 |
| Skillshare Web UI | 独立补丁版 `0.25.13+fwd2`；systemd 常驻，经 Nginx 访问 |
| Magpie | **MCP 管理**；Skillshare 已撤销 MCP 纳管，不能重新导入抢写 |
| Hooks / Plugins | Skillshare 继续管理既有 8 组 hooks / 9 个 Codex 插件；原生信任、账号授权不转移 |
| Agent 自身 | 会话内技能加载、权限、安全决策及原生插件授权 |

分发正常不等于所有 Agent 的账号登录、模型调用或每条技能脚本都测试通过。本轮不执行技能内脚本，也不批量更新技能或重开所有 Agent。

## 2. 文件、目录与版本

```text
/home/jacyl4/1base/GitLab/agent_skills/   # Git 根，注意 GitLab 大小写
├── skills/                            # Skillshare 唯一 Skills Source
│   ├── automation/  data/  documents/  engineering/
│   ├── frontend/    platforms/  writing/
│   ├── .metadata.json                 # 原生技能来源、版本与基线
│   └── .license-manifest.json          # 许可证声明完整性记录
├── tooling/
│   ├── scripts/                       # 校验、保护同步、归集工具
│   ├── tests/                         # 当前 50 项测试
│   └── patches/                       # UI 本地源码补丁
├── docs/                              # 维护记录、来源/审计/许可证说明
├── README.md
└── .gitignore
```

| 路径 | 用途 |
|---|---|
| `/opt/ai/skillshare/releases/0.25.13/skillshare` | 官方 CLI 二进制 |
| `/opt/ai/skillshare/current` | 指向 `releases/0.25.13` |
| `/usr/local/bin/skillshare` | 经 current 指向官方 CLI 的稳定入口 |
| `/opt/ai/skillshare/ui-releases/0.25.13+fwd2/` | 独立 UI 二进制、构建清单和补丁 |
| `~/.config/skillshare/config.yaml` | 私有全局配置，权限 0600，不提交 Git |
| `~/.config/skillshare/agents`、`extras` | 独立资源源目录，当前为空，不是 Skills Source |
| `~/.config/systemd/user/skillshare.service` | UI user unit |
| `~/.config/systemd/user/skillshare.service.d/domain-allowlist.conf` | 实际 UI 启动路径、可信域名/网关、隐藏 Target 策略 |
| `~/.cache/skillshare-domain-ui/skillshare/ui/0.25.13+fwd2/` | 当前 UI 前端缓存，含审计文案修正，**不能当作可随便删除的普通缓存** |
| `~/.local/state/skillshare/logs/` | `operations.log`、`audit.log` |
| `~/.local/share/skillshare/backups/` | 原生 Target 分发备份 |
| `~/.local/state/skillshare-onboarding/` | 私有分阶段快照、隔离区和验证证据 |

校验基线：

```text
CLI SHA256  54bdad8c3defc8604fc5e10c9f0a4c5b8c8cfc20834d13efd1b9429103d987d2
UI  SHA256  3d308dbefa7e6e6a957acfeb2927a047c2074481dc8f8cfef4502de78c0d1432
UI 上游基线 commit  a7adb69e527c9f48eff154dce0b01c233da53004
```

校验命令：

```bash
skillshare version
readlink -f /usr/local/bin/skillshare
sha256sum /opt/ai/skillshare/releases/0.25.13/skillshare \
  /opt/ai/skillshare/ui-releases/0.25.13+fwd2/skillshare-ui
```

## 3. 技能分发与 Target 约定

默认 `merge` + `target_naming: standard`；逐技能建立链接，不覆盖无关真实目录。8 个登记 Target 如下：

| Target | 作用 | 本轮受管链接 |
|---|---|---:|
| universal | 唯一共享写入方，`~/.agents/skills` | 104 |
| antigravity-cli | Google 独立 `agy` CLI，`~/.gemini/antigravity-cli/skills` | 104 |
| hermes | 写入 `~/.hermes/skills`，含 Hermes 专用技能 | 126 |
| codex、cursor、grok、opencode、zed | `skills.enabled: false`，经 Universal 共享读取，不重复写入 | 0 |

**UI 的 “Skills off” 是关闭重复写入，不是 Agent 无技能可用。** API 应显示这五项 `skillsReadFrom: [universal]`。OMX 使用 Codex 的技能发现入口，不需要伪造独立 omx Target。

126 与 104 的差额是定向分发的 22 项 Hermes 专用技能，不是漏同步。Hermes 非受管内容以及 Understand Anything 等原生/外部链接保留，不为了让目录条目数一致而删除。local 数量以实时清单为准，CLI/API 对外部链接等条目的计数口径可能不同，不拿其差异判断受管技能缺失。

Universal 保持可见。已清理的 Warp、Antigravity IDE、Gemini CLI、Dexto、Witsy、Pi 不应重新登记；GSD 运行时也已清理。`antigravity-cli` 才是保留的 agy，不要因共享 `.gemini` 父目录而误删它。

### 每次改技能后的标准流程

以下命令以 `jacyl4` 运行，不要 sudo 整套同步：

```bash
cd /home/jacyl4/1base/GitLab/agent_skills
export PYTHONDONTWRITEBYTECODE=1
PYTHON=/home/jacyl4/.hermes/hermes-agent/.venv/bin/python

git status --short
"$PYTHON" tooling/scripts/validate_skills.py
"$PYTHON" -m unittest discover -s tooling/tests
"$PYTHON" tooling/scripts/sync_skills.py          # 默认预演
# 审查通过、变更符合本次任务后再应用：
"$PYTHON" tooling/scripts/sync_skills.py --apply
skillshare doctor -g --json
skillshare status -g --json
"$PYTHON" tooling/scripts/sync_skills.py          # 再次预演，查漂移/意外清理
```

保护脚本锁定 Source、官方二进制路径/版本、merge+standard、目标重叠和非受管冲突。升级 CLI 后它可能主动拒绝同步，应审阅兼容性并更新测试，不能绕过保护。

`linked` 是正确关联的总数，不代表每次重新创建全部链接。判断幂等要看链接目标、manifest 的 managed 内容和 Doctor 的 drift，不能只看会变化的 `updated_at`。

内容修改会经软链接即时反映到目标文件；新增/删除/改名或分发策略改变仍需同步。Agent 当前会话不一定即时重载，应按其原生方式刷新或新开会话。不要直接改消费端软链接中的内容后误以为未改 Source。

## 4. Web 服务、Nginx 与网络边界

```text
浏览器 https://fwd.seso.icu:34000/
    → Nginx 网关 10.0.0.2:34000（TLS、LAN/VPN ACL）
    → http://10.0.0.186:34000（独立 UI，后端 nft 限源）
```

**14082 是网关 SSH 端口，不是 Skillshare 端口。** 入口、反代监听、后端均用 34000。内网 DNS/客户端 hosts 应将域名解析到网关；定向内网验收不代表公网 DNS/NAT 链路已打通。

服务由 user systemd 唯一管理：enabled，`Restart=always` / 3 秒，`Linger=yes`。退出登录后仍运行。实际 ExecStart 由 drop-in 覆盖：

```text
/opt/ai/skillshare/ui-releases/0.25.13+fwd2/skillshare-ui ui -g --host 10.0.0.186 --port 34000 --no-open
```

drop-in 的关键环境变量：

```ini
Environment=SKILLSHARE_UI_TRUSTED_ORIGIN=https://fwd.seso.icu:34000
Environment=SKILLSHARE_UI_TRUSTED_PROXY=10.0.0.2
Environment=SKILLSHARE_UI_HIDE_TARGETS=warp,antigravity,gemini,dexto,witsy,pi
Environment=XDG_CACHE_HOME=/home/jacyl4/.cache/skillshare-domain-ui
```

```bash
systemctl --user status skillshare.service --no-pager
systemctl --user cat skillshare.service
systemctl --user restart skillshare.service
journalctl --user -u skillshare.service -n 100 --no-pager
loginctl show-user jacyl4 -p Linger
```

仅修改 unit/drop-in 后才先执行 `systemctl --user daemon-reload`。不要混用 `skillshare ui start/stop`，不要点 Dashboard 的 Restart/Upgrade，以免启动第二个实例或丢失补丁。

### 防火墙与可信来源

- 本机 `/etc/nftables.d/skillshare-ui.nft` 的独立 `inet skillshare_ui` 表限制到后端 IPv4 地址的流量，仅允许网关 `10.0.0.2` 与本机 `10.0.0.186`。
- 系统 `skillshare-ui-firewall.service` 在开机加载规则，再创建 `/run/skillshare-ui-firewall.ready`；UI 以该标记作为启动前置检查。**标记只是启动条件，不能代替检查实际 nft 表。**
- 网关 `/etc/nginx/conf.d/skillshare.conf` 允许 loopback、`10.0.0.0/24` 和 `172.16.66.0/24`，其他来源拒绝。
- Host 必须是 `fwd.seso.icu:34000`；Nginx 转发真实 `$http_host`，不能伪造 localhost 或受信任 Origin。
- UI 白名单还核验实际 TCP peer 为网关、HTTPS forwarded proto 和同源 Origin/Fetch 元信息。MCP/Hooks/Plugins 管理页可以通过现有反代访问；MCP 页已不再纳管任何定义。
- 没有新增用户登录认证。ACL 白名单不是身份认证，不能直接取消 ACL 开放公网。当前只监听指定 IPv4，不得未审查便扩展为 0.0.0.0 或 IPv6。

本机检查与网关管理：

```bash
systemctl status skillshare-ui-firewall.service --no-pager
sudo nft list table inet skillshare_ui
test -f /run/skillshare-ui-firewall.ready
curl --fail --show-error --silent \
  --resolve fwd.seso.icu:34000:10.0.0.2 \
  https://fwd.seso.icu:34000/api/health

ssh -p 14082 -o IdentitiesOnly=yes \
  -i /home/jacyl4/1base/@secure/id_rsa root@10.0.0.2
# 以下在网关执行：
nginx -t
# 仅配置修改且测试通过后：systemctl reload nginx
tail -n 80 /var/log/nginx/skillshare.error.log
```

curl 不使用 `-k`。资源管理 API 还要求浏览器同源证明，不能用裸 curl 返回 403 判定网页故障；应以浏览器从真实入口访问验收。Nginx 保留 `proxy_buffering off` 及长读超时以支持 SSE。

## 5. 重新安装或迁机恢复

### 5.1 准备

先确认新主机 IP、用户名、架构、路径及网关没有变化；变化时所有模板都要适配。需要 curl、tar、Git、systemd、nftables；维护 Python 需要 PyYAML。现有 Hermes venv 已可用，不往系统 Python 强行 pip 安装。不要顺手批量升级系统或执行 autoremove。

有既有仓库就复用；仅在新机器、目标路径不存在时按原 remote 克隆：

```text
https://gitlab.seso.icu:32221/jacyl4/agent_skills.git
```

保留 main、历史、上游元数据、许可证和本地未提交内容。不要 `git init`、修改 origin、`reset --hard` 或 `git clean`。

### 5.2 安装官方 CLI

使用 [官方 v0.25.13 Release](https://github.com/runkids/skillshare/releases/tag/v0.25.13) 的 `skillshare_0.25.13_linux_amd64.tar.gz` 及 `checksums.txt`；这是固定版本恢复，不代表建议永远停留此版本。将下载放到临时目录，先校验包，再解压并核验二进制 SHA256，与第 2 节一致后才用 root 安装。

```bash
# 在下载目录执行；文件应来自上述官方 Release：
grep 'skillshare_0.25.13_linux_amd64.tar.gz$' checksums.txt > selected-checksum.txt
test "$(wc -l < selected-checksum.txt)" -eq 1
sha256sum -c selected-checksum.txt
mkdir extracted
tar -xzf skillshare_0.25.13_linux_amd64.tar.gz -C extracted
sha256sum extracted/skillshare
# 确认校验通过且不是覆盖正在使用的未知文件后：
sudo install -d -m 0755 /opt/ai/skillshare/releases/0.25.13
sudo install -m 0755 extracted/skillshare /opt/ai/skillshare/releases/0.25.13/skillshare
```

新安装应建立两条稳定链接；以下只在路径不存在时创建，已有路径不覆盖，最后校验实际解析结果：

```bash
set -e
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

任一检查失败就停止，先辨识/备份现有文件，不能用强制覆盖来“通过”。日后切换 CLI 版本时，只对已确认归本部署管理的 `current` 软链接操作：先备份旧链接，在同目录创建指向已验签/校验的新发布目录的临时软链接，再用 `sudo mv -Tf 临时链接 /opt/ai/skillshare/current` 原子替换。临时路径必须未占用；不要对未知真实目录使用该命令。切换后重新执行 readlink、版本、hash 和保护同步兼容性检查；回退同样只切换该链接。不要 pipe-to-shell 安装，也不要在仓库重新执行强制 init。

### 5.3 恢复配置和部署组件

1. 从可信私有备份恢复 `config.yaml`（0600），将 `sources.skills` 校准到本机实际 `skills/`。保留三写入方/五共享读取方和 `mcp` 无受管服务器状态；不要恢复撤销前的 MCP 所有权。
2. 保存既有目标文件和 manifest；先运行仓库校验、测试、同步预演，遇到非受管同名目录先核对来源，不强制覆盖。
3. UI 必须恢复匹配的 **fwd2 二进制、build-manifest/源码补丁及当前前端缓存**。官方 CLI 不包含这些本地适配；只安装官方 release 不能复原当前域名行为。
4. 恢复本机防火墙规则及系统 unit；确认实际 nft 表已加载、ready 存在后，再恢复 UI user unit/drop-in，执行各自 daemon-reload。首次加载独立表可 `sudo systemctl enable --now skillshare-ui-firewall.service`；已有活动表不要重复 `nft -f` 堆叠规则。
5. 必要时 `sudo loginctl enable-linger jacyl4`；用 `jacyl4` 执行 `systemctl --user enable --now skillshare.service`。不要用 root 的 user manager 启动。
6. 在网关审阅并恢复单份 `skillshare.conf`，复用现有 TLS include 和 `$connection_upgrade` map；`nginx -t` 后 reload。不要复制证书私钥到文档或覆盖整套 conf.d。
7. 完成第 10 节验收，才算恢复完成。生产整机重装与重启恢复未在本轮执行，不能把这份步骤当成已经实测的灾备演练。

### 5.4 本轮可恢复的程序与前端快照

已额外保存程序目录及**修正后的完整前端缓存**，不是只有源码补丁：

```text
目录：/home/jacyl4/.local/state/skillshare-onboarding/distribution-final-20261018-120409/
归档：skillshare-program-ui-artifacts.tar.gz
SHA256：6c1fec10f541d259ebb9afee9e799ead2db2ed46fa5961f1a1ed4fdfe736008c
```

归档含 `opt/ai/skillshare/` 与 `.cache/skillshare-domain-ui/skillshare/ui/0.25.13+fwd2/`；该目录还保存本轮配置快照、user unit/drop-in、本机防火墙文件和 `nginx-skillshare.conf`。归档本身不含账户凭据；旁边的私有配置可能有凭据，整个目录维持 0700 私有保存。

恢复前先校验归档 hash，使用 `tar -tzf` 检查成员，并解到新建临时目录，**不要直接解到 `/` 覆盖生产**。核对程序 hash、缓存文件和目标机器参数后，停 UI，再将受影响版本目录、缓存和经审阅的配置分别恢复到第 2 节位置。文件属主/权限分别按 root 管理的程序目录与 jacyl4 管理的缓存恢复，然后按第 5.3 节启动、验收。

这是同机私有快照，不是异机灾备。迁机或磁盘故障恢复前，必须将该目录及所需私有配置安全复制到可信备份介质；只有桌面 Markdown 或 Git 仓库不包含这些二进制、前端缓存与凭据。未来升级后应另生成新归档和 hash，不能沿用本次摘要。

**后续 MCP 默认排除适配：** 上述 12:08 全程序快照不含这项后续前端默认值。最新前端缓存另存 `/home/jacyl4/.local/state/skillshare-onboarding/sync-repair-20261018-135545/ui-cache-mcp-off1.tar.gz`，SHA256 为 `5ff378c3e04c16962f2eaa9f7b0417782a3e537cd981d77bddfce3f2da66317d`；恢复旧程序快照后，应校验并恢复此更新缓存，或按下一节补丁流程重建。该缓存仍包含审计文案修正，恢复时不覆盖 Magpie/Agent 配置。

## 6. 技能 GitHub 来源与更新

原生更新映射位于 `skills/.metadata.json`；来源证据见仓库 `docs/upstream-sources.json`、`docs/upstream-updates.md`。有来源不等于适合自动覆盖；本地包装和无可靠来源的技能不应按同名仓库强行绑定。

```bash
skillshare check -g --json
# 此版本单项使用 Source 相对路径，不是 UI 的双下划线 ID：
skillshare check -g frontend/animation/gsap-core
skillshare update -g frontend/animation/gsap-core --dry-run
# 仅在备份、逐文件审阅及风险判断完成后：
skillshare update -g frontend/animation/gsap-core --diff
```

**普通技能 Update 会替换整个技能目录，不会自动合并本地修改；Git dirty 也不是保护。** 更新前备份该技能完整目录及元数据，再比较变动。保留本地 frontmatter 规范化、机器适配和 LICENSE/NOTICE；更新后重新校验、测试和保护同步。dry-run 不等于下载的新内容已全部审阅。

不批量 `update --all`，不使用 `--force` / `--skip-audit` 绕过风险。不能仅凭远端 HEAD 变化判定本地每个附件落后。更改元数据基线时不要伪造导入 commit 或把本地修改冒充上游原件。

## 7. CLI、UI 升级与补丁

这是两条独立发布链，更新 CLI 不会更新 UI，反之亦然。

当前本地补丁：

1. `tooling/patches/skillshare-v0.25.13-trusted-origin.patch`：精确域名/网关同源守卫。
2. `tooling/patches/skillshare-v0.25.13-hide-warp-target.patch`：显式隐藏已清理的 Target 候选，保留通用 Target。
3. `tooling/patches/skillshare-v0.25.13-audit-sync-label.patch`：11 语言共 55 条提示，澄清审计阈值不阻止普通同步。
4. `tooling/patches/skillshare-v0.25.13-sync-mcp-default-off.patch`：Sync 页默认排除 MCP，避免与 Magpie 职责混淆。

前两项已在 fwd2 二进制内；第三、四项当前通过前端缓存资源适配，JS 文件/引用和 service worker 缓存名均已更新。**删缓存或升级可能丢失提示与默认值修正；只备份 Go 二进制不够。**

升级流程：备份当前 artifact/缓存/配置 → 核对新版本官方来源、校验与配置迁移 → 在干净源码对补丁 `git apply --check` → 审阅上游是否已原生解决，决定重用或移除 → 隔离容器构建和测试 → 发布到新的版本目录 → 切换 user drop-in → 验证健康/同源正负用例/技能分发 → 保留旧版本供回退。

不要在生产宿主直接构建或盲目套用旧版压缩资源。构建基线和参数见 UI 发布目录的 `build-manifest.json`；本机已验证基线是 Go 1.26.3、CGO_ENABLED=0。新版本构建应使用该版本要求的工具链，不机械锁死旧工具链。

CLI 升级还要同步审阅 `tooling/scripts/sync_skills.py` 的版本/路径 pin 和测试。升级失败回退版本路径/启动配置，不能回退整个 HOME 或 Source 来“修复程序”。

## 8. MCP、审计、插件与已知提示

### MCP 已交给 Magpie

Skillshare 已用 `mcp remove --keep-files` 撤销 context7、crawl4ai、qwebbridge 的 3 个定义/4 个绑定；所有权记录为 0，Agent 配置保持。以下应返回无变更：

```bash
skillshare sync mcp -g --dry-run --json
```

网页仍可能展示 unmanaged MCP，这是只读发现，不代表接管。不要重新 import 或执行 Skillshare 的 MCP add/edit/sync 作为日常配置流程；MCP 日常配置交给 Magpie。恢复旧 Skillshare 快照时尤其不能重新覆盖 Magpie。

Sync 页的 MCP 默认不勾选；刷新仍不参与，真实点击 Sync 验证没有 MCP 写入请求。此项只改默认选择，用户以后仍可手动勾选，不是服务端永久禁用 MCP 功能。

### 审计不是分发失败

最新实测扫描 126 项：5 条 CRITICAL、64 条 HIGH、3 项达到安装/更新阈值，scanErrors=0。普通技能同步没有被其阻断；网页旧 `Blocked from sync` 已改为“达到审计阈值（不阻止同步）”。风险与安装/更新审核保留，不假装安全全绿。

godmode 按用户要求保留，提示注入/绕过能力风险并未消失。create-skill 和 cloudflare 的对应 CRITICAL 示例有已记录误报背景，不代表所有 HIGH 都是误报。详细记录见 `docs/audit-review.md`。

Doctor 唯一 warning 是可选内建 Skillshare 管理 skill 未安装，不影响当前分发，不必为消除提示盲目安装。Hermes 常驻索引约 11.5K token，超过默认 10K 提示；数十万 on-demand token 是可按需加载的总量，不是每轮全部注入。不要为了压低数字删除用户技能。

### Work Pets 不能卸载

Codex 将其标为 `INSTALLED_BY_DEFAULT`，远端卸载返回 403：`Installed-by-default plugins cannot be uninstalled`。已清掉 Skillshare 失败的 pending remove，同步为 noop；仍是已安装、启用状态。不是 Nginx 或登录问题，不反复删除、不删缓存冒充成功。其他插件保持原生状态；详见 `docs/work-pets-removal.md`。

## 9. 备份、Git 与精准回退

### 必须备份的边界

- Git 仓库：Source、隐藏元数据/忽略文件、许可证、tooling、docs、未提交变更；按需 `git bundle create` 保留已提交历史，注意 bundle **不含未提交和未跟踪文件**。
- 私有配置：`~/.config/skillshare/`、目标 manifest/原生配置、Skillshare 状态/所有权。
- 部署：`/opt/ai/skillshare/` 相关版本和构建清单、UI 缓存、user unit/drop-in、本机 nft 文件及系统 unit、网关单份反代配置。
- 凭据、授权和 SSH 私钥另走可信安全备份，不写入 Git、桌面 Markdown 或公开日志。

修改前用 0700 外置目录存快照并记录摘要；备份含配置可能带密钥，应限制权限。不要将整个私有备份复制到桌面。现存私有证据由仓库 `.omx/plans/*backup-path` 指针索引；若只迁走 Git，它们指向的外置内容不会一起迁移，需单独安全保存。

Git 日常只用明确文件集合提交，保持既有 origin/main。确认工作区干净且分支合适后才 `git pull --ff-only`；冲突/分叉停止核对，不 force、reset 或 clean。普通 push 成功不能证明已部署，反过来同步成功也不能证明已 push。当前没有自动 Git pull/sync 定时任务。

### 回退顺序

1. 先保存回退前当前状态和后续修改，确定只撤销哪一项。
2. 技能内容回退：恢复单技能完整快照及对应元数据，再运行校验/测试/保护同步。Git 可用新 revert 提交，不重写远端历史。
3. UI 回退：停止 user 服务，恢复对应版本 artifact/缓存及 drop-in，daemon-reload 后启动；健康和同源 API 验证。回退为官方原版 UI 会失去本地域名适配，不能声称功能相同。
4. 维护防火墙：**先停 UI**，只更改专属规则/服务，检查实际 nft 表和 ready 后再启动 UI。不 flush 全局 ruleset，不恢复旧 Docker 动态规则。
5. 反代回退：仅恢复审核后的单份配置，`nginx -t` 再 reload，不回滚整套 Nginx，不动 SSH 14082。
6. 不将历史 Skillshare MCP 所有权恢复到当前 Magpie 管理配置上；不恢复整套 HOME，也不擅自清空隔离区。

## 10. 验收与排障速查

| 现象 | 检查与处理 |
|---|---|
| Target 为 Skills off | 对照第 3 节；五个共享读取方是正常设计，不全部打开 |
| 某技能少分发 | 核查 `targets`、ignore/include/exclude、Source 有效性；Hermes 22 项专用技能只去 Hermes |
| preflight blocked | 看 Source/版本 pin、重叠或非受管冲突；保留现场，不 `--force` |
| UI 起不来 / 重启循环 | journal、端口占用、实际 nft 表及 ready、二进制/缓存路径；不要自行 touch 标记绕过保护 |
| 502 / SSE 卡住 | 网关 error.log、后端 service/监听、防火墙、buffering 与超时 |
| 域名管理页 403 / Host 被拒绝 | 核查真实 Host:端口、TCP peer、Origin、HTTPS、ACL；不要伪造受信任头放行 |
| DNS 连不上 | 检查客户端是否将域名指向 10.0.0.2；用 --resolve 的可信 TLS 检查只证明内网链路 |
| Plugin 删除泛化报错 | 看原生命令错误；默认预装策略拒绝与本地权限错误不同 |
| 审计非绿 | 按真实风险逐项复核，不靠关规则或改标签伪装安全 |
| `symlink to external location (...), kept` | 属于保留外部链接的提示，不是同步失败。当前 Magpie/Understand Anything 的链接应保留；看 API failed、日志状态和 Doctor drift，不为清空提示删除链接或改 Source |
| 更新后许可证/基线失败 | 对照真实上游声明和本地修订，不删除回归测试或伪造来源 |

建议保留如下证据：Source 校验通过；测试通过；预演无意外清理；实际同步成功；334 条受管链接（此基线）指向正确 Source；Doctor 无 error/drift/broken/duplicate；HTTPS health 200；浏览器三写入方/五读取方正确；MCP 受管 0；hooks/plugins 正常；Nginx `-t` 通过。

```bash
skillshare log -g --since 2h --status error --json
skillshare log -g --audit --tail 30 --json
skillshare doctor -g --json
skillshare status -g --json
```

日志可能含私有路径或敏感请求背景，分享前脱敏，不删除历史错误来制造“全绿”。本轮证据指针：`.omx/plans/distribution-final-backup-path`。

## 11. 本轮已验证与未覆盖事项

- 2026-10-18：126 项源校验、50 项测试、保护预演与实际同步成功。
- 104 + 104 + 126 = **334 条受管链接逐项解析到正确主源**；5 项关闭重复写入的登记保留。
- Doctor 22 pass / 1 warning / 0 error / 1 info；55/55 原生完整性基线验证；hooks 8、plugins 9 in sync；MCP 0。
- 真实 HTTPS Targets/API 检查三写入方和五 Universal 读取方；审计126项、3项达到阈值、无扫描错误，godmode 保留。
- TLS health 正常、user 服务/系统防火墙服务均 enabled，Linger=yes；网关 Nginx `-t` 通过。
- **未在本轮做**整机重启、生产灾备恢复、所有 Agent 新会话模型调用、远端技能实际升级；上述是边界，不以路径验证冒充调用验证。

后续 Source 数量、版本或路由改变时，应重新采集以上基线，不机械要求永远是 126/334。
