/**
 * 租户相关类型定义
 * v4.0 新增 - 与后端 Python Schema 完全匹配
 */

/**
 * 租户信息 - 与后端 TenantResponse 完全匹配
 */
export interface TenantInfo {
  /** 租户 ID */
  tenant_id: string;
  /** 租户名称 */
  tenant_name: string;
  /** 状态 */
  status: string;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
  /** 配置 */
  config: Record<string, any>;
  /** 最大 Agent 数量 */
  max_agents: number;
  /** 最大 callId 数量 */
  max_callids: number;
  /** 描述（兼容旧代码） */
  description?: string;
  /** 是否启用（兼容旧代码） */
  enabled?: boolean;
  /** 最大 Bot 数量（兼容旧代码） */
  max_bots?: number;
  /** 最大 Channel 数量（兼容旧代码） */
  max_channels?: number;
  /** Bot 数量（兼容旧代码） */
  bot_count?: number;
  /** Channel 数量（兼容旧代码） */
  channel_count?: number;
  /** callId 数量（兼容旧代码） */
  callid_count?: number;
}

/**
 * 租户创建请求 - 与后端 TenantCreateRequest 完全匹配
 */
export interface TenantCreateRequest {
  /** 租户 ID */
  tenant_id: string;
  /** 租户名称 */
  tenant_name: string;
  /** 最大 Agent 数量（默认 10） */
  max_agents?: number;
  /** 最大 callId 数量（默认 100） */
  max_callids?: number;
  /** 配置（可选） */
  config?: Record<string, any>;
  // ===== 兼容字段（可选，用于旧代码）=====
  /** 描述（兼容旧代码） */
  description?: string;
  /** 最大 Bot 数量（兼容旧代码） */
  max_bots?: number;
  /** 最大 Channel 数量（兼容旧代码） */
  max_channels?: number;
}

/**
 * 租户更新请求 - 与后端 TenantUpdateRequest 完全匹配
 */
export interface TenantUpdateRequest {
  /** 租户名称（可选） */
  tenant_name?: string;
  /** 最大 Agent 数量（可选） */
  max_agents?: number;
  /** 最大 callId 数量（可选） */
  max_callids?: number;
  /** 配置（可选） */
  config?: Record<string, any>;
  // ===== 兼容字段（可选，用于旧代码）=====
  /** 描述（兼容旧代码） */
  description?: string;
  /** 是否启用（兼容旧代码） */
  enabled?: boolean;
  /** 最大 Bot 数量（兼容旧代码） */
  max_bots?: number;
  /** 最大 Channel 数量（兼容旧代码） */
  max_channels?: number;
}

/**
 * 租户统计响应 - 与后端 TenantStatsResponse 完全匹配
 */
export interface TenantStatsResponse {
  /** 租户 ID */
  tenant_id: string;
  /** Agent 数量 */
  agent_count: number;
  /** callId 数量 */
  callid_count: number;
  /** 24 小时消息数量 */
  message_count_24h: number;
  /** 活跃会话数量 */
  active_sessions: number;
}
