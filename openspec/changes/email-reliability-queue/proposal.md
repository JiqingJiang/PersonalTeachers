## Why

当前推送流程存在两个可靠性缺陷：（1）推送中途进程崩溃，未处理的用户当天彻底错过推送；（2）邮件发送失败 3 次后标记 failed，无自动重试。需要引入任务队列保证消息推送的可靠投递。

## What Changes

- 引入 Redis + RQ 作为推送任务队列
- 推送调度器改为往队列投递任务，不再直接执行推送
- 新增 RQ Worker 进程独立消费队列任务
- 失败任务自动重试（指数退避，最多 3 次）
- 补全 email_send_logs.error_message 字段的写入
- 所有凭证通过 .env 配置，代码不含硬编码敏感信息

## Capabilities

### New Capabilities
- `push-queue`: Redis RQ 推送任务队列，解耦调度与执行，支持崩溃恢复和失败重试
- `redis-setup`: Redis 安装与 2G 服务器优化配置

### Modified Capabilities

## Impact

- **新增依赖**: redis, rq
- **新增进程**: RQ Worker（与 FastAPI 并列运行）
- **部署变更**: 需安装 Redis，新增 worker systemd 服务
- **代码影响**: push_scheduler.py 改为入队模式，新增 push_queue.py、push_worker.py、worker.py
- **配置变更**: .env 新增 REDIS_URL
- **无影响**: 前端、admin、数据库模型、API 路由
