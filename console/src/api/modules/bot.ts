/**
 * Bot 管理 API 模块
 * v4.0 新增 - 7 个 API 接口，与后端 routes/bot.py 完全匹配
 */
import { request } from "../request";
import type {
  BotInfo,
  BotCreateRequest,
  BotUpdateRequest,
  BotConnectRequest,
  BotStatusResponse,
} from "../types/bot";

/**
 * 列出 Bot 列表
 * @param tenantId 租户 ID（可选）
 * @param platform 平台类型（可选）
 * @returns Bot 列表
 */
export async function listBots(
  tenantId?: string,
  platform?: string
): Promise<BotInfo[]> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  if (platform) {
    params.append("platform", platform);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/bots${query}`);
}

/**
 * 查询 Bot 详情
 * @param botId Bot ID
 * @returns Bot 详情
 */
export async function getBot(botId: string): Promise<BotInfo> {
  return request(`/bots/${botId}`);
}

/**
 * 创建 Bot
 * @param data Bot 创建请求
 * @returns 创建后的 Bot 信息
 */
export async function createBot(data: BotCreateRequest): Promise<BotInfo> {
  return request("/bots", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 更新 Bot
 * @param botId Bot ID
 * @param data Bot 更新请求
 * @returns 更新后的 Bot 信息
 */
export async function updateBot(
  botId: string,
  data: BotUpdateRequest
): Promise<BotInfo> {
  return request(`/bots/${botId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * 连接 Bot
 * @param data Bot 连接请求
 * @returns 操作结果
 */
export async function connectBot(data: BotConnectRequest): Promise<{ message: string }> {
  return request("/bots/connect", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 断开 Bot 连接
 * @param botId Bot ID
 * @returns 操作结果
 */
export async function disconnectBot(botId: string): Promise<{ message: string }> {
  return request(`/bots/${botId}/disconnect`, {
    method: "POST",
  });
}

/**
 * 查询 Bot 状态
 * @param botId Bot ID
 * @returns Bot 状态
 */
export async function getBotStatus(botId: string): Promise<BotStatusResponse> {
  return request(`/bots/${botId}/status`);
}

/**
 * 删除 Bot
 * @param botId Bot ID
 * @returns 操作结果
 */
export async function deleteBot(botId: string): Promise<{ message: string }> {
  return request(`/bots/${botId}`, {
    method: "DELETE",
  });
}

/**
 * Bot API 模块导出
 */
export const botApi = {
  listBots,
  getBot,
  createBot,
  updateBot,
  deleteBot,
  connectBot,
  disconnectBot,
  getBotStatus,
};
