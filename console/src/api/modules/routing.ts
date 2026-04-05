/**
 * 路由配置 API 模块
 * v4.0 新增 - 5 个 API 接口，与后端 routes/routing.py 完全匹配
 */
import { request } from "../request";
import type {
  RoutingStrategy,
  RoutingStrategyCreateRequest,
  RoutingStrategyUpdateRequest,
  RoutingConfig,
  RoutingConfigCreateRequest,
  RoutingConfigUpdateRequest,
  RoutingDecision,
  RoutingTestResult,
  AgentRoutingStatus,
  RoutingStatsResponse,
} from "../types/routing";

/**
 * 列出路由策略
 * @param tenantId 租户 ID（可选）
 * @param strategyType 策略类型（可选）
 * @returns 路由策略列表
 */
export async function listRoutingStrategies(
  tenantId?: string,
  strategyType?: string
): Promise<RoutingStrategy[]> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  if (strategyType) {
    params.append("strategy_type", strategyType);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/routing/strategies${query}`);
}

/**
 * 查询路由策略详情
 * @param strategyId 策略 ID
 * @returns 路由策略详情
 */
export async function getRoutingStrategy(strategyId: string): Promise<RoutingStrategy> {
  return request(`/routing/strategies/${strategyId}`);
}

/**
 * 创建路由策略
 * @param data 路由策略创建请求
 * @returns 创建后的路由策略
 */
export async function createRoutingStrategy(
  data: RoutingStrategyCreateRequest
): Promise<RoutingStrategy> {
  return request("/routing/strategies", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 更新路由策略
 * @param strategyId 策略 ID
 * @param data 路由策略更新请求
 * @returns 更新后的路由策略
 */
export async function updateRoutingStrategy(
  strategyId: string,
  data: RoutingStrategyUpdateRequest
): Promise<RoutingStrategy> {
  return request(`/routing/strategies/${strategyId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * 删除路由策略
 * @param strategyId 策略 ID
 * @returns 操作结果
 */
export async function deleteRoutingStrategy(strategyId: string): Promise<{ message: string }> {
  return request(`/routing/strategies/${strategyId}`, {
    method: "DELETE",
  });
}

/**
 * 列出路由配置
 * @param tenantId 租户 ID（可选）
 * @param callId callId（可选）
 * @returns 路由配置列表
 */
export async function listRoutingConfigs(
  tenantId?: string,
  callId?: string
): Promise<RoutingConfig[]> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  if (callId) {
    params.append("call_id", callId);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/routing/configs${query}`);
}

/**
 * 查询路由配置详情
 * @param configId 配置 ID
 * @returns 路由配置详情
 */
export async function getRoutingConfig(configId: string): Promise<RoutingConfig> {
  return request(`/routing/configs/${configId}`);
}

/**
 * 创建路由配置
 * @param data 路由配置创建请求
 * @returns 创建后的路由配置
 */
export async function createRoutingConfig(
  data: RoutingConfigCreateRequest
): Promise<RoutingConfig> {
  return request("/routing/configs", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 更新路由配置
 * @param configId 配置 ID
 * @param data 路由配置更新请求
 * @returns 更新后的路由配置
 */
export async function updateRoutingConfig(
  configId: string,
  data: RoutingConfigUpdateRequest
): Promise<RoutingConfig> {
  return request(`/routing/configs/${configId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * 删除路由配置
 * @param configId 配置 ID
 * @returns 操作结果
 */
export async function deleteRoutingConfig(configId: string): Promise<{ message: string }> {
  return request(`/routing/configs/${configId}`, {
    method: "DELETE",
  });
}

/**
 * 查询路由决策历史
 * @param callId callId
 * @param sessionId 会话 ID（可选）
 * @param limit 返回记录数（默认 50）
 * @returns 路由决策历史
 */
export async function getRoutingDecisions(
  callId: string,
  sessionId?: string,
  limit: number = 50
): Promise<RoutingDecision[]> {
  const params = new URLSearchParams({
    call_id: callId,
    limit: limit.toString(),
  });
  if (sessionId) {
    params.append("session_id", sessionId);
  }
  return request(`/routing/decisions?${params.toString()}`);
}

/**
 * 测试路由策略
 * @param strategyId 策略 ID
 * @param testInput 测试输入
 * @returns 路由测试结果
 */
export async function testRoutingStrategy(
  strategyId: string,
  testInput: Record<string, any>
): Promise<RoutingTestResult> {
  return request(`/routing/strategies/${strategyId}/test`, {
    method: "POST",
    body: JSON.stringify({ test_input: testInput }),
  });
}

/**
 * 查询 Agent 路由状态
 * @param tenantId 租户 ID
 * @returns Agent 路由状态列表
 */
export async function getAgentRoutingStatus(
  tenantId: string
): Promise<AgentRoutingStatus[]> {
  const params = new URLSearchParams({ tenant_id: tenantId });
  return request(`/routing/agents/status?${params.toString()}`);
}

/**
 * 查询路由统计
 * @param tenantId 租户 ID
 * @param startTime 开始时间
 * @param endTime 结束时间
 * @returns 路由统计
 */
export async function getRoutingStats(
  tenantId: string,
  startTime: string,
  endTime: string
): Promise<RoutingStatsResponse> {
  const params = new URLSearchParams({
    tenant_id: tenantId,
    start_time: startTime,
    end_time: endTime,
  });
  return request(`/routing/stats?${params.toString()}`);
}

/**
 * 路由 API 模块导出
 */
export const routingApi = {
  listRoutingStrategies,
  listRoutingRules: listRoutingStrategies,  // 别名，与前端页面匹配
  getRoutingStrategy,
  createRoutingStrategy,
  updateRoutingStrategy,
  deleteRoutingStrategy,
  listRoutingConfigs,
  getRoutingConfig,
  createRoutingConfig,
  updateRoutingConfig,
  deleteRoutingConfig,
  getRoutingDecisions,
  testRoutingStrategy,
  getAgentRoutingStatus,
  getRoutingStats,
};
