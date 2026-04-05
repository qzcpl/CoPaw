/**
 * 灰度发布 API 模块
 * v4.0 新增 - 6 个 API 接口，与后端 routes/gray_release.py 完全匹配
 */
import { request } from "../request";

/**
 * 灰度发布配置接口
 */
export interface GrayReleaseConfig {
  /** 配置 ID */
  config_id: string;
  /** 配置名称 */
  config_name: string;
  /** 租户 ID */
  tenant_id: string;
  /** 目标类型 */
  target_type: "agent" | "channel" | "callid" | "skill";
  /** 目标 ID */
  target_id: string;
  /** 灰度策略 */
  gray_strategy: GrayStrategy;
  /** 灰度比例（0-100） */
  gray_percentage: number;
  /** 状态 */
  status: GrayReleaseStatus;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
  /** 开始时间（可选） */
  start_at?: string;
  /** 结束时间（可选） */
  end_at?: string;
  /** 描述（可选） */
  description?: string;
}

/**
 * 灰度策略类型
 */
export type GrayStrategy =
  | "percentage"     // 按比例
  | "whitelist"      // 白名单
  | "canary"         // 金丝雀
  | "ab_test";       // A/B 测试

/**
 * 灰度发布状态
 */
export type GrayReleaseStatus =
  | "draft"         // 草稿
  | "pending"       // 待启动
  | "running"       // 进行中
  | "paused"        // 已暂停
  | "completed"     // 已完成
  | "rolled_back";  // 已回滚

/**
 * 灰度发布创建请求
 */
export interface GrayReleaseCreateRequest {
  /** 配置名称 */
  config_name: string;
  /** 目标类型 */
  target_type: "agent" | "channel" | "callid" | "skill";
  /** 目标 ID */
  target_id: string;
  /** 灰度策略 */
  gray_strategy: GrayStrategy;
  /** 灰度比例（0-100） */
  gray_percentage: number;
  /** 白名单（可选，用于 whitelist 策略） */
  whitelist?: string[];
  /** 描述（可选） */
  description?: string;
}

/**
 * 灰度发布更新请求
 */
export interface GrayReleaseUpdateRequest {
  /** 配置名称（可选） */
  config_name?: string;
  /** 灰度策略（可选） */
  gray_strategy?: GrayStrategy;
  /** 灰度比例（可选） */
  gray_percentage?: number;
  /** 白名单（可选） */
  whitelist?: string[];
  /** 状态（可选） */
  status?: GrayReleaseStatus;
  /** 描述（可选） */
  description?: string;
}

/**
 * 灰度发布统计
 */
export interface GrayReleaseStats {
  /** 配置 ID */
  config_id: string;
  /** 总请求数 */
  total_requests: number;
  /** 灰度请求数 */
  gray_requests: number;
  /** 灰度比例 */
  gray_percentage: number;
  /** 成功率 */
  success_rate: number;
  /** 平均延迟（毫秒） */
  avg_latency_ms: number;
  /** 错误数 */
  error_count: number;
  /** 统计时间 */
  stats_at: string;
}

/**
 * 列出灰度发布配置
 * @param tenantId 租户 ID（可选）
 * @param status 状态（可选）
 * @param targetType 目标类型（可选）
 * @returns 灰度发布配置列表
 */
export async function listGrayReleaseConfigs(
  tenantId?: string,
  status?: string,
  targetType?: string
): Promise<GrayReleaseConfig[]> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  if (status) {
    params.append("status", status);
  }
  if (targetType) {
    params.append("target_type", targetType);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/gray-release${query}`);
}

/**
 * 查询灰度发布配置详情
 * @param configId 配置 ID
 * @returns 灰度发布配置详情
 */
export async function getGrayReleaseConfig(configId: string): Promise<GrayReleaseConfig> {
  return request(`/gray-release/${configId}`);
}

/**
 * 创建灰度发布配置
 * @param data 灰度发布创建请求
 * @returns 创建后的灰度发布配置
 */
export async function createGrayReleaseConfig(
  data: GrayReleaseCreateRequest
): Promise<GrayReleaseConfig> {
  return request("/gray-release", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 更新灰度发布配置
 * @param configId 配置 ID
 * @param data 灰度发布更新请求
 * @returns 更新后的灰度发布配置
 */
export async function updateGrayReleaseConfig(
  configId: string,
  data: GrayReleaseUpdateRequest
): Promise<GrayReleaseConfig> {
  return request(`/gray-release/${configId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * 删除灰度发布配置
 * @param configId 配置 ID
 * @returns 操作结果
 */
export async function deleteGrayReleaseConfig(configId: string): Promise<{ message: string }> {
  return request(`/gray-release/${configId}`, {
    method: "DELETE",
  });
}

/**
 * 启动灰度发布
 * @param configId 配置 ID
 * @returns 操作结果
 */
export async function startGrayRelease(configId: string): Promise<{ message: string }> {
  return request(`/gray-release/${configId}/start`, {
    method: "POST",
  });
}

/**
 * 暂停灰度发布
 * @param configId 配置 ID
 * @returns 操作结果
 */
export async function pauseGrayRelease(configId: string): Promise<{ message: string }> {
  return request(`/gray-release/${configId}/pause`, {
    method: "POST",
  });
}

/**
 * 恢复灰度发布
 * @param configId 配置 ID
 * @returns 操作结果
 */
export async function resumeGrayRelease(configId: string): Promise<{ message: string }> {
  return request(`/gray-release/${configId}/resume`, {
    method: "POST",
  });
}

/**
 * 停止灰度发布
 * @param configId 配置 ID
 * @returns 操作结果
 */
export async function stopGrayRelease(configId: string): Promise<{ message: string }> {
  return request(`/gray-release/${configId}/stop`, {
    method: "POST",
  });
}

/**
 * 回滚灰度发布
 * @param configId 配置 ID
 * @param reason 回滚原因
 * @returns 操作结果
 */
export async function rollbackGrayRelease(
  configId: string,
  reason: string
): Promise<{ message: string }> {
  return request(`/gray-release/${configId}/rollback`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

/**
 * 查询灰度发布统计
 * @param configId 配置 ID
 * @param startTime 开始时间
 * @param endTime 结束时间
 * @returns 灰度发布统计
 */
export async function getGrayReleaseStats(
  configId: string,
  startTime: string,
  endTime: string
): Promise<GrayReleaseStats> {
  const params = new URLSearchParams({
    start_time: startTime,
    end_time: endTime,
  });
  return request(`/gray-release/${configId}/stats?${params.toString()}`);
}

/**
 * 灰度发布 API 模块导出
 */
export const grayReleaseApi = {
  listGrayReleaseConfigs,
  listGrayReleases: listGrayReleaseConfigs,  // 别名，与后端匹配
  getGrayReleaseConfig,
  getGrayRelease: getGrayReleaseConfig,  // 别名，与后端匹配
  createGrayReleaseConfig,
  createGrayRelease: createGrayReleaseConfig,  // 别名，与后端匹配
  updateGrayReleaseConfig,
  updateGrayRelease: updateGrayReleaseConfig,  // 别名，与后端匹配
  deleteGrayReleaseConfig,
  startGrayRelease,
  pauseGrayRelease,
  resumeGrayRelease,
  stopGrayRelease,
  rollbackGrayRelease,
  getGrayReleaseStats,
};
