/**
 * 频道 API 模块
 * v4.0 更新 - 新增频道管理 API（与后端 routes/channel.py 完全匹配）
 */
import { request } from "../request";
import type {
  ChannelConfig,
  ChannelCreateRequest,
  ChannelUpdateRequest,
  ChannelInstance,
  ChannelStatsResponse,
  ChannelHealthStatus,
  LegacyChannelConfig,
  SingleChannelConfig,
} from "../types";

/**
 * 列出频道（v4.0 更新）
 * @param tenantId 租户 ID（可选）
 * @param platform 平台类型（可选）
 * @param status 状态（可选）
 * @returns 频道列表
 */
export async function listChannels(
  tenantId?: string,
  platform?: string,
  status?: string
): Promise<ChannelConfig[]> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  if (platform) {
    params.append("platform", platform);
  }
  if (status) {
    params.append("status", status);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/channels${query}`);
}

/**
 * 查询频道详情（v4.0 新增）
 * @param channelId 频道 ID
 * @param tenantId 租户 ID（可选）
 * @returns 频道详情
 */
export async function getChannel(
  channelId: string,
  tenantId?: string
): Promise<ChannelConfig> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/channels/${channelId}${query}`);
}

/**
 * 创建频道（v4.0 新增）
 * @param data 频道创建请求
 * @returns 创建后的频道
 */
export async function createChannel(data: ChannelCreateRequest): Promise<ChannelConfig> {
  return request("/channels", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 更新频道（v4.0 新增）
 * @param channelId 频道 ID
 * @param data 频道更新请求
 * @returns 更新后的频道
 */
export async function updateChannel(
  channelId: string,
  data: ChannelUpdateRequest
): Promise<ChannelConfig> {
  return request(`/channels/${channelId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * 删除频道（v4.0 新增）
 * @param channelId 频道 ID
 * @param tenantId 租户 ID（可选）
 * @returns 操作结果
 */
export async function deleteChannel(
  channelId: string,
  tenantId?: string
): Promise<{ message: string }> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/channels/${channelId}${query}`, {
    method: "DELETE",
  });
}

/**
 * 列出频道实例（v4.0 新增）
 * @param channelId 频道 ID
 * @param tenantId 租户 ID（可选）
 * @returns 频道实例列表
 */
export async function listChannelInstances(
  channelId: string,
  tenantId?: string
): Promise<ChannelInstance[]> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/channels/${channelId}/instances${query}`);
}

/**
 * 查询频道实例详情（v4.0 新增）
 * @param channelId 频道 ID
 * @param instanceId 实例 ID
 * @returns 频道实例详情
 */
export async function getChannelInstance(
  channelId: string,
  instanceId: string
): Promise<ChannelInstance> {
  return request(`/channels/${channelId}/instances/${instanceId}`);
}

/**
 * 查询频道统计（v4.0 新增）
 * @param channelId 频道 ID
 * @param tenantId 租户 ID（可选）
 * @returns 频道统计
 */
export async function getChannelStats(
  channelId: string,
  tenantId?: string
): Promise<ChannelStatsResponse> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/channels/${channelId}/stats${query}`);
}

/**
 * 查询频道健康状态（v4.0 新增）
 * @param channelId 频道 ID
 * @returns 频道健康状态
 */
export async function getChannelHealth(
  channelId: string
): Promise<ChannelHealthStatus> {
  return request(`/channels/${channelId}/health`);
}

/**
 * 连接频道实例（v4.0 新增）
 * @param channelId 频道 ID
 * @param instanceId 实例 ID
 * @param config 连接配置
 * @returns 操作结果
 */
export async function connectChannelInstance(
  channelId: string,
  instanceId: string,
  config: Record<string, any>
): Promise<{ message: string }> {
  return request(`/channels/${channelId}/instances/${instanceId}/connect`, {
    method: "POST",
    body: JSON.stringify({ config }),
  });
}

/**
 * 断开频道实例连接（v4.0 新增）
 * @param channelId 频道 ID
 * @param instanceId 实例 ID
 * @returns 操作结果
 */
export async function disconnectChannelInstance(
  channelId: string,
  instanceId: string
): Promise<{ message: string }> {
  return request(`/channels/${channelId}/instances/${instanceId}/disconnect`, {
    method: "POST",
  });
}

/**
 * 重启频道实例（v4.0 新增）
 * @param channelId 频道 ID
 * @param instanceId 实例 ID
 * @returns 操作结果
 */
export async function restartChannelInstance(
  channelId: string,
  instanceId: string
): Promise<{ message: string }> {
  return request(`/channels/${channelId}/instances/${instanceId}/restart`, {
    method: "POST",
  });
}

// ── 保留原有 API（向后兼容） ─────────────────────────────────────────────────

export const legacyChannelApi = {
  listChannelTypes: () => request<string[]>("/config/channels/types"),

  getLegacyChannels: () => request<LegacyChannelConfig>("/config/channels"),

  updateLegacyChannels: (body: LegacyChannelConfig) =>
    request<LegacyChannelConfig>("/config/channels", {
      method: "PUT",
      body: JSON.stringify(body),
    }),

  getChannelConfig: (channelName: string) =>
    request<SingleChannelConfig>(
      `/config/channels/${encodeURIComponent(channelName)}`,
    ),

  updateChannelConfig: (channelName: string, body: SingleChannelConfig) =>
    request<SingleChannelConfig>(
      `/config/channels/${encodeURIComponent(channelName)}`,
      {
        method: "PUT",
        body: JSON.stringify(body),
      },
    ),

  getWeixinQrcode: () =>
    request<{ qrcode_img: string; qrcode: string }>(
      "/config/channels/weixin/qrcode",
    ),

  getWeixinQrcodeStatus: (qrcode: string) =>
    request<{ status: string; bot_token: string; base_url: string }>(
      `/config/channels/weixin/qrcode/status?qrcode=${encodeURIComponent(
        qrcode,
      )}`,
    ),
};

/**
 * 频道 API 模块导出
 */
export const channelApi = {
  // v4.0 新增 API
  listChannels,
  getChannel,
  createChannel,
  updateChannel,
  deleteChannel,
  listChannelInstances,
  getChannelInstance,
  getChannelStats,
  getChannelHealth,
  connectChannelInstance,
  disconnectChannelInstance,
  restartChannelInstance,

  // 保留原有 API（向后兼容）
  ...legacyChannelApi,
};
