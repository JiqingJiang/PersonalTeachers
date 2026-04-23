## Context

PersonalTeachers v2 当前推送流程：APScheduler 定时触发 → push_scheduler 直接并发调 push_for_user() → 生成语录 → 发邮件。两个可靠性问题：（1）进程崩溃则未处理用户当天错过推送；（2）邮件失败无自动重试。服务器 2 核 2G，需控制额外中间件内存占用。

## Goals / Non-Goals

**Goals:**
- 推送任务持久化到 Redis，崩溃不丢
- 失败任务自动重试（指数退避，最多 3 次）
- 解耦调度与执行，FastAPI 和 Worker 独立运行
- 所有敏感信息通过 .env 配置

**Non-Goals:**
- 不引入 Kafka/RocketMQ（2G 服务器无法承载）
- 不改造前端和 admin
- 不修改数据库模型结构（error_message 字段已存在）

## Decisions

### D1: Redis + RQ 而非 SQLite 队列
**选择**: 使用 Redis 作为消息队列后端，RQ 作为任务队列库。
**理由**: RQ 是 Python 生态最成熟的轻量任务队列，API 简洁（enqueue/retry/worker），比自建 SQLite 队列更可靠（Redis 有 AOF 持久化，RQ 有内置重试）。Redis 占用 ~50-80MB，2G 服务器可承受。

### D2: 任务只传 user_id
**选择**: 入队时只传 user_id，Worker 内部查库。
**理由**: 避免入队快照数据过期。用户可能在排队期间修改了关键词偏好、推送时间等，Worker 实时查库保证使用最新数据。

### D3: 单队列 push_queue
**选择**: 只用一个队列，不区分优先级。
**理由**: 当前只有一种任务类型（推送），没必要搞多队列复杂度。

### D4: Worker 独立进程
**选择**: Worker 和 FastAPI 分别运行，各自 systemd 服务。
**理由**: 彻底解耦。FastAPI 崩溃不影响推送，Worker 崩溃不影响 API。各自重启互不干扰。

## Risks / Trade-offs

- **[风险] Redis 未开启 AOF 则重启丢数据** → 接受此风险，下次调度周期会重新入队（last_push_date 机制兜底），setup_redis.sh 默认开启 AOF
- **[风险] 2G 服务器多一个进程** → Redis ~50-80MB + Worker ~100MB，总计 ~700MB，可控
- **[取舍] RQ 不支持定时重试** → 使用 interval 列表模拟指数退避，够用
