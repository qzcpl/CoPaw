/**
 * Bot 相关类型定义
 * v4.0 新增 - 与后端 Python Schema 完全匹配
 */

/** Bot 平台类型 */
export type BotPlatform = "dingtalk" | "feishu" | "wechat" | "web";

/** Bot 状态 */
export type BotStatus = "connected" | "disconnected" | "error";

/**
 * Bot 信息 - 与后端 BotResponse 完全匹配
 */
export interface BotInfo {
  /** Bot ID */
  bot_id: string;
  /** Bot 名称 */
  bot_name: string;
  /** 名称（兼容旧代码） */
  name?: string;
  /** 租户 ID */
  tenant_id: string;
  /** 平台类型 */
  platform: BotPlatform;
  /** 状态 */
  status: BotStatus;
  /** Webhook URL（可选） */
  webhook_url?: string;
  /** Client ID（可选） */
  client_id?: string;
  /** 连接时间（可选） */
  connected_at?: string;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
  /** 配置 */
  config: Record<string, any>;
  /** 描述（兼容旧代码） */
  description?: string;
  /** 是否启用（兼容旧代码） */
  enabled?: boolean;
  /** Bot 密钥（兼容旧代码） */
  bot_secret?: string;
}

/**
 * Bot 创建请求 - 与后端 BotCreateRequest 完全匹配
 */
export interface BotCreateRequest {
  /** Bot 名称 */
  bot_name: string;
  /** 平台类型 */
  platform: BotPlatform;
  /** 租户 ID */
  tenant_id: string;
  /** 配置（可选） */
  config?: Record<string, any>;
}

/**
 * Bot 更新请求 - 与后端 BotUpdateRequest 完全匹配
 */
export interface BotUpdateRequest {
  /** Bot 名称（可选） */
  bot_name?: string;
  /** 配置（可选） */
  config?: Record<string, any>;
}

/**
 * Bot 连接请求 - 与后端 BotConnectRequest 完全匹配
 */
export interface BotConnectRequest {
  /** Bot ID */
  bot_id: string;
  /** Client ID */
  client_id: string;
  /** Client Secret */
  client_secret: string;
  /** Webhook URL */
  webhook_url: string;
}

/**
 * Bot 状态响应 - 与后端 BotStatusResponse 完全匹配
 */
export interface BotStatusResponse {
  /** Bot ID */
  bot_id: string;
  /** 状态 */
  status: BotStatus;
  /** 最后心跳时间（可选） */
  last_heartbeat?: string;
  /** 消息数量 */
  message_count: number;
  /** 错误数量 */
  error_count: number;
}
