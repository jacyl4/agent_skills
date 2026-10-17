# 本机 Agent 技能归集（2026-10-18）

> 后续路由修复：全部8项仍登记，但Universal是共享目录唯一写入方，5个工具改为共享读取；最新审计与风险接受见[日志和审计记录](audit-review.md)。下文逐Target写入数量为归集时快照，不代表应该重复开启写入。

## 结果和单一主源

主源仍是本仓库 `skills/`，实际为 **126 项全局不重名技能**：

- 原主源 68 项：正文逐份校验，未被各 Agent 的副本覆盖。
- 共享目录 35 个独立技能目录：共 36 项（github-workflows 内还包含独立 gh 技能）。
- Hermes 22 项不属于自带/WebUI/Hub 注册所有权的本地技能。
- 共迁移 57 个原目录；完整附件和可执行权限保留。旧目录原件进入私有备份，原路径改为指向主源的链接。
- Hermes 导入项保留正文，只补 `metadata.targets: [hermes]`，避免把 Hermes 专属工具约定分发给其他 Agent；目录名采用原 frontmatter 的 canonical name，例如 audiocraft-audio-generation。
- 已完成受保护的 skills-only 预演及同步，没有 `--force`、`--all` 或实际技能升级。

网页 Skills / API 显示126项；8个已登记 Target 均为 In sync：Hermes126项，其他7个104项。Codex/Universal/Zed共享同一目录，统计不代表保存了三份副本。Universal 保持可见、已登记。

分类：automation13、data1、documents11、engineering38、frontend28、platforms32、writing3。

逐目录来源、原始/归集后 SHA、目标限定见 [归集清单](skill-collection.json)。它是本轮导入证据，不是另一个更新器，也不伪造 GitHub 来源或导入提交。新增58项没有足够已验证的远程来源，先按本地技能管理。

## 原渠道维护的例外

这些不是遗漏，不能通过复制缓存和抢占所有权来“统一”：

- Codex `.system`、OMX 原生工作流；
- Codex 插件缓存、Understand Anything 插件提供的外部技能；
- Hermes `.bundled_manifest`、`.webui-managed-skills.json`、`.hub/lock.json` 已登记内容及未安装的 optional catalog；
- agy builtin 与各 Agent 原生系统资源。

它们继续由对应安装器/插件生命周期维护，没有改变原生信任、审批、插件启停或所有权清单。以后若要接管，需单独解除原渠道更新所有权；不要直接把 symlink 接到主源后继续让原安装器覆盖。

## 修复的前置问题

1. **OfficeCLI 嵌套重复**：此前更新把整个 Git repo 放进 officecli 技能目录，引入11份嵌套重名 SKILL。现将完整 repo 原样保留在外置备份，主源 officecli 仅保留该提交真实 `skills/officecli` 技能负载。它只有 SKILL.md，且与原根 SKILL 字节一致。原生元数据改为该子目录，同一真实提交 `fb98e593612dee2cec36847666671dba502e60aa`；其他10项文档技能不改。后续 OfficeCLI 单项更新不会再安装整个仓库。
2. **共享目标误拦截**：保护同步入口允许完全相同的目标路径别名，但仍拒绝嵌套路径、源/目标重叠、非merge/standard及未托管冲突。
3. **元数据测试漂移**：保留真实版本/提交，仅统一 repo URL 的可选.git拼写、OfficeCLI来源粒度和本地SHA。测试逐项检查正确类型，不再错误要求每个清单必须同时存在整仓库与子目录两种类型。

OfficeCLI SKILL 正文、原68项正文、原MCP/hooks/plugin定义不变。没有用历史快照覆盖用户已升级技能。

## 维护

- 用 Skillshare 页面管理 Source；新增/移动/筛选后运行 `tooling/scripts/sync_skills.py` 预演，再以 `--apply` 应用。
- `tooling/scripts/collect_local_skills.py` 提供有摘要校验的复制原语，不是自动全盘搜集器：拒绝覆盖、变化的原件、链接/特殊文件和目标范围冲突。不会执行技能正文或安装脚本。
- 本轮先根据所有权清单筛选，审查凭据类文件名及私钥，再暂存；原路径替换前再次核对原件和主源摘要。以后不要绕过这些人工审核阶段直接递归导入所有 Agent/插件缓存。
- 导入技能在 Skillshare 可见不等于已通过安全认证，也不保证既有 Agent 进程立即刷新；建议开新会话使用。

## 验证和已知风险

- 43项工具测试全部通过，主源126项唯一名称校验通过；基线原有56个失败已消除，未关闭重复名、命名、路径或冲突检查。
- 57组归集后负载、57组隔离原件摘要一致；原68项正文逐字节不变。全局Skillshare配置语义不变。
- 真实HTTPS反代浏览器检查 Skills/Targets 一致为126、无冲突，8个Target均同步；移除的旧工具仍不出现在候选中。
- MCP3、Hooks8、Plugins9的网页/API及只读预演正常；11个既有安全拒绝场景通过。
- 原生静态审计非全绿：133个扫描单元（含分类/聚合），10条CRITICAL、125条HIGH，scanErrors=0，审计退出1。包括create-skill/godmode等既有高权限或提示注入型说明；未执行其内容、放宽审计规则或跳过阻断。归集不代表推荐激活这些高风险能力。
- 原生同步提示技能按需上下文总量超过默认预算；这是可用技能集合估算，不是宣称每轮都加载全部正文。需要时按Target筛选，不能通过删内容或降低审计阈值消除告警。
- Python语法和定向/完整工具测试已做；没有启动所有Agent交互会话或运行技能内脚本，没有新增依赖。

## 备份与精准回退

本轮私有目录（0700）：
`~/.local/state/skillshare-onboarding/skills-collection-20261017-232228/`，
指针为仓库忽略的 `.omx/plans/skills-collection-backup-path`。

保留 `source-before-swap/`（含完整OfficeCLI checkout）、`skills-before/`、`quarantine/`、`native-migration-map.json`、`target-before/`、原配置/tooling/docs以及测试、同步、审计和浏览器证据。

回退前保存后续修改并暂停本UI写入。只按本轮映射检查链接身份后逐项恢复原件，恢复受影响的原Target链接/manifest和Source；不要恢复整个HOME、覆盖其他Target的本地内容或git reset/clean。若以后有新增技能或用户编辑，先做逐项三方比较，不直接整目录回滚。源切换后先校验，再启动服务。

自动施工脚本仅在本轮失败时使用精确快照回退；不要把一次性apply.py当作幂等更新命令重复执行。
