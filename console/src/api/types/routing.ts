/**
 * 路由相关类型定义
 * v4.0 新增 - 与后端 Python Schema 完全匹配
 */

/** 路由策略类型 */
export type RoutingStrategyType = "direct" | "round_robin" | "weighted" | "skill_based" | "least_loaded";

/** 路由状态 */
export type RoutingStatus = "active" | "inactive";

/**
 * 路由策略 - 与后端 RoutingStrategyResponse 完全匹配
 */
export interface RoutingStrategy {
  /** 策略 ID */
  strategy_id: string;
  /** 策略名称 */
  strategy_name: string;
  /** 策略类型 */
  strategy_type: RoutingStrategyType;
  /** 租户 ID */
  tenant_id: string;
  /** 配置 */
  config: Record<string, any>;
  /** 状态 */
  status: RoutingStatus;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
}

/**
 * 路由策略创建请求 - 与后端 RoutingStrategyCreateRequest 完全匹配
 */
export interface RoutingStrategyCreateRequest {
  /** 策略名称 */
  strategy_name: string;
  /** 策略类型 */
  strategy_type: RoutingStrategyType;
  /** 租户 ID */
  tenant_id: string;
  /** 配置 */
  config: Record<string, any>;
}

/**
 * 路由策略更新请求 - 与后端 RoutingStrategyUpdateRequest 完全匹配
 */
export interface RoutingStrategyUpdateRequest {
  /** 策略名称（可选） */
  strategy_name?: string;
  /** 配置（可选） */
  config?: Record<string, any>;
  /** 状态（可选） */
  status?: RoutingStatus;
}

/**
 * 路由配置 - 与后端 RoutingConfigResponse 完全匹配
 */
export interface RoutingConfig {
  /** callId */
  call_id: string;
  /** 策略 ID */
  strategy_id: string;
  /** 策略类型 */
  strategy_type: string;
  /** 配置 */
  config: Record<string, any>;
  /** 目标列表 */
  targets: RoutingTarget[];
  /** 状态 */
  status: RoutingStatus;
}

/**
 * 路由目标
 */
export interface RoutingTarget {
  /** Agent ID */
  agent_id: string;
  /** 权重（用于加权轮询） */
  weight?: number;
  /** 技能标签（用于技能路由） */
  skills?: string[];
  /** 优先级 */
  priority?: number;
}

/**
 * 路由配置创建请求
 */
export interface RoutingConfigCreateRequest {
  /** callId */
  call_id: string;
  /** 策略 ID */
  strategy_id: string;
  /** 配置 */
  config: Record<string, any>;
  /** 目标列表 */
  targets: RoutingTarget[];
}

/**
 * 路由配置更新请求 - 与后端 RoutingConfigUpdateRequest 完全匹配
 */
export interface RoutingConfigUpdateRequest {
  /** 策略 ID（可选） */
  strategy_id?: string;
  /** 配置（可选） */
  config?: Record<string, any>;
  /** 目标列表（可选） */
  targets?: RoutingTarget[];
}

/**
 * 路由规则 - 用于前端管理（兼容旧代码）
 */
export interface RoutingRule {
  /** 规则 ID */
  rule_id: string;
  /** 规则名称 */
  rule_name: string;
  /** callId */
  call_id: string;
  /** 策略 ID */
  strategy_id: string;
  /** 优先级 */
  priority: number;
  /** 匹配条件 */
  match_conditions: MatchCondition[];
  /** 目标 Agent ID */
  target_agent_id: string;
  /** 状态 */
  status: RoutingStatus;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
  /** 是否启用（兼容旧代码） */
  enabled?: boolean;
}

/**
 * 匹配条件
 */
export interface MatchCondition {
  /** 字段 */
  field: string;
  /** 操作符 */
  operator: "equals" | "contains" | "regex" | "gt" | "lt";
  /** 值 */
  value: string;
}

/**
 * 路由决策 - 与后端 RoutingDecision 完全匹配
 */
export interface RoutingDecision {
  /** 决策 ID */
  decision_id: string;
  /** callId */
  call_id: string;
  /** 命中的策略 ID */
  strategy_id: string;
  /** 命中的规则 ID */
  rule_id?: string;
  /** 目标 Agent ID */
  target_agent_id: string;
  /** 决策时间 */
  decided_at: string;
  /** 决策原因 */
  reason?: string;
}

/**
 * 路由决策链
 */
export interface RoutingDecisionChain {
  /** 决策链 ID */
  chain_id: string;
  /** callId */
  call_id: string;
  /** 决策列表 */
  decisions: RoutingDecision[];
  /** 最终状态 */
  final_status: "routed" | "dropped" | "error";
  /** 创建时间 */
  created_at: string;
}

/**
 * 路由测试请求
 */
export interface RoutingTestRequest {
  /** callId */
  call_id: string;
  /** 测试输入 */
  input: Record<string, any>;
}

/**
 * 路由测试结果
 */
export interface RoutingTestResult {
  /** 是否匹配 */
  matched: boolean;
  /** 命中的规则 ID */
  rule_id?: string;
  /** 目标 Agent ID */
  target_agent_id?: string;
  /** 决策原因 */
  reason?: string;
}

/**
 * 路由测试输出
 */
export interface RoutingTestOutput {
  /** 输出类型 */
  output_type: "text" | "json" | "error";
  /** 输出内容 */
  content: string;
  /** 元数据 */
  metadata?: Record<string, any>;
}

/**
 * Agent 路由状态
 */
export interface AgentRoutingStatus {
  /** Agent ID */
  agent_id: string;
  /** 状态 */
  status: "active" | "inactive" | "error" | "busy";
  /** 当前负载 */
  current_load: number;
  /** 最大负载 */
  max_load: number;
  /** 技能标签 */
  skills: string[];
  /** 最后更新时间 */
  updated_at: string;
}

/**
 * 路由统计响应
 */
export interface RoutingStatsResponse {
  /** 策略 ID */
  strategy_id: string;
  /** 总请求数 */
  total_requests: number;
  /** 成功路由数 */
  successful_routes: number;
  /** 失败路由数 */
  failed_routes: number;
  /** 平均延迟（毫秒） */
  avg_latency_ms: number;
  /** 统计时间 */
  stats_at: string;
}

/**
 * 路由列表响应
 */
export interface RoutingListResponse {
  /** 路由策略列表 */
  strategies: RoutingStrategy[];
  /** 路由配置列表 */
  configs: RoutingConfig[];
  /** 总数 */
  total: number;
}

/**
 * 故障转移配置
 */
export interface FailoverConfig {
  /** 是否启用 */
  enabled: boolean;
  /** 超时时间（毫秒） */
  timeout_ms: number;
  /** 最大重试次数 */
  max_retries: number;
  /** 备用目标列表 */
  fallback_targets: string[];
}

/**
 * 负载均衡配置
 */
export interface LoadBalancingConfig {
  /** 负载均衡策略 */
  strategy: "round_robin" | "weighted" | "least_loaded";
  /** 权重配置 */
  weights?: Record<string, number>;
  /** 健康检查间隔（秒） */
  health_check_interval_sec: number;
}

/**
 * 路由策略配置
 */
export interface RoutingStrategyConfig {
  /** 策略类型 */
  strategy_type: RoutingStrategyType;
  /** 故障转移配置 */
  failover?: FailoverConfig;
  /** 负载均衡配置 */
  load_balancing?: LoadBalancingConfig;
  /** 自定义配置 */
  custom?: Record<string, any>;
}
