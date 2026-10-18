# 日志、原生审计与共享写入修复（2026-10-18）

后续澄清：审计页旧版“Blocked from sync”是误导性文案，普通同步没有该阻断；已修正提示并实测同步。安装／更新审核和风险记录保留，见[审计提示与同步放行](audit-sync-label.md)。下文“原生阻断”指安装／更新阈值，不代表技能不能同步。

## 检查结论

- user systemd 服务正常，最新部署后没有崩溃/重启风暴；Nginx配置测试通过。操作日志中的最新同步为成功、0个失败Target。
- 历史OfficeCLI的11个重名告警已由主源规范化解决，不删除历史日志来“修复”。
- Source126项、8个Target登记保持，MCP3、Hooks8、Plugins9保持；50项工具测试通过，真实HTTPS共享路由与安全负向用例验收通过。
- 原Doctor有4个warning、0error：Git未提交、共享路径多写入、跨运行时重复发现、可选内建skill缺失。前两类实际重复已修复，Git待本轮提交收尾。内建Skillshare skill缺失不妨碍服务；没有为消除提示而盲目安装或在分类Source中伪造根目录条目。

## 共享目录单一写入方

现在直接同步技能的只有：

| Target | 写入位置/作用 |
|---|---|
| universal | `~/.agents/skills`，104项通用技能的唯一写入方 |
| antigravity-cli | CLI专属路径，104项 |
| hermes | Hermes路径，126项，含22项专用技能 |

Codex、Zed、Cursor、Grok、OpenCode保留登记，但设 `skills.enabled: false`，由Universal共享目录读取。**网页“Skills off”表示停掉重复写入，不是Agent不能使用技能。** API中这五项均有 `skillsReadFrom: [universal]`。原生Agent/MCP/hooks/plugin管理不受影响。

原生命令先dry-run；共享路径guard保留实际共享目录；Cursor/Grok/OpenCode仅移除各自104个Source链接，没有删除其他本地文件、插件外部链接或Source。Doctor的shared_target_paths和cross_target_discovery均恢复pass，且无同步漂移、坏链接或重名。

维护时不要因看到Skills off就把所有Target重新开启。若某工具未来改变发现规则，再独立核验；本轮按固定版本配置中的已知runtime scan paths及真实API检查，没有启动所有Agent交互会话。

## 原生审计，不绕过规则

真实HTTPS网页Audit共扫描126项：57通过、66warning、3failed；5条CRITICAL、64条HIGH，scanErrors=0。详见[逐条CRITICAL记录](audit-review.json)。

- **create-skill**：`references/api-security.md:10` 的curl示例在明确标注的 BAD/反面教学段，使用环境变量和example.com；不是硬编码真实密钥或实际外传。保留文档，不通过改写示例躲避正则。
- **cloudflare**：smart-placement两处curl发送到官方 `api.cloudflare.com`，Authorization使用环境变量；属于合法API示例被通用外传规则命中。
- **godmode**：包括提示注入/安全绕过的实质能力，**按用户明确要求保留**，不伪装误报；其CRITICAL、HIGH及原生阻断保持。归集或Git提交不等于建议执行这些脚本或授权其降低其他Agent安全设置。

HIGH中的“hardcoded-secret”三处经核查分别为环境变量名和统一x占位Token；Git候选文件的常见Token/私钥模式检查无真实密钥命中。其他exec、shell、网络安装和跨技能能力告警仍应按任务审查，不将全体HIGH统称为误报。

没有降低阈值、关闭规则、增加audit ignore、改动godmode内容或执行任何技能内动作。最终审计仍是风险非绿，这是有意保留的真实状态。

CLI全局audit会额外扫描分类/聚合项，因此此前日志中的133单元/10条CRITICAL/125条HIGH不应当成独立技能数量；本页使用Web去重后的126项统计。没有为统一统计而修改官方CLI。

## 上下文预算

原生提示的350K/558K是所有按需正文之和，不代表每轮全量加载。Hermes的常驻技能索引约11.5K，超过默认10K告警线，应留意实际上下文开销；本轮未为清零提示而抬高阈值，也未擅自删除用户技能。后续可按任务/Agent筛选，不影响当前同步正确性。

## Git和回退边界

Git只包含分类Source、维护脚本、测试、补丁与文档，不包含原生配置、凭据、日志、私有隔离区或运行状态。推送前检查无嵌套Git目录、越界链接、大文件和Token/私钥；远端fetch后确认无分叉，以正常fast-forward push同步，禁止force/reset/clean。

本轮备份指针 `.omx/plans/audit-repair-backup-path` 指向私有目录，含原配置、完整Git bundle、Target链接映射/manifest及诊断证据。若撤销共享路由，先保存后续修改，恢复单一配置快照和受影响的Source链接，预演同步后应用；不要恢复整套HOME或覆盖MCP/hooks/plugin后续变更。Git提交回退应另做revert，不重写远端历史。

维护脚本/文档的Git whitespace检查通过；28个上游技能文件保留原有空白格式，未为通过格式检查改写正文/附件或破坏上游摘要。统一diff补丁的上下文行需要保留前导空格与tab，单独以gitattributes声明，不改补丁字节。

发布前另修复许可证/NOTICE遗漏，补回114份真实声明并新增声明遗失/篡改/路径回归与原生基线一致性测试，详见[声明保留](third-party-notices.md)。原审计结果未伪装全绿，godmode继续按用户要求保留。
