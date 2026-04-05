/**
 * callId 管理 API 模块
 * v4.0 新增 - 8 个 API 接口，与后端 routes/callid.py 完全匹配
 */
import { request } from "../request";
import type {
  CallIdBinding,
  CallIdBindRequest,
  CallIdUnbindRequest,
  CallIdSwitchRequest,
  CallIdSuspendRequest,
  CallIdResumeRequest,
  CallIdChangeRecord,
} from "../types/callid";

/**
 * 列出 callId 绑定列表
 * @param tenantId 租户 ID（可选，默认使用当前租户）
 * @returns callId 绑定列表
 */
export async function listCallIdBindings(tenantId?: string): Promise<CallIdBinding[]> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/callid/bindings${query}`);
}

/**
 * 查询 callId 详情
 * @param callId callId
 * @param tenantId 租户 ID（可选）
 * @returns callId 绑定详情
 */
export async function getCallIdBinding(
  callId: string,
  tenantId?: string
): Promise<CallIdBinding> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/callid/bindings/${callId}${query}`);
}

/**
 * 绑定 callId
 * @param data 绑定请求
 * @returns 绑定后的 callId 信息
 */
export async function bindCallId(data: CallIdBindRequest): Promise<CallIdBinding> {
  return request("/callid/bind", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 解绑 callId
 * @param data 解绑请求
 * @returns 操作结果
 */
export async function unbindCallId(data: CallIdUnbindRequest): Promise<{ message: string }> {
  return request("/callid/unbind", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 切换 Agent（携号转网）
 * @param data 切换请求
 * @returns 操作结果
 */
export async function switchAgent(data: CallIdSwitchRequest): Promise<{ message: string }> {
  return request("/callid/switch", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 暂停 callId
 * @param callId callId
 * @param data 暂停请求
 * @returns 操作结果
 */
export async function suspendCallId(
  callId: string,
  data: CallIdSuspendRequest
): Promise<{ message: string }> {
  return request(`/callid/bindings/${callId}/suspend`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 恢复 callId
 * @param callId callId
 * @param data 恢复请求
 * @returns 操作结果
 */
export async function resumeCallId(
  callId: string,
  data: CallIdResumeRequest
): Promise<{ message: string }> {
  return request(`/callid/bindings/${callId}/resume`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 查询 callId 变更历史
 * @param callId callId
 * @param tenantId 租户 ID
 * @param limit 返回记录数（默认 50）
 * @returns 变更历史记录
 */
export async function getCallIdHistory(
  callId: string,
  tenantId: string,
  limit: number = 50
): Promise<CallIdChangeRecord[]> {
  const params = new URLSearchParams({
    call_id: callId,
    tenant_id: tenantId,
    limit: limit.toString(),
  });
  return request(`/callid/history?${params.toString()}`);
}

/**
 * callId API 模块导出
 */
export const callIdApi = {
  listCallIdBindings,
  getCallIdBinding,
  bindCallId,
  unbindCallId,
  switchAgent,
  suspendCallId,
  resumeCallId,
  getCallIdHistory,
};
