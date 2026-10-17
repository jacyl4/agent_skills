# Skillshare 持久化与 Nginx 反代

> 后续已追加精确域名白名单，当前MCP/Hooks/Plugins可通过既有域名访问；UI为独立0.25.13+fwd1补丁版，官方CLI不变。以[白名单记录](domain-allowlist.md)为准；下文有关三页403、固定Host和SSH必需的描述记录原始反代部署状态。

变更日期：2026-10-17。目标：本机长期运行，复用网关现有TLS反代样式。最终端口按用户追加指定为 **34000**。

当前 Git 根保持 `/home/jacyl4/1base/GitLab/agent_skills`；Skillshare 唯一 Source 为其 `skills/` 子目录。UI 使用全局配置读取该 Source，不修改服务工作目录或网络配置。

## 当前访问与安全边界

- 入口：`https://fwd.seso.icu:34000/`。
- Nginx网关：`10.0.0.2:34000`。
- 后端：`http://10.0.0.186:34000`；程序版本仍为v0.25.13。
- `14082` 实际是网关SSH端口，保留不动；未修改SSH配置，也未将其让给Nginx。
- 网关ACL：允许loopback、本机LAN `10.0.0.0/24`、现有WireGuard网络 `172.16.66.0/24`；其他来源403。当前无公网登录认证，不能把ACL等同用户身份认证。
- 后端nft独立表 `inet skillshare_ui` 只放行网关和本机源地址，不允许其他LAN机器绕过反代。没有改写Docker或其他主机规则。
- 使用现有网关TLS证书 `*.seso.icu` / `seso.icu`，本次未签发或复制私钥。

当前普通DNS把 `fwd.seso.icu` 解析到公网地址，普通域名34000连接尚未打通；本次HTTPS/浏览器验收使用定向内网解析到 `10.0.0.2`。内网使用该域名时，需要内网DNS或客户端hosts将它指向网关。没有擅自修改DNS、hosts或公网路由器映射；不能把内网验收宣称为公网已通。

前端访问范围未收到用户进一步选择时，采用已说明的安全默认：仅内网和既有VPN。如果需要公网，先增加认证并明确暴露范围，不直接移除ACL。

## 文件与生命周期

| 位置 | 用途 |
|---|---|
| `~/.config/systemd/user/skillshare.service` | 普通用户前台运行UI，全局配置，Restart=always/3秒 |
| `/etc/systemd/system/skillshare-ui-firewall.service` | root oneshot，加载专属表，开机启用 |
| `/etc/nftables.d/skillshare-ui.nft` | 只影响本机IPv4后端34000的入站访问 |
| `/run/skillshare-ui-firewall.ready` | root创建的启动保护标记，非持久数据 |
| `10.0.0.2:/etc/nginx/conf.d/skillshare.conf` | 新增独立TLS反代配置 |
| `10.0.0.2:/var/log/nginx/skillshare.{access,error}.log` | 网关请求和上游错误日志 |

Linger在变更前已为yes，未改变其他用户的驻留设置。user服务已enable；防火墙系统服务已enable并排在user@1000之前，Nginx原本已经开机启用。未重启主机做启动演练。

不要混用 `skillshare ui start/stop` 或Dashboard Restart/Upgrade；生命周期统一由systemd负责。原生UI后台实例已正常停止，旧19420不再监听。用户服务工作目录为HOME并显式传 `-g`，不会因为仓库cwd进入项目模式。

## 反代的关键项

- 沿用 `.ssl_certs`、`.HSTS` 和既有HTTP/2监听样式，HTTP误入该端口会转到同端口HTTPS。
- 明确转发 `Host: fwd.seso.icu:34000`，不能丢掉非标准端口，否则Origin校验不一致。
- `proxy_http_version 1.1`、`proxy_buffering off`，读超时3600秒，支持SSE。
- 保留实际客户端/Forwarded头。没有加通配CORS。
- 复用已有 `$connection_upgrade` map 保持代理样式兼容；Skillshare主要用SSE，不依赖WebSocket。
- 域名入口MCP/Plugins/Hooks仍按产品设计403；这不是代理配置失败。未改写应用代码或伪造localhost/IP绕过守卫。
- 此处使用固定Host；将来更换域名/端口时，需要一起更新server_name、Host/Forwarded相关字段和证书适配，并重新验证Origin行为。

完整的受保护页面可按需经已认证SSH隧道访问（不要放到后台常驻，使用完关闭）：

```bash
ssh -N -T -p 14082 -i /home/jacyl4/1base/@secure/id_rsa \
  -L 127.0.0.1:19420:10.0.0.186:34000 root@10.0.0.2
# 浏览器：http://localhost:19420
```

已临时验证localhost转发后的MCP接口200，测试隧道随后关闭；不会伪造反代Origin绕过域名守卫。

## 验证

已执行并留存：

1. `systemd-analyze --user verify`、root unit verify和 `nft -c` 均通过。
2. user服务 enabled/active；防火墙服务 enabled/active(exited)；Linger=yes。
3. 后端、本机到网关HTTPS、网关到后端均HTTP200；TLS校验未使用 `-k`。
4. 受控终止服务主进程后，systemd按策略自动拉起新PID，HTTPS恢复200；没有执行任何Skill脚本。
5. 非允许源地址的后端访问被拒绝；网关源地址访问后端200。
6. Nginx变更前后均 `nginx -t` 成功，只做reload，不restart；SSH14082一直可用。
7. `/api/health` 报v0.25.13，`/api/diff/stream` 返回discovering/start/done等SSE事件；域名 `/api/mcp` 返回预期403。
8. HTTPS浏览器Dashboard/Skills/Targets/Sync检查和截图见本次备份；页面JS无错误；MCP/Plugins/Hooks后台请求的预期403单独留存，不冒充零失败。

没有更改Skills内容、Agent目标配置、Git远程或自动同步任务。此次源仓库的变更仅为运维说明更新。

## 备份与精确回退

本机：`~/.local/state/skillshare-onboarding/resident-proxy-20261017-111520/`。
网关：`/var/backups/nginx/skillshare-20261017-111620/`（亦记录于网关 `skillshare-LATEST`）。

本机备份包含原配置、原运维文档、原防火墙ruleset只读快照、最终unit/nft/反代配置、验证日志与截图。不要把ruleset快照整体restore；它包含动态Docker规则。

回退按以下顺序，只处理本次文件：

1. `systemctl --user disable --now skillshare.service`，先停止后端，避免撤防后裸露。
2. 将网关新增 `skillshare.conf` 移到该次备份目录，`nginx -t` 后reload。不要还原整套Nginx目录、不要修改SSH14082。
3. 本机 `sudo systemctl disable --now skillshare-ui-firewall.service`，其ExecStop仅删除专属 `inet skillshare_ui` 表及ready标记。
4. 隔离本次新增unit及nft文件，分别daemon-reload。不要修改原有host/Docker规则或其他用户服务。
5. 如果恢复初次临时使用方式，确认34000实例已经停掉后，再按需运行 `skillshare ui start -g --host 127.0.0.1 --port 19420 --no-open`；原先没有持久service可恢复。

日常重启UI不需要停止防火墙。维护防火墙时先停UI，加载规则并确认ready标记后再启动；若管理员额外flush了全局ruleset，也按此顺序恢复保护。UI来源和配置不变，网络回退不需要回退Skills分类。
