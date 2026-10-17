# fwd.seso.icu 精确白名单（2026-10-17）

## 当前入口

直接通过既有Nginx域名管理，不再需要SSH隧道：

- `https://fwd.seso.icu:34000/mcp`
- `https://fwd.seso.icu:34000/hooks`
- `https://fwd.seso.icu:34000/plugins`

左栏Extras下面有对应入口。已有页面可强制刷新；若侧栏滚动到其他位置，也可直接打开上面的地址。

这是针对官方v0.25.13缺少可信域名开关的**本机UI专用补丁**，不是声称上游原版支持该配置。白名单初始UI版本 `0.25.13+fwd1`；当前由 [Warp 清理](warp-cleanup.md) 的 `0.25.13+fwd2` 继承同一守卫；官方CLI、`current`链接及其保护同步入口仍是原版 `0.25.13`。没有修改技能、MCP/hooks定义、原生审批或插件安装状态。

## 放行条件

仅扩展MCP、Hooks、Plugins共用的管理守卫；原有localhost/IP策略保留。新增域名分支必须同时满足：

1. `Host`精确匹配 `fwd.seso.icu:34000`，不接受别名、子域后缀、其他端口或通配域名。
2. 后端实际TCP peer为 `10.0.0.2`；不依据X-Forwarded-For/X-Real-IP判断身份。
3. 已确认的网关覆盖 `X-Forwarded-Proto: https`，多值不接受。
4. Origin若存在必须精确匹配 `https://fwd.seso.icu:34000`；无Origin时必须有 `Sec-Fetch-Site: same-origin`。跨站、仅same-site、错误Origin、缺少浏览器证明或重复安全头均拒绝。
5. Nginx首先对原始 `$http_host`做精确域名和端口检查；向后端转发真实 `$http_host`，不是把任意请求伪装成白名单Host。没有伪造localhost/Origin。

未改restart/upgrade守卫、native信任、编辑器本地打开检查。原有LAN `10.0.0.0/24`、VPN `172.16.66.0/24` ACL和后端专属nft防火墙保持不变；没有增加公网映射或放宽接收范围。

**白名单不是登录认证。** 本轮按用户要求只增加指定域名，不新增Basic Auth/SSO；原允许LAN/VPN中的访问者仍被视为可信管理员。若这些网段并非全可信，应另行增加认证或收窄ACL。

## 部署位置

下表记录白名单初始发布；当前服务已切换到 `+fwd2`，相同目录布局与安全策略保持，见 [Warp 清理](warp-cleanup.md)。

| 路径 | 作用 |
|---|---|
| `/opt/ai/skillshare/ui-releases/0.25.13+fwd1/skillshare-ui` | 独立UI二进制，root-owned 0755；服务用户不可写 |
| 同目录 `build-manifest.json`、`source.patch` | 上游commit、patch/binary SHA及构建说明 |
| `~/.config/systemd/user/skillshare.service.d/domain-allowlist.conf` | UI启动路径及明确的origin/proxy环境变量 |
| `~/.cache/skillshare-domain-ui/skillshare/ui/0.25.13+fwd1/` | 与官方CLI分离的UI资源缓存；复制现有v0.25.13前端，未改前端代码 |
| `10.0.0.2:/etc/nginx/conf.d/skillshare.conf` | 精确Host检查、真实Host转发，原TLS/ACL/upstream不变 |
| [补丁文件](../tooling/patches/skillshare-v0.25.13-trusted-origin.patch) | 可随工程维护的完整源码差异，非技能内容 |

服务drop-in设置：

```ini
Environment=SKILLSHARE_UI_TRUSTED_ORIGIN=https://fwd.seso.icu:34000
Environment=SKILLSHARE_UI_TRUSTED_PROXY=10.0.0.2
```

任一策略项未设置时新增域名分支关闭，保留原生规则。修改域名/端口/网关时必须联动应用策略、Nginx Host检查/转发、证书、后端防火墙和测试，不能仅增加DNS别名。

## 验证证据

- 基于官方commit `a7adb69e527c9f48eff154dce0b01c233da53004`，无新增Go依赖；在隔离任务容器内构建/测试，复用本机Go 1.26.3和已有镜像，不改生产容器。
- 原生守卫下，允许域名的回归用例先失败；补丁后正/负向策略、三类wrapper、原生localhost/IP、跨站、重复头与原有rebind测试通过。`go vet ./internal/server`、gofmt、源码context-router检查通过。没有宣称运行完整上游测试套件。
- 已通过真实TLS校验、真实Nginx Host转发的浏览器验收：MCP 3项、Hooks 8组、Plugins 9项；三页和API全部200。MCP/hooks只读POST预演也200且无阻塞；无JS错误或失败API请求，没有应用资源变更。
- 11个真实负向用例通过：错误Host/后缀/端口由Nginx关闭（444，对HTTP/1为空响应、HTTP/2为stream reset）；跨站GET/POST、错误/http/重复Origin、缺浏览器证明、伪造XFF的直接后端调用均拒绝。
- 全局Skillshare配置语义内容不变；验收期间出现了空行/段落排序规范化，未将其误报为逐字节一致。85份原生配置/技能文件快照保持；专属nft规则不变，原版CLI SHA仍为原校验值。没有修复或掩盖原有OfficeCLI嵌套重复及完整仓库测试失败。
- 服务enabled/active；仅原后端 `10.0.0.186:34000`，SSH14082及其他网关服务不变。没有主机重启演练。

浏览器测试采用定向内网解析到网关 `10.0.0.2`；不据此声称公网DNS/NAT链路已通，也未改DNS/hosts。

## 升级维护

不要点击Dashboard Restart/Upgrade，不混用 `skillshare ui start/stop`；仍由systemd管理。UI二进制及父目录root-owned，避免服务用户自更新覆盖本地白名单补丁。

升级官方CLI不会自动升级这个UI fork。若要升级UI：先保存当前配置、补丁和已验证artifact；在新上游版本重新检查安全守卫与三类消费者，审阅/rebase补丁；在隔离环境重跑正负测试、构建新UI版本和匹配的前端缓存，然后切换drop-in并重验。不能直接替换为上游二进制后假称白名单还有效。

本轮源码与构建证据保留在外置备份的 `source/`、`build-manifest.json`、`logs/`。补丁为普通unified diff，可在对应官方commit的干净源码上 `git apply --check` 后应用；需核对Go toolchain/go.sum和manifest，不执行远程安装脚本。构建命令核心为：

```sh
CGO_ENABLED=0 go build -trimpath \
  -ldflags '-s -w -X main.version=0.25.13+fwd1' \
  -o skillshare-ui ./cmd/skillshare
```

命令应在隔离构建容器中运行；前端资源版本需与发布路径、服务XDG缓存目录一致。补丁源码不是另一套技能Source。

## 备份与精准回退

- 本机：`/home/jacyl4/.local/state/skillshare-onboarding/domain-allowlist-20261017-223230`（0700）。
- 网关：`/var/backups/nginx/skillshare-domain-20261017-223230/skillshare-before.conf`。
- 本机含原unit、原/新Nginx、原资源配置、85文件内容摘要、原CLI SHA、源码、patch/build manifest、测试与浏览器证据。保留这些备份，不公开私有配置日志。

若需撤销本轮白名单：

1. 先保存任何后续改动；只移走本轮drop-in `domain-allowlist.conf` 到外置保留区，执行user `daemon-reload`与 `restart skillshare.service`，恢复原官方UI启动路径。不要覆盖整个unit目录或其他drop-in。
2. 对照本轮新配置确认没有其他管理员后续修改，再恢复网关这一份 `skillshare-before.conf`；`nginx -t`通过后reload。不要恢复整套Nginx、修改SSH或清空nft规则。
3. 核对官方CLI hash、service健康、原LAN/VPN和防火墙。此时域名下三类管理API恢复403，SSH localhost/IP原生访问仍可使用。
4. 新UI artifact/缓存先保留供审计，不自动删除；确认无需回退后才精确清理本版本，不动 `current` 或原release。

生产未做破坏性全量回滚演练；部署脚本在健康/正向API验证失败时具备恢复本轮drop-in与精确Nginx配置的路径，但本次未触发。
