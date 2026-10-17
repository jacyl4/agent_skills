# 本机部署验收（2026-10-16 开始，2026-10-17 收尾）

> 本报告记录初次接入验收，文中源路径与映射属于历史状态。后续唯一 Source 已调整为仓库 `skills/`，见[布局迁移](source-layout-2026-10-17.md)。后续已追加持久化和34000反代；当前运行入口与网络边界见[最新运维记录](skillshare-resident-proxy.md)。下表中的临时localhost入口/未自启描述是初次交付时的历史状态。

## 结果

Skillshare v0.25.13 已部署；当前 GitLab 仓库是自维护 Skills 主源。68项全局唯一、目录/name一致；两个 Target 各有68条正确主源链接。没有重新克隆、迁移Git根、修改remote、自动提交或push，也没有第二套Git同步任务。

- 程序和操作方法：[运维手册](skillshare-operations.md)。
- 原48项分类映射、20项导入来源及原件摘要：[迁移记录](layout-migration.json)。
- 外置完整证据/备份：`/home/jacyl4/.local/state/skillshare-onboarding/20261016-201504`。
- 源分支 `main`，HEAD `280cf3d2e27b71d9cf155184e8a0d6af6398116e`，remote保持施工前值；地址不在报告重复公开。
- 当前工作区有预期的目录移动、归并、新文档和校验工具变更，**尚未提交**。Git未暂存时会把移动显示为删除+未跟踪；不代表原内容丢失。

## 源整理与清理

- 原48项按用途分类；叶目录使用既有frontmatter调用名，修复10项旧目录/name不一致。
- 从共享目录和Codex目录归并20个独立bundle：7项沟通技能、11项Office/Morph、Graphify、ParaSpeech。
- 原有469个文件逐项核对内容和权限；除精确安装路径/来源标记更新，以及schematic日期加引号外保持原内容。日期修复来自实际Hermes读取失败：裸YAML日期被解析成date对象，JSON序列化失败；已加回归测试。
- 对20项导入先完整复制和校验文件/权限，再替换消费端。没有执行第三方Skill脚本或安装器。
- 实际Hermes调用发现12个本地副本和external主源重名，officecli/paraspeech调用失败。已隔离副本，保留ParaSpeech本机部署说明及规则放置附件、Graphify本机review和runtime配置checklist、OfficeCLI的Hermes元数据，确认原有四项命令说明完整保留且没有重复。重新验证68项均可从主源读取。
- 旧Pi Skills和旧Antigravity IDE Skills已外置隔离；安装中的GSD和agy CLI使用不同的有效消费路径。保留Pi AGENTS、历史、认证和其他父目录文件。
- 原有系统/OMX/GSD/插件内容不纳管，不为清理数字删除有效独立技能。未发现Claude/OpenCode/Droid对应目录，未创建无效Target。
- 目录删除仅有一个经确认已空的root-owned旧IDE容器；其他被替代内容均进入quarantine，保留逐项恢复清单。

## 验证证据

| 项目 | 结果 |
|---|---|
| 版本与安装包 | v0.25.13，官方SHA256校验通过，安装文件与解包文件hash一致 |
| Source结构 | 68个唯一name，description/YAML/目录一致性及JSON兼容校验通过 |
| 回归测试 | 23项通过；新增日期与同步冲突保护测试均有RED→GREEN证据 |
| 原始文件 | 469项内容/权限核对通过，Git HEAD/分支/remote不变 |
| 受控分发 | 2 Targets × 68 = 136条链接全部指向正确源路径 |
| 幂等性 | 沙箱重复真实sync语义一致；生产第二次dry-run updated=0、pruned=0 |
| 独立XDG沙箱 | standard/flat、targets、include/exclude、启停恢复、人工链接纳管、local保护、移名/删除及精确恢复通过 |
| Codex发现 | 新App Server重扫，68个主源name全部发现，无解析错误 |
| Codex实际调用 | 新的ephemeral只读会话读取主源karpathy，并按最小变更/验证原则作答 |
| Hermes实际读取 | 新Python进程逐项skill_view 68项均成功，路径均为主源，重名已消除 |
| Dashboard | 浏览器检查List/Cards/Tree、分类、详情、Targets/Sync/Audit/Settings；无页面JS错误；截图留存 |
| UI监听 | 仅127.0.0.1:19420，未开放公网；未设自启 |
| 静态检查 | 维护脚本与测试Python语法解析通过，git diff --check通过；无独立lint/typecheck/build配置，没有伪报这些门禁已运行 |

原生sync JSON的 `linked=136` 表示已正确关联总数，不等于第二次又创建136条；幂等判断同时检查链接目标、目录状态和manifest的managed内容，不比较每次都会变的updated_at时间戳。

## 未通过或未覆盖的验收

- **agy实际调用：待重新授权。** CLI会话在30秒授权窗口后退出；后来收到的旧授权码未提交到新流程，也未写入仓库/本报告。此项不能写成调用通过。专用目标链接136项中的对应68项已独立验证。
- **Grok实际调用：未登录。** 只读新会话返回Not signed in；未新增凭据或替用户开启认证。官方对应版本代码及本机binary确认其读取共享`.agents/skills`；旧的单独qweb链接已隔离，避免重复。
- **Cursor与GSD新会话模型调用：未做。** 路径已据官方资料和安装代码核验；不把路径检查等同交互调用。施工期间另一进程执行npm update，Codex/GSD入口曾暂时消失后恢复，GSD从1.3.0变为1.22.0。没有中断或回退该更新；对更新后GSD内部私有模块的直接导入探针失败，不足以判断正常CLI是否故障，亦未扩展为GSD修复任务。
- 生产回退未实际执行；恢复仅在沙箱演练，完整备份与逐项映射已交付。

## 安全和非阻塞告警

最终精确审计扫描68项：**5 CRITICAL、34 HIGH**，退出码1，scanErrors=0。并非安全全绿。经独立逐项复核，没有阻塞本次被动归并/分发的发现；真实能力仍需在后续调用时守住权限边界。

- 原有21项高危/严重命中：10项语义误报，11项为预期网络、凭据或动态执行能力。
- 导入新增17 HIGH：3项误报，其余为Office远程安装、文档写入和Caveman可选外部模型调用等真实能力。未新增CRITICAL。
- 合并ParaSpeech本机说明后新增1 HIGH：`sudo systemctl restart paraspeech`服务重启能力；只是按需运维说明，本次没有执行服务重启。
- 不能通过关规则、提高阈值、删有效技能来制造绿色结果。OfficeCLI已有安装，不执行文档里的pipe-to-shell；变量URL上的凭据请求必须先确认host；压缩私人文档到外部模型须明确要求。
- doctor退出0，但保留Git未提交、维护目录不是Skill、可选built-in管理skill未安装等告警。没有为消除告警创建伪Skill或执行upgrade --skill。
- Skillshare估算Codex描述常驻约10.4K token，超过其10K提示预算；按需技能总量不代表每次全部加载。本次不为压低数字重写技能行为，后续可单独讨论筛选/精简。

## 交付边界

本机主源、程序、配置、受控链接、GUI和保护工具已可用；不等于所有Agent账号级调用均已通过。下一项需要用户参与的是重新完成agy授权；Grok需要有效登录，Cursor/GSD可另做交互验收。原始部署指引保留未覆盖，后续以本仓库运维手册和实测记录为准。
