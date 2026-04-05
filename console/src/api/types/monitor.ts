/**
 * 监控相关类型定义
 * v4.0 新增 - 与后端 Python Schema 完全匹配
 */

/** 指标类型 */
export type MetricType = "counter" | "gauge" | "histogram" | "summary";

/** 告警级别 */
export type AlertSeverity = "INFO" | "WARNING" | "ERROR" | "CRITICAL";

/** 告警状态 */
export type AlertStatus = "active" | "resolved" | "muted";

/** 告警渠道 */
export type AlertChannel = "LOG" | "EMAIL" | "DINGTALK" | "WEBHOOK";

/** 比较操作符 */
export type AlertOperator = ">" | "<" | ">=" | "<=" | "==" | "!=";

/**
 * 监控指标 - 与后端 MonitorMetricResponse 完全匹配
 */
export interface MonitorMetric {
  /** 指标 ID */
  metric_id: string;
  /** 指标名称 */
  metric_name: string;
  /** 指标类型 */
  metric_type: MetricType;
  /** 当前值 */
  value: number;
  /** 单位 */
  unit: string;
  /** 时间戳 */
  timestamp: string;
  /** 标签（可选） */
  labels?: Record<string, string>;
  /** 描述（可选） */
  description?: string;
}

/**
 * 指标历史数据点
 */
export interface MetricDataPoint {
  /** 时间戳 */
  timestamp: string;
  /** 值 */
  value: number;
  /** 标签（可选） */
  labels?: Record<string, string>;
}

/**
 * 指标历史记录 - 与后端 MonitorMetricHistoryResponse 完全匹配
 */
export interface MonitorMetricHistory {
  /** 指标 ID */
  metric_id: string;
  /** 指标名称 */
  metric_name: string;
  /** 时间范围开始 */
  start_time: string;
  /** 时间范围结束 */
  end_time: string;
  /** 数据点 */
  data_points: MetricDataPoint[];
  /** 聚合方式 */
  aggregation?: "avg" | "max" | "min" | "sum" | "count";
  /** 聚合间隔（秒） */
  aggregation_interval_sec?: number;
}

/**
 * 告警定义 - 与后端 MonitorAlertResponse 完全匹配
 */
export interface MonitorAlert {
  /** 告警 ID */
  alert_id: string;
  /** 告警名称 */
  alert_name: string;
  /** 指标 ID */
  metric_id: string;
  /** 阈值 */
  threshold: number;
  /** 比较操作符 */
  operator: AlertOperator;
  /** 告警级别 */
  severity: AlertSeverity;
  /** 状态 */
  status: AlertStatus;
  /** 通知渠道 */
  channels: AlertChannel[];
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
  /** 最后触发时间（可选） */
  triggered_at?: string;
  /** 最后解决时间（可选） */
  resolved_at?: string;
  /** 静默结束时间（可选） */
  muted_until?: string;
  /** 描述（可选） */
  description?: string;
  /** 通知配置（可选） */
  notification_config?: NotificationConfig;
}

/**
 * 告警创建请求 - 与后端 MonitorAlertCreateRequest 完全匹配
 */
export interface MonitorAlertCreateRequest {
  /** 告警名称 */
  alert_name: string;
  /** 指标 ID */
  metric_id: string;
  /** 阈值 */
  threshold: number;
  /** 比较操作符 */
  operator: AlertOperator;
  /** 告警级别 */
  severity: AlertSeverity;
  /** 通知渠道 */
  channels: AlertChannel[];
  /** 描述（可选） */
  description?: string;
  /** 通知配置（可选） */
  notification_config?: NotificationConfig;
}

/**
 * 告警更新请求 - 与后端 MonitorAlertUpdateRequest 完全匹配
 */
export interface MonitorAlertUpdateRequest {
  /** 告警名称（可选） */
  alert_name?: string;
  /** 阈值（可选） */
  threshold?: number;
  /** 比较操作符（可选） */
  operator?: AlertOperator;
  /** 告警级别（可选） */
  severity?: AlertSeverity;
  /** 通知渠道（可选） */
  channels?: AlertChannel[];
  /** 描述（可选） */
  description?: string;
  /** 通知配置（可选） */
  notification_config?: NotificationConfig;
}

/**
 * 通知配置
 */
export interface NotificationConfig {
  /** 邮件地址列表 */
  email_recipients?: string[];
  /** 钉钉 Webhook URL */
  dingtalk_webhook_url?: string;
  /** 自定义 Webhook URL */
  webhook_url?: string;
  /** 通知模板（可选） */
  template?: string;
  /** 通知频率限制（分钟） */
  rate_limit_minutes?: number;
}

/**
 * 告警触发记录 - 与后端 MonitorAlertTriggerResponse 完全匹配
 */
export interface MonitorAlertTrigger {
  /** 触发记录 ID */
  trigger_id: string;
  /** 告警 ID */
  alert_id: string;
  /** 触发时间 */
  triggered_at: string;
  /** 触发时指标值 */
  metric_value: number;
  /** 阈值 */
  threshold: number;
  /** 操作符 */
  operator: AlertOperator;
  /** 状态 */
  status: "fired" | "resolved" | "suppressed";
  /** 通知发送状态 */
  notifications_sent: boolean;
  /** 通知渠道列表 */
  notification_channels: AlertChannel[];
  /** 解决时间（可选） */
  resolved_at?: string;
}

/**
 * 系统健康状态 - 与后端 SystemHealthResponse 完全匹配
 */
export interface SystemHealthStatus {
  /** 整体健康状态 */
  overall_status: "healthy" | "degraded" | "unhealthy";
  /** 健康分数（0-100） */
  health_score: number;
  /** 组件状态 */
  components: ComponentHealthStatus[];
  /** 活跃告警数量 */
  active_alerts_count: number;
  /** 最后检查时间 */
  last_check_at: string;
  /** 问题列表 */
  issues: string[];
  /** 建议列表 */
  recommendations: string[];
}

/** 系统健康响应（兼容旧代码） */
export type SystemHealthResponse = SystemHealthStatus;

/**
 * 组件健康状态
 */
export interface ComponentHealthStatus {
  /** 组件名称 */
  component_name: string;
  /** 组件类型 */
  component_type: string;
  /** 状态 */
  status: "healthy" | "degraded" | "unhealthy";
  /** 健康分数（0-100） */
  health_score: number;
  /** 指标（可选） */
  metrics?: Record<string, number>;
  /** 问题列表 */
  issues: string[];
  /** 最后检查时间 */
  last_check_at: string;
}

/**
 * 监控仪表板 - 与后端 MonitorDashboardResponse 完全匹配
 */
export interface MonitorDashboard {
  /** 仪表板 ID */
  dashboard_id: string;
  /** 仪表板名称 */
  dashboard_name: string;
  /** 租户 ID */
  tenant_id: string;
  /** 布局配置 */
  layout: DashboardLayout;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
  /** 描述（可选） */
  description?: string;
}

/**
 * 仪表板布局
 */
export interface DashboardLayout {
  /** 网格列数 */
  grid_columns: number;
  /** 小部件列表 */
  widgets: DashboardWidget[];
}

/**
 * 仪表板小部件
 */
export interface DashboardWidget {
  /** 小部件 ID */
  widget_id: string;
  /** 小部件类型 */
  widget_type: "metric_card" | "chart" | "table" | "alert_list";
  /** 标题 */
  title: string;
  /** 位置 X */
  x: number;
  /** 位置 Y */
  y: number;
  /** 宽度 */
  width: number;
  /** 高度 */
  height: number;
  /** 配置 */
  config: Record<string, any>;
}

/**
 * 监控指标分类
 */
export enum MetricCategory {
  /** 系统指标 */
  SYSTEM = "system",
  /** 应用指标 */
  APPLICATION = "application",
  /** 业务指标 */
  BUSINESS = "business",
  /** 频道指标 */
  CHANNEL = "channel",
  /** 队列指标 */
  QUEUE = "queue",
  /** Agent 指标 */
  AGENT = "agent",
}

/**
 * 常用系统指标 ID
 */
export enum SystemMetricIds {
  /** CPU 使用率 */
  CPU_USAGE = "system.cpu.usage_percent",
  /** 内存使用率 */
  MEMORY_USAGE = "system.memory.usage_percent",
  /** 磁盘使用率 */
  DISK_USAGE = "system.disk.usage_percent",
  /** 网络入站带宽 */
  NETWORK_IN = "system.network.in_bytes_per_sec",
  /** 网络出站带宽 */
  NETWORK_OUT = "system.network.out_bytes_per_sec",
}

/**
 * 常用应用指标 ID
 */
export enum ApplicationMetricIds {
  /** 请求总数 */
  REQUEST_TOTAL = "app.http.requests_total",
  /** 请求延迟（P50） */
  REQUEST_LATENCY_P50 = "app.http.latency_p50_ms",
  /** 请求延迟（P95） */
  REQUEST_LATENCY_P95 = "app.http.latency_p95_ms",
  /** 请求延迟（P99） */
  REQUEST_LATENCY_P99 = "app.http.latency_p99_ms",
  /** 错误率 */
  ERROR_RATE = "app.http.error_rate_percent",
  /** 活跃连接数 */
  ACTIVE_CONNECTIONS = "app.connections.active",
}

/**
 * 常用频道指标 ID
 */
export enum ChannelMetricIds {
  /** 消息接收总数 */
  MESSAGES_RECEIVED = "channel.messages.received_total",
  /** 消息发送总数 */
  MESSAGES_SENT = "channel.messages.sent_total",
  /** 消息处理延迟 */
  MESSAGE_LATENCY = "channel.messages.latency_ms",
  /** 活跃会话数 */
  ACTIVE_SESSIONS = "channel.sessions.active",
  /** 频道错误数 */
  CHANNEL_ERRORS = "channel.errors.total",
}

/**
 * 常用队列指标 ID
 */
export enum QueueMetricIds {
  /** 队列深度 */
  QUEUE_DEPTH = "queue.depth",
  /** 入队速率 */
  ENQUEUE_RATE = "queue.enqueue_rate_per_sec",
  /** 出队速率 */
  DEQUEUE_RATE = "queue.dequeue_rate_per_sec",
  /** 队列延迟 */
  QUEUE_LATENCY = "queue.latency_ms",
  /** 死信队列大小 */
  DLQ_SIZE = "queue.dlq.size",
}
