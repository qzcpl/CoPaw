/**
 * callId 相关类型定义
 * v4.0 新增 - 与后端 Python Schema 完全匹配
 */

/** callId 类型 */
export type CallIdType = "shared" | "dedicated";

/** 路由策略类型 */
export type RoutingStrategy = "direct" | "round_robin" | "weighted" | "skill_based";

/** callId 状态 */
export type CallIdStatus = "active" | "suspended" | "unbound";

/** 变更类型 */
export type ChangeType = "bind" | "switch" | "suspend" | "resume" | "unbind";

/**
 * callId 绑定信息 - 与后端 CallIdBindingResponse 完全匹配
 */
export interface CallIdBinding {
  /** callId（如 400-001） */
  call_id: string;
  /** callId 类型 */
  call_type: CallIdType;
  /** 所属 Agent ID */
  owner_agent_id: string;
  /** 所属租户 ID */
  owner_tenant_id: string;
  /** 频道 ID */
  channel_id: string;
  /** 频道实例 ID */
  channel_instance_id: string;
  /** 路由策略 */
  routing_strategy: RoutingStrategy;
  /** 路由配置 */
  routing_config: Record<string, any>;
  /** 状态 */
  status: CallIdStatus;
  /** 绑定时间 */
  bound_at: string;
  /** 暂停时间（可选） */
  suspended_at?: string;
  /** 暂停原因（可选） */
  suspended_reason?: string;
  /** 元数据（可选） */
  metadata?: Record<string, any>;
}

/**
 * callId 绑定请求 - 与后端 CallIdBindRequest 完全匹配
 */
export interface CallIdBindRequest {
  /** callId */
  call_id: string;
  /** Agent ID */
  agent_id: string;
  /** 租户 ID */
  tenant_id: string;
  /** 频道 ID */
  channel_id: string;
  /** 路由策略（可选，默认 direct） */
  routing_strategy?: RoutingStrategy;
  /** 路由配置（可选） */
  routing_config?: Record<string, any>;
}

/**
 * callId 解绑请求 - 与后端 CallIdUnbindRequest 完全匹配
 */
export interface CallIdUnbindRequest {
  /** callId */
  call_id: string;
  /** 租户 ID */
  tenant_id: string;
}

/**
 * Agent 切换请求 - 与后端 CallIdSwitchRequest 完全匹配
 */
export interface CallIdSwitchRequest {
  /** callId */
  call_id: string;
  /** 新的 Agent ID */
  new_agent_id: string;
  /** 租户 ID */
  tenant_id: string;
  /** 切换原因（可选） */
  reason?: string;
}

/**
 * callId 暂停请求 - 与后端 CallIdSuspendRequest 完全匹配
 */
export interface CallIdSuspendRequest {
  /** callId */
  call_id: string;
  /** 租户 ID */
  tenant_id: string;
  /** 暂停原因 */
  reason: string;
}

/**
 * callId 恢复请求 - 与后端 CallIdResumeRequest 完全匹配
 */
export interface CallIdResumeRequest {
  /** callId */
  call_id: string;
  /** 租户 ID */
  tenant_id: string;
}

/**
 * callId 变更记录 - 与后端 CallIdChangeRecordResponse 完全匹配
 */
export interface CallIdChangeRecord {
  /** callId */
  call_id: string;
  /** 变更类型 */
  change_type: ChangeType;
  /** 旧绑定信息（可选） */
  old_binding?: Partial<CallIdBinding>;
  /** 新绑定信息（可选） */
  new_binding?: Partial<CallIdBinding>;
  /** 操作人 */
  operator: string;
  /** 变更原因 */
  reason: string;
  /** 创建时间 */
  created_at: string;
}
