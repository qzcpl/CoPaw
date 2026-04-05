import { getApiToken } from "./config";

/**
 * 构建认证请求头
 * v4.0 改造 - 新增 X-Tenant-ID 头（从 localStorage 直接读取，避免循环依赖）
 * 
 * @returns 认证请求头对象
 */
export function buildAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {};
  
  // 添加 Authorization Token
  const token = getApiToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  
  // 添加 X-Agent-Id（从 sessionStorage 读取）
  try {
    const agentStorage = sessionStorage.getItem("copaw-agent-storage");
    if (agentStorage) {
      const parsed = JSON.parse(agentStorage);
      const selectedAgent = parsed?.state?.selectedAgent;
      if (selectedAgent) {
        headers["X-Agent-Id"] = selectedAgent;
      }
    }
  } catch (error) {
    console.warn("Failed to get selected agent from storage:", error);
  }
  
  // ✅ v4.0 新增：添加 X-Tenant-ID（直接从 localStorage 读取，避免循环依赖）
  try {
    const tenantStorage = localStorage.getItem("copaw-tenant-storage-v1");
    if (tenantStorage) {
      const parsed = JSON.parse(tenantStorage);
      const currentTenantId = parsed?.state?.currentTenantId;
      if (currentTenantId) {
        headers["X-Tenant-ID"] = currentTenantId;
      }
    }
  } catch (error) {
    console.warn("Failed to get tenant ID from storage:", error);
  }
  
  return headers;
}
