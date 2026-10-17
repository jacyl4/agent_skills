# 独立 Skills Source 布局（2026-10-17）

## 结果与边界

- Git 根：`/home/jacyl4/1base/GitLab/agent_skills`，分支、HEAD、remote 保持不变，没有提交或推送。
- 唯一 Skillshare Source：Git 根下的 `skills/`。保留七大分类及其细分目录，68 项名称不变。
- 工程维护：`tooling/scripts/` 和 `tooling/tests/`；仓库维护文档：`docs/`。完整树及日常命令见 [README](../README.md)。
- `skills/.skillignore` 随 Source 移动，当前零忽略规则；无需再用规则排除维护目录。
- Skillshare 全局配置和 Hermes `skills.external_dirs` 都改为新 Source。没有新增第二个 Git 仓库；`git_root` 不是任意文件路径字段，未改成绝对路径。
- 保护同步脚本与校验器默认定位仓库 `skills/`，不依赖调用工作目录；校验器仍可显式接收测试路径。
- 两个 Target 共136条受管链接精确切换；9条外部插件链接及其他工具自管目录不动。没有使用强制同步。
- 来源标记及技能中的安装路径同步更新；talk-normal 的 Hermes 发现说明改成实际采用的 `external_dirs`。其余技能文件内容和权限逐项保持。
- UI 在切换期间停止，完成保护同步后由既有 user systemd 恢复。端口34000、Nginx、TLS、ACL和后端防火墙未修改。

## 验证

- 新增两项回归测试先验证失败，再迁移实现；现25项通过。
- 626个技能文件按迁移前快照校验：只允许精确绝对路径与上述发现说明变化，权限保持。
- 校验器输出68项；保护同步应用后再次预演；两个 Target 各68条正确链接，外部链接保持。
- Codex 新 app-server 的 `skills/list` 强制刷新：68/68 名称和新 Source 路径正确，无发现错误。
- Hermes 新进程逐项 `skill_view`：68/68 成功且指向新 Source。既有长会话是否自动刷新不作保证，必要时开新会话。
- HTTPS经网关实测 Dashboard、Skills、Targets、Sync；技能页68项，无前端异常。域名访问 MCP/Plugins/Hooks 的预期403守卫保持。
- 安全审计逐项扫描68项、scanErrors=0；仍有5项CRITICAL发现和34项HIGH发现，与迁移前基线一致。审计退出码1为风险门禁，不是全绿，未关闭规则。
- `doctor` 确认 Source 68项；维护目录伪技能警告消失。未提交Git变更和未安装可选built-in skill的提醒保留，不为消警告做自动提交或安装。
- 账号授权、真实模型调用缺口与域名公网解析限制沿用原验收边界，见[部署记录](deployment-2026-10-17.md)和[反代记录](skillshare-resident-proxy.md)。发现/读取验证不等于所有Agent模型调用完成。

## 外置备份与针对性回退

备份目录（0700）：`/home/jacyl4/.local/state/skillshare-onboarding/source-layout-20261017-173200`。

- `repository-before/`：迁移前完整仓库快照，包含此前尚未提交的施工成果。
- `skillshare-config-before.yaml`、`hermes-config-before.yaml`：原配置；Hermes配置可能含凭据，不上传、不公开。
- `targets/`、`targets-before.json`：两侧原目录快照与原始链接文本。
- `inventory-before.json`、`source-files-before.json`、`source-changes.json`：68项、文件摘要/权限和精确修改记录。
- `logs/`：红/绿测试、同步、doctor、Agent发现、审计及浏览器证据。

回退只针对这次目录分层，不撤销此前的技能归并：

1. 停UI与同步；另备份当前源、配置、manifest及所有后续用户修改。
2. 核对上述备份与当前文件。仅将本次七个分类从 `skills/` 精确移回仓库根，将 `tooling/scripts/`、`tooling/tests/` 移回原位；任何同名冲突先停下，不覆盖。恢复对应脚本和精确路径改动时须保留后续编辑。
3. 恢复旧Source配置和Hermes的对应一项路径，不无差别覆盖整个配置。把 `.skillignore` 移回并恢复旧内容。
4. 只对仍为本次目标的136条受管链接按快照恢复原链接文本；不覆盖真实目录、外部链接或新目标；同步恢复对应manifest。
5. 重跑旧布局校验和链接核对，最后启动UI。没有完成验收前不要运行同步。

不复制旧 `.git` 覆盖当前仓库，不使用 `reset --hard`、`clean` 或整目录恢复覆盖。生产未执行破坏性全量回退演练。
