# Work Pets 删除失败处理（2026-10-18）

## 原因

网页在 09:45 的 `plugin remove` 和后续 `plugin sync` 均失败。复现发现 Skillshare 抹去了原生错误细节，只提示检查登录、信任或配置；实际 Codex 卸载请求返回 HTTP 403：`Installed-by-default plugins cannot be uninstalled`。

原生清单中 `work-pets@openai-curated-remote` 的 `installPolicy` 是 `INSTALLED_BY_DEFAULT`。这是远端安装策略，不是 Nginx、登录过期或本地文件权限错误。

## 已处理

- 备份 Skillshare/Codex 配置、原生清单和 Work Pets 缓存。
- 用原生命令确认拒绝原因，没有删除缓存、修改远端策略或伪造卸载状态。
- 经带 revision 的 Skillshare `plugin import` 重新认领既有安装，清掉失败遗留的 `pending: remove`。
- 再次预演 Work Pets 同步为 `noop`，不会继续重试失败的删除；9 个插件原生记录和 Codex 配置保持不变。
- 临时 `-c plugins."work-pets@openai-curated-remote".enabled=false` 探测未改变原生清单的 enabled 状态；没有将无效设置写入配置，更没有把 Skillshare 的同步选中开关冒充原生禁用。

**Work Pets 仍是已安装、启用状态；没有卸载成功或禁用成功。** 远端策略未改变前，重复点击删除仍会被拒绝，不应通过删缓存来规避。插件列表显示该项是如实反映原生状态。

私有备份及原始错误证据由 `.omx/plans/work-pets-remove-backup-path` 指向。不覆盖其他插件、MCP、hooks 或已有宠物数据。
