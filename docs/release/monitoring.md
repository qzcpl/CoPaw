# 监控指标

**文档版本：** v1.0  
**创建日期：** 2026-03-31  
**负责人：** 陈总  
**状态：** 待执行

---

## 1. 监控概述

### 1.1 监控目标

- 实时掌握系统运行状态
- 快速发现和定位问题
- 评估系统性能和容量
- 支持决策和优化

### 1.2 监控层次

```
┌─────────────────────────────────────┐
│           业务监控层                 │
│  (用户数、消息量、成功率)            │
├─────────────────────────────────────┤
│           应用监控层                 │
│  (QPS、延迟、错误率)                 │
├─────────────────────────────────────┤
│           资源监控层                 │
│  (CPU、内存、磁盘、网络)             │
├─────────────────────────────────────┤
│           基础设施层                 │
│  (服务器、网络、存储)                │
└─────────────────────────────────────┘
```

---

## 2. 核心指标

### 2.1 消息处理指标

| 指标名称 | 描述 | 类型 | 单位 | 采集频率 |
|----------|------|------|------|----------|
| message_total | 消息总数 | Counter | 条 | 10 秒 |
| message_success | 成功处理消息数 | Counter | 条 | 10 秒 |
| message_failed | 失败消息数 | Counter | 条 | 10 秒 |
| message_timeout | 超时消息数 | Counter | 条 | 10 秒 |
| success_rate | 成功率 | Gauge | % | 1 分钟 |
| failure_rate | 失败率 | Gauge | % | 1 分钟 |

**计算公式：**
```
success_rate = message_success / message_total * 100
failure_rate = message_failed / message_total * 100
```

**告警阈值：**

| 指标 | 警告 | 严重 |
|------|------|------|
| success_rate | < 98% | < 95% |
| failure_rate | > 2% | > 5% |

---

### 2.2 性能指标

| 指标名称 | 描述 | 类型 | 单位 | 采集频率 |
|----------|------|------|------|----------|
| response_time | 响应时间 | Histogram | ms | 10 秒 |
| response_time_p50 | P50 响应时间 | Gauge | ms | 1 分钟 |
| response_time_p95 | P95 响应时间 | Gauge | ms | 1 分钟 |
| response_time_p99 | P99 响应时间 | Gauge | ms | 1 分钟 |
| qps | 每秒查询数 | Gauge | 次/秒 | 10 秒 |
| queue_size | 队列积压数 | Gauge | 条 | 10 秒 |

**告警阈值：**

| 指标 | 警告 | 严重 |
|------|------|------|
| response_time_p95 | > 3000ms | > 10000ms |
| qps | < 100 | < 50 |
| queue_size | > 500 | > 1000 |

---

### 2.3 路由指标

| 指标名称 | 描述 | 类型 | 单位 | 采集频率 |
|----------|------|------|------|----------|
| routing_total | 路由总数 | Counter | 次 | 10 秒 |
| routing_cache_hit | 缓存命中数 | Counter | 次 | 10 秒 |
| routing_cache_miss | 缓存未命中数 | Counter | 次 | 10 秒 |
| cache_hit_rate | 缓存命中率 | Gauge | % | 1 分钟 |
| routing_latency | 路由延迟 | Histogram | ms | 10 秒 |

**计算公式：**
```
cache_hit_rate = routing_cache_hit / routing_total * 100
```

**告警阈值：**

| 指标 | 警告 | 严重 |
|------|------|------|
| cache_hit_rate | < 80% | < 50% |
| routing_latency_p95 | > 10ms | > 50ms |

---

### 2.4 会话穿透指标

| 指标名称 | 描述 | 类型 | 单位 | 采集频率 |
|----------|------|------|------|----------|
| session_build_total | 会话构建总数 | Counter | 次 | 10 秒 |
| session_build_latency | 会话构建延迟 | Histogram | ms | 10 秒 |
| profile_load_total | 画像加载总数 | Counter | 次 | 10 秒 |
| profile_load_latency | 画像加载延迟 | Histogram | ms | 10 秒 |
| group_context_load_total | 群聊上下文加载数 | Counter | 次 | 10 秒 |

**告警阈值：**

| 指标 | 警告 | 严重 |
|------|------|------|
| session_build_latency_p95 | > 100ms | > 500ms |
| profile_load_latency_p95 | > 200ms | > 1000ms |

---

## 3. 资源指标

### 3.1 服务器资源

| 指标名称 | 描述 | 类型 | 单位 | 采集频率 |
|----------|------|------|------|----------|
| cpu_usage | CPU 使用率 | Gauge | % | 10 秒 |
| memory_usage | 内存使用率 | Gauge | % | 10 秒 |
| disk_usage | 磁盘使用率 | Gauge | % | 1 分钟 |
| network_in | 网络流入 | Gauge | KB/s | 10 秒 |
| network_out | 网络流出 | Gauge | KB/s | 10 秒 |

**告警阈值：**

| 指标 | 警告 | 严重 |
|------|------|------|
| cpu_usage | > 70% | > 90% |
| memory_usage | > 70% | > 90% |
| disk_usage | > 80% | > 95% |

---

### 3.2 Redis 资源

| 指标名称 | 描述 | 类型 | 单位 | 采集频率 |
|----------|------|------|------|----------|
| redis_memory_usage | Redis 内存使用 | Gauge | MB | 10 秒 |
| redis_connected_clients | 连接数 | Gauge | 个 | 10 秒 |
| redis_ops_per_sec | 每秒操作数 | Gauge | 次 | 10 秒 |
| redis_keyspace_hits | 键空间命中 | Counter | 次 | 10 秒 |
| redis_keyspace_misses | 键空间未命中 | Counter | 次 | 10 秒 |

**告警阈值：**

| 指标 | 警告 | 严重 |
|------|------|------|
| redis_memory_usage | > 80% | > 95% |
| redis_connected_clients | > 80% | > 95% |

---

### 3.3 数据库资源

| 指标名称 | 描述 | 类型 | 单位 | 采集频率 |
|----------|------|------|------|----------|
| db_connections | 连接数 | Gauge | 个 | 10 秒 |
| db_queries_per_sec | 每秒查询数 | Gauge | 次 | 10 秒 |
| db_slow_queries | 慢查询数 | Counter | 次 | 1 分钟 |
| db_lock_waits | 锁等待数 | Counter | 次 | 1 分钟 |

**告警阈值：**

| 指标 | 警告 | 严重 |
|------|------|------|
| db_connections | > 80% | > 95% |
| db_slow_queries | > 10/分钟 | > 50/分钟 |

---

## 4. 业务指标

### 4.1 用户指标

| 指标名称 | 描述 | 类型 | 单位 | 采集频率 |
|----------|------|------|------|----------|
| active_users | 活跃用户数 | Gauge | 人 | 5 分钟 |
| new_users | 新增用户数 | Counter | 人 | 1 小时 |
| user_retention | 用户留存率 | Gauge | % | 1 天 |

**告警阈值：**

| 指标 | 警告 | 严重 |
|------|------|------|
| active_users (同比) | -30% | -50% |

---

### 4.2 频道指标

| 指标名称 | 描述 | 类型 | 单位 | 采集频率 |
|----------|------|------|------|----------|
| channel_messages | 各频道消息数 | Counter | 条 | 10 秒 |
| channel_users | 各频道用户数 | Gauge | 人 | 5 分钟 |
| channel_errors | 各频道错误数 | Counter | 次 | 10 秒 |

---

### 4.3 Agent 指标

| 指标名称 | 描述 | 类型 | 单位 | 采集频率 |
|----------|------|------|------|----------|
| agent_load | Agent 负载 | Gauge | % | 1 分钟 |
| agent_active_sessions | 活跃会话数 | Gauge | 个 | 1 分钟 |
| agent_messages | 处理消息数 | Counter | 条 | 10 秒 |

---

## 5. 告警配置

### 5.1 告警级别

| 级别 | 名称 | 响应时间 | 通知渠道 |
|------|------|----------|----------|
| P0 | CRITICAL | 5 分钟 | 电话 + 短信 + 钉钉 |
| P1 | ERROR | 30 分钟 | 短信 + 钉钉 |
| P2 | WARNING | 2 小时 | 钉钉 |
| P3 | INFO | 24 小时 | 邮件 |

### 5.2 告警规则

**P0 级别告警：**

```yaml
- alert: ServiceDown
  expr: up{job="copaw"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "服务不可用"
    description: "CoPaw 服务已宕机"

- alert: SuccessRateLow
  expr: success_rate < 90
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "成功率过低"
    description: "消息处理成功率低于 90%"
```

**P1 级别告警：**

```yaml
- alert: HighLatency
  expr: response_time_p95 > 10000
  for: 5m
  labels:
    severity: error
  annotations:
    summary: "延迟过高"
    description: "P95 响应时间超过 10 秒"

- alert: QueueBacklog
  expr: queue_size > 1000
  for: 5m
  labels:
    severity: error
  annotations:
    summary: "队列积压"
    description: "队列积压超过 1000 条"
```

**P2 级别告警：**

```yaml
- alert: HighCPU
  expr: cpu_usage > 70
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "CPU 使用率高"
    description: "CPU 使用率超过 70%"

- alert: HighMemory
  expr: memory_usage > 70
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "内存使用率高"
    description: "内存使用率超过 70%"
```

---

## 6. 监控大盘

### 6.1 核心大盘

**系统概览：**
- 消息处理成功率
- 平均响应时间
- 活跃用户数
- 队列积压数

**性能分析：**
- QPS 趋势
- 响应时间分布（P50/P95/P99）
- 路由延迟
- 会话构建延迟

**资源监控：**
- CPU/内存使用率
- Redis 状态
- 数据库状态
- 网络流量

### 6.2 业务大盘

**频道分析：**
- 各频道消息量
- 各频道用户数
- 各频道错误率

**Agent 分析：**
- Agent 负载分布
- Agent 会话数
- Agent 消息处理量

---

## 7. 日志监控

### 7.1 日志级别

| 级别 | 描述 | 示例 |
|------|------|------|
| ERROR | 错误日志 | 消息处理失败 |
| WARN | 警告日志 | 重试、降级 |
| INFO | 信息日志 | 请求处理 |
| DEBUG | 调试日志 | 详细流程 |

### 7.2 关键日志

**错误日志：**
```
ERROR [MessageProcessor] Failed to process message: msg_001
ERROR [Router] No agent found for call_id: 400-001
ERROR [Queue] Failed to enqueue message: queue full
```

**警告日志：**
```
WARN [MessageProcessor] Message timeout: msg_001
WARN [Router] Fallback to default agent
WARN [Queue] Queue size exceeds threshold: 500
```

---

## 8. 附录

### 8.1 监控工具

- **指标采集：** Prometheus
- **日志收集：** ELK Stack
- **告警通知：** AlertManager + 钉钉
- **大盘展示：** Grafana
- **链路追踪：** Jaeger

### 8.2 相关文档

- [灰度发布计划](./canary-release-plan.md)
- [全量上线计划](./launch-plan.md)
- [回滚方案](./rollback-plan.md)

---

**维护：**

| 角色 | 姓名 | 日期 |
|------|------|------|
| 创建人 | 陈总 | 2026-03-31 |
| 审核人 | | |
| 更新人 | | |
