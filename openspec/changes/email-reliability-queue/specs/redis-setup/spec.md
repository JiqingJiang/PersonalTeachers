## ADDED Requirements

### Requirement: Redis 一键安装
系统 MUST 提供 setup_redis.sh 脚本，在阿里云 ECS 上自动安装并优化 Redis。

#### Scenario: 首次安装 Redis
- **WHEN** 管理员在 ECS 上执行 `bash scripts/setup_redis.sh`
- **THEN** 脚本检测系统包管理器安装 Redis，写入 2G 内存优化配置（maxmemory=128mb, allkeys-lru, bind 127.0.0.1, requirepass）

#### Scenario: Redis 已存在
- **WHEN** 管理员再次执行 setup_redis.sh
- **THEN** 脚本 MUST 跳过安装，只检查 Redis 运行状态并打印信息

### Requirement: Redis 连接配置
Redis 连接信息 MUST 通过 .env 配置。

#### Scenario: 使用默认配置
- **WHEN** .env 未配置 REDIS_URL
- **THEN** 系统 MUST 使用默认值 `redis://:redis_password@localhost:6379/0`

#### Scenario: 自定义 Redis 配置
- **WHEN** 管理员在 .env 中设置 REDIS_URL
- **THEN** 系统 MUST 使用指定的 Redis 连接地址

### Requirement: 敏感信息不入代码
所有密码、地址等敏感信息 MUST 通过 .env 配置，代码中 MUST NOT 硬编码。

#### Scenario: Redis 密码
- **WHEN** 配置 Redis 连接
- **THEN** 密码 MUST 从 REDIS_URL 环境变量读取，代码和 README 中 MUST NOT 包含真实密码
