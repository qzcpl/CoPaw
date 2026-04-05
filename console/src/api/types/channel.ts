/**
 * 频道相关类型定义
 * v4.0 更新 - 新增频道管理、频道实例类型（与后端 Python Schema 完全匹配）
 */

/** 频道平台类型 */
export type ChannelPlatform =
  | "dingtalk"
  | "feishu"
  | "wechat"
  | "web"
  | "discord"
  | "telegram"
  | "mqtt"
  | "matrix"
  | "mattermost"
  | "wecom"
  | "qq"
  | "imessage"
  | "voice"
  | "xiaoyi"
  | "console";

/** 频道状态 */
export type ChannelStatus = "active" | "inactive" | "error" | "maintenance";

/** 消息策略 */
export type MessagePolicy = "open" | "allowlist" | "blocklist";

/**
 * 基础频道配置 - 保留原有类型
 */
export interface BaseChannelConfig {
  enabled: boolean;
  bot_prefix: string;
  filter_tool_messages?: boolean;
  filter_thinking?: boolean;
  dm_policy?: MessagePolicy;
  group_policy?: MessagePolicy;
  allow_from?: string[];
  require_mention?: boolean;
}

/**
 * 频道配置 - v4.0 新增
 * 与后端 ChannelConfigResponse 完全匹配
 */
export interface ChannelConfig {
  /** 频道 ID（如 dingtalk） */
  channel_id: string;
  /** 频道名称 */
  channel_name: string;
  /** 平台类型 */
  platform: ChannelPlatform;
  /** 状态 */
  status: ChannelStatus;
  /** 租户 ID */
  tenant_id: string;
  /** 配置 */
  config: Record<string, any>;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
  /** 描述（可选） */
  description?: string;
  /** 图标 URL（可选） */
  icon_url?: string;
}

/**
 * 频道创建请求 - 与后端 ChannelCreateRequest 完全匹配
 */
export interface ChannelCreateRequest {
  /** 频道 ID */
  channel_id: string;
  /** 频道名称 */
  channel_name: string;
  /** 平台类型 */
  platform: ChannelPlatform;
  /** 配置 */
  config: Record<string, any>;
  /** 描述（可选） */
  description?: string;
}

/**
 * 频道更新请求 - 与后端 ChannelUpdateRequest 完全匹配
 */
export interface ChannelUpdateRequest {
  /** 频道名称（可选） */
  channel_name?: string;
  /** 配置（可选） */
  config?: Record<string, any>;
  /** 描述（可选） */
  description?: string;
  /** 状态（可选） */
  status?: ChannelStatus;
}

/**
 * 频道实例 - v4.0 新增
 * 与后端 ChannelInstanceResponse 完全匹配
 */
export interface ChannelInstance {
  /** 实例 ID */
  instance_id: string;
  /** 频道 ID */
  channel_id: string;
  /** Bot ID */
  bot_id: string;
  /** 租户 ID */
  tenant_id: string;
  /** 状态 */
  status: ChannelStatus;
  /** 连接时间（可选） */
  connected_at?: string;
  /** 最后心跳时间（可选） */
  last_heartbeat?: string;
  /** 消息数量 */
  message_count: number;
  /** 错误数量 */
  error_count: number;
  /** 配置 */
  config: Record<string, any>;
}

/**
 * 频道统计 - v4.0 新增
 * 与后端 ChannelStatsResponse 完全匹配
 */
export interface ChannelStatsResponse {
  /** 频道 ID */
  channel_id: string;
  /** 实例数量 */
  instance_count: number;
  /** 24 小时消息数量 */
  message_count_24h: number;
  /** 活跃会话数量 */
  active_sessions: number;
  /** 错误数量 */
  error_count_24h: number;
  /** 平均响应时间（毫秒） */
  avg_response_time_ms: number;
}

/**
 * 频道健康状态 - v4.0 新增
 */
export interface ChannelHealthStatus {
  /** 频道 ID */
  channel_id: string;
  /** 状态 */
  status: "healthy" | "degraded" | "unhealthy";
  /** 健康分数（0-100） */
  health_score: number;
  /** 问题列表 */
  issues: string[];
  /** 建议列表 */
  recommendations: string[];
}

// ── 保留原有类型定义（向后兼容） ──────────────────────────────────────────

export interface IMessageChannelConfig extends BaseChannelConfig {
  db_path: string;
  poll_sec: number;
}

export interface DiscordConfig extends BaseChannelConfig {
  bot_token: string;
  http_proxy: string;
  http_proxy_auth: string;
  accept_bot_messages?: boolean;
}

export interface DingTalkConfig extends BaseChannelConfig {
  client_id: string;
  client_secret: string;
  message_type: string;
  card_template_id: string;
  card_template_key: string;
  robot_code: string;
}

export interface FeishuConfig extends BaseChannelConfig {
  app_id: string;
  app_secret: string;
  encrypt_key: string;
  verification_token: string;
  media_dir: string;
  domain?: "feishu" | "lark";
}

export interface QQConfig extends BaseChannelConfig {
  app_id: string;
  client_secret: string;
}

export interface TelegramConfig extends BaseChannelConfig {
  bot_token: string;
  http_proxy: string;
  http_proxy_auth: string;
  show_typing?: boolean;
}

export interface MQTTConfig extends BaseChannelConfig {
  host: string;
  port: number;
  transport: string;
  clean_session: boolean;
  qos: number;
  username: string;
  password: string;
  subscribe_topic: string;
  publish_topic: string;
  tls_enabled?: boolean;
  tls_ca_certs?: string;
  tls_certfile?: string;
  tls_keyfile?: string;
}

export interface MatrixConfig extends BaseChannelConfig {
  homeserver: string;
  user_id: string;
  access_token: string;
}

export interface MattermostConfig extends BaseChannelConfig {
  url: string;
  bot_token: string;
  media_dir?: string;
  show_typing?: boolean;
  thread_follow_without_mention?: boolean;
}

export interface WecomConfig extends BaseChannelConfig {
  bot_id: string;
  secret: string;
  media_dir?: string;
  welcome_text?: string;
  max_reconnect_attempts?: number;
}

export type ConsoleConfig = BaseChannelConfig;

export interface VoiceChannelConfig extends BaseChannelConfig {
  twilio_account_sid: string;
  twilio_auth_token: string;
  phone_number: string;
  phone_number_sid: string;
  tts_provider: string;
  tts_voice: string;
  stt_provider: string;
  language: string;
  welcome_greeting: string;
}

export interface XiaoYiConfig extends BaseChannelConfig {
  ak: string;
  sk: string;
  agent_id: string;
  ws_url: string;
  task_timeout_ms?: number;
}

/**
 * 旧版 ChannelConfig 类型（保留用于向后兼容）
 */
export interface LegacyChannelConfig {
  imessage: IMessageChannelConfig;
  discord: DiscordConfig;
  dingtalk: DingTalkConfig;
  feishu: FeishuConfig;
  qq: QQConfig;
  telegram: TelegramConfig;
  mqtt: MQTTConfig;
  matrix: MatrixConfig;
  mattermost: MattermostConfig;
  wecom: WecomConfig;
  console: ConsoleConfig;
  voice: VoiceChannelConfig;
  xiaoyi: XiaoYiConfig;
}

export type SingleChannelConfig =
  | IMessageChannelConfig
  | DiscordConfig
  | DingTalkConfig
  | FeishuConfig
  | QQConfig
  | ConsoleConfig
  | TelegramConfig
  | MQTTConfig
  | MatrixConfig
  | MattermostConfig
  | WecomConfig
  | VoiceChannelConfig
  | XiaoYiConfig;
