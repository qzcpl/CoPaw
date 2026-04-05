/**
 * 灰度发布相关类型定义
 * v4.0 新增 - 与后端 Python Schema 完全匹配
 */

// 从 routing.ts 导入共享类型
import type { MatchCondition } from './routing';

/** 灰度发布状态 */
export type GrayReleaseStatus = "active" | "paused" | "completed" | "rolled_back";

/**
 * 灰度发布配置 - 与后端 GrayReleaseConfigResponse 完全匹配
 */
export interface GrayReleaseConfig {
  /** 发布 ID */
  release_id: string;
  /** 发布名称 */
  release_name: string;
  /** callId */
  call_id: string;
  /** 目标 Agent ID */
  target_agent_id: string;
  /** 流量百分比（0-100） */
  traffic_percentage: number;
  /** 状态 */
  status: GrayReleaseStatus;
  /** 开始时间 */
  started_at: string;
  /** 完成时间（可选） */
  completed_at?: string;
  /** 配置 */
  config: Record<string, any>;
  // ===== 兼容字段（可选，用于旧代码）=====
  config_id?: string;
  config_name?: string;
  enabled?: boolean;
  paused?: boolean;
  tenant_id?: string;
  target_type?: "agent" | "channel" | "callid" | "skill";
  gray_strategy?: any;
  gray_percentage?: number;
}

/**
 * 灰度发布创建请求 - 与后端 GrayReleaseCreateRequest 完全匹配
 */
export interface GrayReleaseCreateRequest {
  /** 发布名称 */
  release_name: string;
  /** callId */
  call_id: string;
  /** 目标 Agent ID */
  target_agent_id: string;
  /** 流量百分比（0-100） */
  traffic_percentage: number;
  /** 配置（可选） */
  config?: Record<string, any>;
}

/**
 * 灰度发布更新请求 - 与后端 GrayReleaseUpdateRequest 完全匹配
 */
export interface GrayReleaseUpdateRequest {
  /** 流量百分比（可选） */
  traffic_percentage?: number;
  /** 状态（可选） */
  status?: GrayReleaseStatus;
}

/**
 * 灰度发布指标 - 与后端 GrayReleaseMetricsResponse 完全匹配
 */
export interface GrayReleaseMetrics {
  /** 发布 ID */
  release_id: string;
  /** 总请求数 */
  total_requests: number;
  /** 目标 Agent 请求数 */
  target_agent_requests: number;
  /** 原始 Agent 请求数 */
  original_agent_requests: number;
  /** 错误率 */
  error_rate: number;
  /** 平均延迟（毫秒） */
  avg_latency_ms: number;
  /** 回滚次数 */
  rollback_count: number;
}

/**
 * 灰度发布规则 - 用于前端管理
 */
export interface GrayReleaseRule {
  /** 规则 ID */
  rule_id: string;
  /** 规则名称 */
  rule_name: string;
  /** callId */
  call_id: string;
  /** 目标 Agent ID */
  target_agent_id: string;
  /** 原始 Agent ID */
  original_agent_id: string;
  /** 流量百分比（0-100） */
  traffic_percentage: number;
  /** 匹配条件 */
  match_conditions: MatchCondition[];
  /** 状态 */
  status: GrayReleaseStatus;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
}

/**
 * 灰度发布历史
 */
export interface GrayReleaseHistory {
  /** 发布 ID */
  release_id: string;
  /** 事件类型 */
  event_type: "created" | "updated" | "paused" | "resumed" | "completed" | "rolled_back";
  /** 事件描述 */
  description: string;
  /** 事件时间 */
  occurred_at: string;
  /** 详细信息 */
  details?: Record<string, any>;
}

/**
 * 灰度发布列表响应
 */
export interface GrayReleaseListResponse {
  /** 灰度发布列表 */
  items: GrayReleaseConfig[];
  /** 总数 */
  total: number;
}
