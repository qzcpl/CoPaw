/**
 * 队列相关类型定义
 * v4.0 新增 - 与后端 Python Schema 完全匹配
 */

/** 队列类型 */
export type QueueType = "redis" | "sqlite" | "memory";

/** 队列状态 */
export type QueueStatus = "active" | "paused" | "draining" | "error";

/** 消息状态 */
export type MessageStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | "dead_letter";

/**
 * 消息队列 - 与后端 MessageQueueResponse 完全匹配
 */
export interface MessageQueue {
  /** 队列 ID */
  queue_id: string;
  /** 队列名称 */
  queue_name: string;
  /** 队列类型 */
  queue_type: QueueType;
  /** 状态 */
  status: QueueStatus;
  /** 租户 ID */
  tenant_id: string;
  /** 配置 */
  config: QueueConfig;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
  /** 描述（可选） */
  description?: string;
}

/**
 * 队列配置 - 与后端 QueueConfig 完全匹配
 */
export interface QueueConfig {
  /** 最大容量 */
  max_size: number;
  /** 消息 TTL（秒） */
  message_ttl_sec: number;
  /** 可见性超时（秒） */
  visibility_timeout_sec: number;
  /** 最大重试次数 */
  max_retries: number;
  /** 重试间隔（秒） */
  retry_interval_sec: number;
  /** 死信队列 ID（可选） */
  dead_letter_queue_id?: string;
  /** 后端配置 */
  backend_config: Record<string, any>;
}

/**
 * 队列创建请求 - 与后端 MessageQueueCreateRequest 完全匹配
 */
export interface MessageQueueCreateRequest {
  /** 队列名称 */
  queue_name: string;
  /** 队列类型 */
  queue_type: QueueType;
  /** 配置 */
  config: QueueConfig;
  /** 描述（可选） */
  description?: string;
}

/**
 * 队列更新请求 - 与后端 MessageQueueUpdateRequest 完全匹配
 */
export interface MessageQueueUpdateRequest {
  /** 队列名称（可选） */
  queue_name?: string;
  /** 配置（可选） */
  config?: QueueConfig;
  /** 状态（可选） */
  status?: QueueStatus;
  /** 描述（可选） */
  description?: string;
}

/**
 * 队列消息 - 与后端 QueueMessageResponse 完全匹配
 */
export interface QueueMessage {
  /** 消息 ID */
  message_id: string;
  /** 队列 ID */
  queue_id: string;
  /** 消息内容 */
  body: Record<string, any>;
  /** 状态 */
  status: MessageStatus;
  /** 优先级（可选） */
  priority?: number;
  /** 创建时间 */
  created_at: string;
  /** 可见时间（可选） */
  visible_at?: string;
  /** 处理超时时间（可选） */
  processing_timeout_at?: string;
  /** 重试次数 */
  retry_count: number;
  /** 最后处理时间（可选） */
  processed_at?: string;
  /** 错误信息（可选） */
  error_message?: string;
  /** 元数据（可选） */
  metadata?: Record<string, any>;
}

/**
 * 队列统计 - 与后端 QueueStatsResponse 完全匹配
 */
export interface QueueStatsResponse {
  /** 队列 ID */
  queue_id: string;
  /** 总消息数 */
  total_messages: number;
  /** 待处理消息数 */
  pending_messages: number;
  /** 处理中消息数 */
  processing_messages: number;
  /** 完成消息数 */
  completed_messages: number;
  /** 失败消息数 */
  failed_messages: number;
  /** 死信消息数 */
  dead_letter_messages: number;
  /** 入队速率（条/秒） */
  enqueue_rate_per_sec: number;
  /** 出队速率（条/秒） */
  dequeue_rate_per_sec: number;
  /** 平均处理延迟（毫秒） */
  avg_processing_latency_ms: number;
  /** P95 处理延迟（毫秒） */
  p95_processing_latency_ms: number;
  /** P99 处理延迟（毫秒） */
  p99_processing_latency_ms: number;
  /** 消息数量（兼容旧代码） */
  message_count?: number;
  /** 最大容量（兼容旧代码） */
  max_size?: number;
}

/**
 * 队列深度历史 - 与后端 QueueDepthHistoryResponse 完全匹配
 */
export interface QueueDepthHistory {
  /** 队列 ID */
  queue_id: string;
  /** 时间范围开始 */
  start_time: string;
  /** 时间范围结束 */
  end_time: string;
  /** 数据点 */
  data_points: QueueDepthDataPoint[];
  /** 聚合间隔（秒） */
  aggregation_interval_sec: number;
}

/**
 * 队列深度数据点
 */
export interface QueueDepthDataPoint {
  /** 时间戳 */
  timestamp: string;
  /** 队列深度 */
  depth: number;
  /** 待处理数 */
  pending: number;
  /** 处理中数 */
  processing: number;
}

/**
 * 死信队列消息 - 与后端 DeadLetterMessageResponse 完全匹配
 */
export interface DeadLetterMessage {
  /** 消息 ID */
  message_id: string;
  /** 原始队列 ID */
  original_queue_id: string;
  /** 消息内容 */
  body: Record<string, any>;
  /** 失败原因 */
  failure_reason: string;
  /** 错误信息 */
  error_message: string;
  /** 重试次数 */
  retry_count: number;
  /** 创建时间 */
  created_at: string;
  /** 进入死信队列时间 */
  dead_lettered_at: string;
  /** 元数据（可选） */
  metadata?: Record<string, any>;
}

/**
 * 队列消费者 - 与后端 QueueConsumerResponse 完全匹配
 */
export interface QueueConsumer {
  /** 消费者 ID */
  consumer_id: string;
  /** 队列 ID */
  queue_id: string;
  /** 消费者名称 */
  consumer_name: string;
  /** 状态 */
  status: "active" | "inactive" | "paused";
  /** 最后心跳时间 */
  last_heartbeat: string;
  /** 已处理消息数 */
  messages_processed: number;
  /** 当前处理消息数 */
  messages_in_progress: number;
  /** 创建时间 */
  created_at: string;
  /** 配置（可选） */
  config?: Record<string, any>;
}

/**
 * 队列告警阈值 - 与后端 QueueAlertThresholdResponse 完全匹配
 */
export interface QueueAlertThreshold {
  /** 阈值 ID */
  threshold_id: string;
  /** 队列 ID */
  queue_id: string;
  /** 指标类型 */
  metric_type: "depth" | "latency" | "error_rate" | "backlog";
  /** 警告阈值 */
  warning_threshold: number;
  /** 严重阈值 */
  critical_threshold: number;
  /** 比较操作符 */
  operator: ">" | "<" | ">=" | "<=";
  /** 状态 */
  status: "active" | "inactive";
  /** 创建时间 */
  created_at: string;
}

/**
 * 队列优先级
 */
export enum QueuePriority {
  /** 最高优先级 */
  CRITICAL = 0,
  /** 高优先级 */
  HIGH = 1,
  /** 正常优先级 */
  NORMAL = 2,
  /** 低优先级 */
  LOW = 3,
  /** 最低优先级 */
  BACKGROUND = 4,
}

/**
 * 队列操作类型
 */
export enum QueueOperation {
  /** 入队 */
  ENQUEUE = "enqueue",
  /** 出队 */
  DEQUEUE = "dequeue",
  /** 确认 */
  ACK = "ack",
  /** 拒绝 */
  NACK = "nack",
  /** 重新入队 */
  REQUEUE = "requeue",
  /** 移动到死信队列 */
  MOVE_TO_DLQ = "move_to_dlq",
}

/**
 * 队列后端类型特性
 */
export interface QueueBackendFeatures {
  /** 后端类型 */
  backend_type: QueueType;
  /** 是否支持优先级队列 */
  supports_priority: boolean;
  /** 是否支持延迟队列 */
  supports_delay: boolean;
  /** 是否支持事务 */
  supports_transactions: boolean;
  /** 是否支持发布订阅 */
  supports_pubsub: boolean;
  /** 最大队列大小 */
  max_queue_size: number;
  /** 最大消息大小（字节） */
  max_message_size_bytes: number;
  /** 持久化支持 */
  persistence: "none" | "memory" | "disk" | "both";
}

/**
 * Redis 队列配置
 */
export interface RedisQueueConfig {
  /** Redis 主机 */
  host: string;
  /** Redis 端口 */
  port: number;
  /** Redis 密码（可选） */
  password?: string;
  /** Redis 数据库 */
  database: number;
  /** 键前缀 */
  key_prefix: string;
  /** 连接池大小 */
  pool_size: number;
  /** 连接超时（毫秒） */
  connection_timeout_ms: number;
  /** 是否启用 TLS */
  tls_enabled?: boolean;
}

/**
 * SQLite 队列配置
 */
export interface SqliteQueueConfig {
  /** 数据库文件路径 */
  database_path: string;
  /** 表名前缀 */
  table_prefix: string;
  /** 是否启用 WAL 模式 */
  wal_mode: boolean;
  /** 连接池大小 */
  pool_size: number;
  /** 繁忙超时（毫秒） */
  busy_timeout_ms: number;
}
