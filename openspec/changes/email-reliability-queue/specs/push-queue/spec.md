## ADDED Requirements

### Requirement: 推送任务入队
PushScheduler MUST 将推送任务投递到 Redis Queue，而非直接执行推送。

#### Scenario: 正常入队
- **WHEN** 推送时间到达，调度器查询到 N 个需要推送的用户
- **THEN** 调度器 MUST 为每个用户创建一个 RQ Job（仅含 user_id），投递到 push_queue

#### Scenario: 任务只含 user_id
- **WHEN** 任务入队时
- **THEN** 任务负载 MUST 只包含 user_id，Worker 从数据库查询完整用户信息（避免快照数据过期）

### Requirement: Worker 消费推送任务
RQ Worker MUST 独立进程运行，消费 push_queue 中的任务并执行推送。

#### Scenario: 正常消费
- **WHEN** Worker 从队列取到任务
- **THEN** Worker MUST 查询用户信息 → 生成语录 → 发送邮件 → 更新 last_push_date → 写入发送日志

#### Scenario: 任务超时
- **WHEN** 单个任务执行超过 120 秒
- **THEN** RQ MUST 将该任务标记为 failed，Worker 继续消费下一个任务

### Requirement: 失败自动重试
失败任务 MUST 自动重试，采用指数退避策略。

#### Scenario: 邮件发送失败重试
- **WHEN** 任务因邮件发送失败而失败
- **THEN** RQ MUST 自动重试，间隔依次为 60 秒、300 秒、900 秒，最多 3 次

#### Scenario: LLM API 不可用重试
- **WHEN** 任务因 LLM API 全部不可用而失败
- **THEN** RQ MUST 按相同策略自动重试

#### Scenario: 重试耗尽最终失败
- **WHEN** 任务重试 3 次后仍失败
- **THEN** 任务 MUST 标记为最终 failed，error_message MUST 写入 email_send_logs 表

### Requirement: 崩溃恢复
进程崩溃后未完成的任务 MUST 不丢失。

#### Scenario: FastAPI 崩溃
- **WHEN** FastAPI 进程崩溃但 RQ Worker 仍在运行
- **THEN** Worker MUST 继续消费队列中已有的任务

#### Scenario: Worker 崩溃
- **WHEN** RQ Worker 进程崩溃
- **THEN** 重启 Worker 后 MUST 自动继续消费未完成的任务（Redis 持久化保证）

#### Scenario: Redis 重启
- **WHEN** Redis 服务重启（未开启 AOF 时队列任务丢失）
- **THEN** 下次调度周期到达时，调度器 MUST 重新为 last_push_date != today 的用户入队
