---
name: honker-sqlite-event-engine
description: 设计 Honker + SQLite 轻量级事件驱动引擎，用于 SQLite-first 任务队列、事件流、事务内异步任务、本地 Agent 工作流任务总线、调度、锁、重试和死信处理。
metadata:
  trigger: SQLite 任务队列, Honker, 事件驱动, 本地任务总线, SQLite-first, 事务内异步任务, 后台任务队列, 轻量消息队列, 定时任务, 死信队列
---

# Honker + SQLite 轻量级事件驱动引擎 Skill

## 1. Skill 定位

本 Skill 用于指导 AI Agent、开发者或自动化工具，将 **Honker + SQLite** 组合设计成一个轻量级事件驱动引擎。

它适合用于：

- 单机应用的后台任务队列
- SQLite-first 应用的事务内异步任务
- 本地 Agent 工作流任务总线
- 文件索引、相册缩略图、知识库解析等后台任务
- 小型 SaaS / 桌面应用 / 边缘节点的本地事件内核
- Hermes / Codex / OpenClaw 等工具链的后台执行层

一句话：

> Honker 让 SQLite 不只是数据库，更像一个内嵌式事件驱动引擎。

---

## 2. 触发条件

当用户提出以下需求时，应优先考虑本 Skill：

- “我想用 SQLite 做任务队列”
- “我不想额外部署 Redis / RabbitMQ”
- “业务写入和异步任务要在同一个事务里”
- “本地 Agent 需要一个任务总线”
- “文件扫描后异步解析、索引、生成缩略图”
- “小型系统需要事件驱动，但不想上复杂消息队列”
- “想把 app.db 同时作为数据库、队列、事件流和调度器”
- “Hermes/Codex/OpenClaw 需要一个轻量后台执行层”

---

## 3. 核心设计思想

Honker + SQLite 的核心思想是：

```text
业务数据
任务队列
事件流
通知信号
定时任务
锁
重试状态
死信状态

全部收敛到同一个 SQLite 文件中。
```

典型结构：

```text
Application / Agent / CLI
        |
        v
SQLite app.db
        |
        +-- 业务表
        |     +-- orders
        |     +-- users
        |     +-- photos
        |     +-- files
        |
        +-- Honker 内部表
              +-- queues
              +-- streams
              +-- scheduler
              +-- offsets
              +-- locks
              +-- retry / dead-letter
```

最大的价值是：

```text
BEGIN
  写业务数据
  enqueue / publish / notify
COMMIT
```

业务数据写入和任务入队可以在同一个事务中完成。

这意味着：

- 提交一起成功
- 回滚一起消失
- 不需要业务库和 Redis 之间的双写补偿
- 可以自然实现 transaction outbox / queue 一体化

---

## 4. 架构原则

### 4.1 SQLite 是状态机中心

在此模式下，SQLite 不只是数据存储，而是整个系统的状态机核心。

应该把以下状态尽量收敛到同一个 `.db`：

- 业务对象状态
- 后台任务状态
- 任务重试状态
- 事件流 offset
- 定时任务触发状态
- 处理结果状态
- Worker 心跳与租约状态

### 4.2 Honker 是事件驱动层

Honker 负责：

- Queue：任务队列
- Stream：可重放事件流
- Notify / Listen：瞬时通知
- Scheduler：定时任务
- Named Lock：命名锁
- Retry / DLQ：失败重试与死信
- Rate Limit：限速控制

### 4.3 不引入独立 Broker

默认不引入：

- Redis
- RabbitMQ
- Kafka
- NATS
- Celery Broker
- Temporal Server

除非系统已经明确进入多机分布式、高吞吐、强 HA 或复杂工作流场景。

### 4.4 单机优先

Honker + SQLite 最适合：

```text
single machine
single writer
local-first
small-to-medium workload
```

不要把 SQLite `.db` 放到 NFS 上让多台机器共同写入。

---

## 5. 模式选择

### 5.1 Queue：任务队列

用于需要可靠执行、ack、retry、DLQ 的异步任务。

适合：

- 发邮件
- Webhook 异步处理
- 图片缩略图生成
- 文件解析
- 索引更新
- Agent 调用 Codex / Playwright / qmd
- 后台数据清理

流程：

```text
enqueue -> claim -> process -> ack
                         |
                         +-> retry / backoff / DLQ
```

### 5.2 Stream：事件流

用于需要可重放、可追踪 offset 的事件流。

适合：

- 审计日志
- 状态广播
- Dashboard 增量刷新
- 前端实时状态
- Agent 任务事件
- 文件处理流水日志

流程：

```text
publish -> consumer offset -> resume
```

特点：

- consumer 有自己的 offset
- 掉线后可继续消费
- 适合 at-least-once 消费模型

### 5.3 Notify / Listen：瞬时通知

用于跨进程轻量唤醒。

适合：

- 本地 UI 刷新
- Worker 唤醒
- 轻量信号
- 非关键状态提示

特点：

- 在线时接收
- 离线不可重放
- 不适合关键任务状态

### 5.4 Scheduler：定时任务

适合：

- 每 N 分钟扫描目录
- 每小时清理过期任务
- 每日压缩索引
- 定期同步知识库
- 定时触发 Agent 巡检

---

## 6. 标准事件流转过程

推荐标准流程：

```text
1. 应用收到事件
2. 开启事务 BEGIN
3. 写入业务数据
4. 同事务调用 Honker：enqueue / publish / notify
5. COMMIT 成功
6. SQLite data_version 变化
7. Honker 唤醒 worker / subscriber
8. worker claim 任务
9. 执行业务处理
10. 成功 ack
11. 失败 retry / backoff / dead-letter
12. 发布 stream 更新状态
```

事务示例：

```sql
BEGIN;

INSERT INTO orders(user_id, amount, status)
VALUES (42, 199.00, 'created');

-- 伪代码：在同一事务内入队
enqueue('emails', {
  "to": "user@example.com",
  "subject": "订单确认",
  "body": "感谢您的购买"
});

COMMIT;
```

核心判断：

> 只要业务写入和任务入队不是同一事务，就要重新审视一致性风险。

---

## 7. Python 使用模板

### 7.1 安装

Debian 环境：

```bash
mkdir -p /opt/ai/honker-demo
cd /opt/ai/honker-demo

python3 -m venv .venv
source .venv/bin/activate

pip install -U pip
pip install honker
```

### 7.2 tasks.py

```python
import time
import honker

db = honker.open("/opt/ai/honker-demo/app.db")
queue = db.queue("default")


@queue.task(name="demo.echo", retries=3, timeout_s=30)
def echo(message: str) -> dict:
    print(f"worker got: {message}")
    return {
        "message": message,
        "processed_at": time.time(),
    }
```

### 7.3 enqueue.py

```python
from tasks import echo

result = echo("hello honker")
print("job enqueued")
print(result.get(timeout=10))
```

### 7.4 启动 Worker

```bash
cd /opt/ai/honker-demo
source .venv/bin/activate

python -m honker worker tasks:db --queue=default --concurrency=2
```

---

## 8. systemd 服务模板

路径：

```text
/etc/systemd/system/honker-worker.service
```

内容：

```ini
[Unit]
Description=Honker Worker
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/ai/honker-demo
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/ai/honker-demo/.venv/bin/python -m honker worker tasks:db --queue=default --concurrency=2
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

启用：

```bash
systemctl daemon-reload
systemctl enable --now honker-worker.service
systemctl status honker-worker.service
journalctl -u honker-worker.service -f
```

---

## 9. 推荐目录结构

适合统一部署到 `/opt/ai/`：

```text
/opt/ai/honker-engine/
├── app.db
├── .venv/
├── tasks.py
├── workers/
│   ├── codex_worker.py
│   ├── browser_worker.py
│   ├── index_worker.py
│   └── thumbnail_worker.py
├── producers/
│   ├── api_producer.py
│   ├── cli_producer.py
│   └── file_watcher.py
├── migrations/
│   └── 001_init.sql
├── scripts/
│   ├── start-worker.sh
│   ├── enqueue-demo.sh
│   └── inspect-db.sh
├── logs/
└── README.md
```

---

## 10. 与 Hermes / Codex / OpenClaw 的组合方式

### 10.1 推荐角色划分

```text
Hermes / OpenClaw
  负责接收任务、理解意图、写入任务队列

Honker + SQLite
  负责任务状态、事件流、调度、重试、锁

Codex / Browser / qmd / Indexer Worker
  负责实际执行工具调用

Web UI / Telegram / Discord
  负责展示任务进度与结果
```

### 10.2 推荐队列设计

```text
queues:
  codex_jobs
  browser_jobs
  index_jobs
  thumbnail_jobs
  notification_jobs
  maintenance_jobs

streams:
  task_events
  audit_events
  file_events
  agent_events

channels:
  ui_refresh
  worker_wakeup
  status_changed
```

### 10.3 Agent 任务模型

建议任务 payload：

```json
{
  "task_id": "uuid",
  "kind": "codex_patch",
  "input": {
    "repo": "/opt/projects/demo",
    "instruction": "根据文档修改代码"
  },
  "context": {
    "source": "hermes",
    "user": "local",
    "priority": "normal"
  }
}
```

任务状态表建议：

```sql
CREATE TABLE IF NOT EXISTS agent_tasks (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    input_json TEXT NOT NULL,
    result_json TEXT,
    error TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

状态建议：

```text
pending
claimed
running
succeeded
failed
retrying
dead_letter
cancelled
```

---

## 11. 相册系统落地模板

适合 Picot / 本地相册类应用。

### 11.1 事件流程

```text
图片上传 / 文件扫描
        |
        v
写入 photos 表
        |
        v
enqueue thumbnail_jobs
enqueue metadata_jobs
enqueue hash_jobs
        |
        v
worker 生成缩略图 / WebP / EXIF / hash
        |
        v
更新 photos 状态
        |
        v
publish photo_events
        |
        v
Web UI 增量刷新
```

### 11.2 推荐队列

```text
photo_import_jobs
thumbnail_jobs
metadata_jobs
webp_jobs
hash_jobs
album_index_jobs
```

### 11.3 推荐事件流

```text
photo_events
album_events
index_events
```

### 11.4 推荐状态字段

```sql
ALTER TABLE photos ADD COLUMN thumb_status TEXT DEFAULT 'pending';
ALTER TABLE photos ADD COLUMN metadata_status TEXT DEFAULT 'pending';
ALTER TABLE photos ADD COLUMN hash_status TEXT DEFAULT 'pending';
ALTER TABLE photos ADD COLUMN indexed_at TEXT;
```

---

## 12. 本地知识库落地模板

### 12.1 事件流程

```text
文件变更
  -> 写入 files 表
  -> enqueue parse_jobs
  -> 解析内容
  -> enqueue chunk_jobs
  -> 切分文本
  -> enqueue index_jobs
  -> 建立全文索引 / 向量索引
  -> publish knowledge_events
```

### 12.2 推荐队列

```text
file_scan_jobs
parse_jobs
chunk_jobs
index_jobs
embed_jobs
cleanup_jobs
```

### 12.3 推荐事件流

```text
knowledge_events
index_events
file_events
```

---

## 13. 轻量 SaaS 落地模板

### 13.1 典型场景

```text
用户注册
订单创建
付款成功
Webhook 接收
文件上传
报表生成
邮件通知
```

### 13.2 推荐流程

```text
HTTP Request
  -> BEGIN
  -> 写业务表
  -> enqueue 后台任务
  -> publish 业务事件
  -> COMMIT
  -> 立即返回用户
  -> Worker 异步处理
```

### 13.3 推荐队列

```text
email_jobs
webhook_jobs
report_jobs
billing_jobs
notification_jobs
```

---

## 14. 数据库与事务设计规则

### 14.1 任务入队必须尽量靠近业务写入

推荐：

```text
BEGIN
  INSERT business row
  enqueue job
COMMIT
```

避免：

```text
INSERT business row
COMMIT

enqueue job
```

后者存在业务写入成功但任务入队失败的问题。

### 14.2 Worker 必须幂等

因为队列一般应按 at-least-once 语义设计，Worker 可能重复执行。

Worker 侧必须做到：

- 根据 task_id 去重
- 处理前检查状态
- 结果写入使用 upsert 或状态机约束
- 外部副作用要有幂等键

### 14.3 任务状态要显式

不要只依赖队列内部状态。

业务系统应维护自己的任务状态表：

```text
pending -> running -> succeeded
                  -> failed
                  -> retrying
                  -> dead_letter
```

### 14.4 重要事件使用 Stream，不要用 Notify

如果事件不能丢，用 Stream。

如果只是 UI 刷新信号，可以用 Notify。

---

## 15. 可观测性清单

落地时必须考虑：

- 当前 pending job 数量
- running job 数量
- retrying job 数量
- dead-letter 数量
- 每个 queue 的处理耗时
- 最近失败原因
- worker 心跳
- stream consumer offset
- scheduler 最近触发时间
- SQLite 文件大小
- WAL 文件大小
- checkpoint 情况

建议提供 CLI：

```bash
./scripts/inspect-db.sh
./scripts/list-queues.sh
./scripts/list-failed-jobs.sh
./scripts/retry-dead-letter.sh
```

---

## 16. SQLite 配置建议

一般建议启用 WAL：

```sql
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA foreign_keys=ON;
PRAGMA busy_timeout=5000;
```

说明：

- WAL 更适合读多写少的并发场景
- `synchronous=NORMAL` 在很多本地应用中是性能与安全的折中
- `busy_timeout` 可以减少短暂锁竞争导致的失败
- 不要为了性能盲目关闭同步，除非可以接受数据丢失

---

## 17. 边界与禁忌

### 17.1 不要多机共写同一个 SQLite 文件

禁止：

```text
Node A ----\
            NFS ---- app.db
Node B ----/
```

风险：

- 文件锁不可靠
- 写入冲突
- 数据损坏
- 任务重复或丢失

### 17.2 不要把它当 Kafka

Honker + SQLite 不适合：

- 大规模日志流
- 海量吞吐
- 多分区 consumer group
- 长期海量事件留存
- 跨数据中心复制

### 17.3 不要把它当 RabbitMQ

不适合：

- 复杂路由
- topic exchange
- fanout exchange
- 多租户 broker
- 跨语言大规模微服务队列

### 17.4 不要把它当 Temporal

不适合：

- 长时间 workflow
- 人工审批流
- 多步骤 DAG
- chain/group/chord
- 复杂补偿事务

### 17.5 Alpha 阶段需谨慎

如果项目仍处于 Alpha，应先用于：

- 内部工具
- 低风险任务
- 可重跑任务
- 本地 Agent
- 开发者工具链
- 非核心生产链路

---

## 18. 选型判断表

| 问题 | 是 | 否 |
|---|---|---|
| 主数据库就是 SQLite？ | 优先考虑 Honker | 继续判断 |
| 只需要单机任务队列？ | 适合 Honker | 继续判断 |
| 需要事务内 outbox？ | 很适合 Honker | 可用 Redis/RQ |
| 要多台机器共同消费？ | 谨慎，通常不适合 | 适合 |
| 要高吞吐事件流？ | 用 Kafka / Redpanda | Honker 可试 |
| 要复杂 workflow？ | 用 Temporal / LangGraph | Honker 可作底层队列 |
| 不想额外部署 broker？ | Honker 很合适 | Redis/RabbitMQ 可接受 |
| 任务可重复执行、可补偿？ | 适合试用 | 谨慎 |

---

## 19. 回答用户时的推荐结构

当用户询问 Honker + SQLite 事件驱动设计时，建议按以下结构回答：

```text
1. 结论
2. 适合 / 不适合场景
3. 核心架构图或文字架构
4. 事务内事件流转
5. Queue / Stream / Notify 的选择
6. Debian 部署方式
7. systemd worker
8. 业务场景落地示例
9. 风险边界
10. 下一步实施清单
```

---

## 20. 最小可落地方案

### 20.1 目标

在 `/opt/ai/honker-engine` 部署一个本地事件驱动引擎。

### 20.2 命令

```bash
mkdir -p /opt/ai/honker-engine
cd /opt/ai/honker-engine

python3 -m venv .venv
source .venv/bin/activate

pip install -U pip
pip install honker
```

### 20.3 建立 tasks.py

```python
import honker
import time

db = honker.open("/opt/ai/honker-engine/app.db")
q = db.queue("default")


@q.task(name="engine.echo", retries=3, timeout_s=30)
def echo(message: str) -> dict:
    return {
        "message": message,
        "time": time.time(),
    }
```

### 20.4 建立 enqueue.py

```python
from tasks import echo

r = echo("hello from honker engine")
print(r.get(timeout=10))
```

### 20.5 运行

终端 1：

```bash
cd /opt/ai/honker-engine
source .venv/bin/activate
python -m honker worker tasks:db --queue=default --concurrency=2
```

终端 2：

```bash
cd /opt/ai/honker-engine
source .venv/bin/activate
python enqueue.py
```

---

## 21. 设计判断口诀

```text
单机、SQLite、本地任务、事务一致性：
  用 Honker。

多机、高吞吐、强 HA、复杂路由：
  不要硬上 Honker。

业务写入与任务入队必须同生共死：
  Honker 是好刀。

需要跨集群消息平台：
  换 Kafka / RabbitMQ / Redis / Postgres 队列。
```

---

## 22. 推荐总结

Honker + SQLite 的最佳定位：

```text
本地任务总线
轻量事件内核
SQLite-first 应用后台执行层
Agent 工作流执行队列
单机 outbox / queue 一体化方案
```

不要把它吹成分布式消息系统。

它真正锋利的地方是：

> 在一个 SQLite 文件里，用事务把业务状态、异步任务和事件流焊死在一起。
