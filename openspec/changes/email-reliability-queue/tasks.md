## 1. 依赖与配置

- [ ] 1.1 requirements.txt: 新增 redis、rq
- [ ] 1.2 config.py: 新增 REDIS_URL 配置项

## 2. Redis 安装脚本

- [ ] 2.1 创建 scripts/setup_redis.sh: 检测包管理器安装 Redis
- [ ] 2.2 setup_redis.sh: 写入 2G 内存优化配置并设置密码
- [ ] 2.3 setup_redis.sh: 幂等处理——已安装时跳过

## 3. 推送队列

- [ ] 3.1 创建 backend/app/services/push_queue.py: 封装 RQ 入队逻辑
- [ ] 3.2 创建 backend/app/services/push_worker.py: Worker 消费逻辑（生成语录+发邮件+重试+写 error_message）
- [ ] 3.3 创建 backend/worker.py: RQ Worker 启动入口
- [ ] 3.4 改造 push_scheduler.py: _push_for_time_slot 改为入队模式

## 4. 文档

- [ ] 4.1 更新 README: 新增 Redis 安装、RQ Worker 启动、所有可配置环境变量说明

## 5. 验证

- [ ] 5.1 本地安装 Redis，启动 Worker，验证入队+消费+重试流程
