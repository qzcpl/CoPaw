/**
 * 租户管理 API 模块
 * v4.0 新增 - 6 个 API 接口，与后端 routes/tenant.py 完全匹配
 */
import { request } from "../request";
import type {
  TenantInfo,
  TenantCreateRequest,
  TenantUpdateRequest,
  TenantStatsResponse,
} from "../types/tenant";

/**
 * 列出租户列表
 * @returns 租户列表
 */
export async function listTenants(): Promise<TenantInfo[]> {
  return request("/tenants");
}

/**
 * 查询租户详情
 * @param tenantId 租户 ID
 * @returns 租户详情
 */
export async function getTenant(tenantId: string): Promise<TenantInfo> {
  return request(`/tenants/${tenantId}`);
}

/**
 * 创建租户
 * @param data 租户创建请求
 * @returns 创建后的租户信息
 */
export async function createTenant(data: TenantCreateRequest): Promise<TenantInfo> {
  return request("/tenants", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 更新租户
 * @param tenantId 租户 ID
 * @param data 租户更新请求
 * @returns 更新后的租户信息
 */
export async function updateTenant(
  tenantId: string,
  data: TenantUpdateRequest
): Promise<TenantInfo> {
  return request(`/tenants/${tenantId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * 删除租户
 * @param tenantId 租户 ID
 * @returns 操作结果
 */
export async function deleteTenant(tenantId: string): Promise<{ message: string }> {
  return request(`/tenants/${tenantId}`, {
    method: "DELETE",
  });
}

/**
 * 查询租户统计
 * @param tenantId 租户 ID
 * @returns 租户统计信息
 */
export async function getTenantStats(tenantId: string): Promise<TenantStatsResponse> {
  return request(`/tenants/${tenantId}/stats`);
}

/**
 * 租户 API 模块导出
 */
export const tenantApi = {
  listTenants,
  getTenant,
  createTenant,
  updateTenant,
  deleteTenant,
  getTenantStats,
};
