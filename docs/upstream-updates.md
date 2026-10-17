# GitHub 来源关联与单项升级

> 当前补充：OfficeCLI 已改为同一提交的真实 `skills/officecli` 子目录，避免整仓库嵌套重复；新增58项本地技能暂不猜测GitHub来源。当前126项及验证见[归集记录](skill-collection.md)。下表为原关联轮次的历史统计。

## 当前关联结果（2026-10-17）

本轮只补全 Skillshare 原生来源元数据，没有升级任何技能，也没有改变分类、名称或内容。

| GitHub 上游 | 可原生检查/升级数量 |
|---|---:|
| [Cloudflare Skills](https://github.com/cloudflare/skills) | 10 |
| [Taste Skill](https://github.com/Leonxlnx/taste-skill) | 13 |
| [GSAP Skills](https://github.com/greensock/gsap-skills) | 8 |
| [Ponytail](https://github.com/dietrichgebert/ponytail) | 6 |
| [OfficeCLI](https://github.com/iOfficeAI/OfficeCLI) | 11 |
| [Caveman / Cavecrew](https://github.com/JuliusBrussee/caveman) | 7 |
| **合计** | **55** |

每项均已从 GitHub 远程 HEAD 验证真实 `SKILL.md` 路径和 frontmatter 名称；不是根据技能正文的任意产品链接猜测。绑定保存在唯一 Source 的 **`skills/.metadata.json`**，这是 v0.25.13 的原生集中式元数据，不是自建更新器。Skillshare 页面可显示 GitHub 来源并检查/更新。

逐项来源、导入基线、远程验证、差异与策略见 [upstream-sources.json](upstream-sources.json)。这是**本轮关联时的历史证据**，不替代以后由 Skillshare 更新的原生元数据。升级后应按实际变化维护该记录。本次关联时间仅记在独立记录的 `recorded_at`，不冒充首次安装时间；原生元数据未填无法统一核实的 `installed_at`。

### 仍保留本地管理的13项

- **10项没有足够来源证据**：crawl4ai、qweb-bridge、scrapling、paraspeech、honker-sqlite-event-engine、browser-first-frontend-engineering、computer-first-performance-engineering、karpathy、schematic、deslop-zh。不随意绑定同名仓库。
- **2项为本地包装**：graphify、talk-normal。虽然有相关 GitHub 产品仓库，当前技能分别包含本地工具集成与 Hermes SOUL 维护约定，不能用产品仓库内容覆盖。
- **1项上游路径已删除**：sandbox-sdk。Cloudflare 当前已改为 `sandbox-stable`、`sandbox-next`、`sandbox-migrate-to-next` 等独立技能，名称和流程不同。本轮不替用户改名、选稳定/预览版或迁移工作流；旧技能完整保留，来源记录保留原 GitHub repo。

## 在 Skillshare 中使用

1. 打开现有 Dashboard 的 **Skills** 页面，打开具体技能，可查看 GitHub 来源链接。
2. 使用 **Check / Check Updates** 检查上游；本轮原生 CLI 实测55项可检查，47项提示可更新、8项为最新。该数字会随上游变化。
3. 升级前先保存该技能目录和 `skills/.metadata.json`，查看本地修改及上游改动，再对**单个技能**执行 Update。不要把本轮来源关联当作“批量升级已审核”。
4. 升级后运行下列校验与保护同步；如新增字段不兼容，先复核规范化，不要删除未知内容来强行过检。打开 Agent 新会话验收。

CLI 等价方式（在仓库根执行）：

```bash
# 只检查，不改技能内容
skillshare check -g --json
skillshare check -g frontend/animation/gsap-core
# 预演，不下载新内容供逐文件diff，不代表新版本已通过兼容性验证
skillshare update -g frontend/animation/gsap-core --dry-run
# 先完成外置备份与变更审核，才执行实际单项更新
skillshare update -g frontend/animation/gsap-core --diff

PYTHON=/home/jacyl4/.hermes/hermes-agent/.venv/bin/python
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" tooling/scripts/validate_skills.py
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -m unittest discover -s tooling/tests
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" tooling/scripts/sync_skills.py
# 审核同步预演后
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" tooling/scripts/sync_skills.py --apply
```

**命名注意**：此版本的 `check/update` 实测使用 Source 相对路径（如 `frontend/animation/gsap-core`），不是 UI/API 的 `frontend__animation__gsap-core`，也不是一概使用叶名称。审计命令与 list 显示可能采用另一种 ID，不要跨命令盲目复用。

## 必须了解的覆盖边界

**普通 GitHub 技能 Update 是重新安装并替换整个技能目录，不会合并或保护本地修改，即使不加 `--force`。** 只有独立 tracked Git repo 的 pull 有 dirty 保护。不要把仓库根的 Git dirty 状态当成普通技能更新保护。

- 本轮没有执行 `update --all`、实际 Update、`--force` 或 `--skip-audit`，没有关闭任何审计规则。
- 普通升级可能删除旧的隐藏来源标记；以后以原生 `.metadata.json` 和独立来源证据记录为准，不依赖这些旧标记。
- **officecli** 的本地 frontmatter 增加了 Hermes tags / related_skills。
- **ponytail** 将 `argument-hint` 移到 `metadata.argument-hint`；**cloudflare** 和 **turnstile-spin** 将 `references` 移到 `metadata.references`。这三项存在本地 schema 规范化，升级后可能需要重新应用；不要无条件用旧补丁覆盖新的上游字段。
- 其他已知导入基线的44项，其 `SKILL.md` 与基线一致；这不代表所有附件或最新上游内容与本地一致。
- Caveman / Cavecrew 七项没有可核实的原始导入 commit，故不伪造版本；目前会提示可更新，需人工审阅后首次更新建立正式版本。
- 已知条目的 `version` 是真实导入基线的7位短SHA，`commit` 是完整SHA；不是当前远程HEAD，也不是本地内容等于上游的证明。`file_hashes` 记录本轮采纳的本地字节基线；原生远程 Check 不以它检测本地修改。
- 本轮保守省略 `tree_hash`。因此同一上游仓库的其他提交也可能引起“可更新”提示；这是保守提示，不是逐文件差异结论。
- 关联后的68项审计为5条CRITICAL、35条HIGH，scanErrors=0，非安全全绿。相比此前新增1条 `publisher-mismatch` HIGH：`cloudflare-one-migrations` 文案提到迁移来源 Zscaler ZIA，审计器将它误认作发布者，与已验证的官方 `cloudflare/skills` 来源发生“发布者不符”。这是补齐来源后显现的元数据告警，技能内容未改；不关闭规则。
- 升级审计可能因这些 HIGH/CRITICAL 能力告警阻止更新；应逐项复核，不直接强制或跳过审计。
- 不自动更新 Graphify/Talk-normal 的本地包装，也不运行它们引用的安装器、SOUL 修改或其他技能动作。

以上覆盖行为已由固定版本源码和隔离沙箱验证：[官方集中元数据](https://github.com/runkids/skillshare/blob/v0.25.13/internal/install/metadata.go)、[普通技能更新实现](https://github.com/runkids/skillshare/blob/v0.25.13/internal/install/install_update.go)。

## 备份与回退本轮关联

本轮外置备份：`/home/jacyl4/.local/state/skillshare-onboarding/upstream-links-20261017-174049`（0700）。包含原技能626个文件、docs/tooling快照、Git状态、候选元数据、来源证据、GitHub远程SKILL缓存及check/dry-run/测试日志。

若仅撤销本轮来源关联，先停UI与其他写入，另存当前元数据及后续更新，再核对本轮候选。只在确认没有后续安装/更新后移走本轮新建的 `skills/.metadata.json`；存在后续变更时逐条删除本轮条目，不整体覆盖。原技能内容本轮未修改，不需要恢复整个Source或Git。最后启动既有user systemd服务。

这不是实际技能升级后的完整回退方案：升级后需恢复对应技能的外置快照及当时元数据条目，并重跑校验、同步和Agent发现。不要恢复旧 `.git`、无差别覆盖所有目录或执行 `reset --hard/clean`。
