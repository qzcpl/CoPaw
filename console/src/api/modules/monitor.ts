/**
 * 监控 API 模块
 * v4.0 新增 - 7 个 API 接口，与后端 routes/monitor.py 完全匹配
 */
import { request } from "../request";

/**
 * 指标接口
 */
export interface MonitorMetric {
  metric_id: string;
  metric_name: string;
  metric_type: string;
  value: number;
  unit: string;
  timestamp: string;
  labels?: Record<string, string>;
}

/**
 * 告警接口
 */
export interface MonitorAlert {
  alert_id: string;
  alert_name: string;
  metric_id: string;
  threshold: number;
  operator: string;
  severity: "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  status: "active" | "resolved" | "muted";
  channels: string[];
  created_at: string;
  triggered_at?: string;
  resolved_at?: string;
}

/**
 * 告警创建请求
 */
export interface AlertCreateRequest {
  alert_name: string;
  metric_id: string;
  threshold: number;
  operator: string;
  severity: "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  channels: string[];
}

/**
 * 告警更新请求
 */
export interface AlertUpdateRequest {
  alert_name?: string;
  threshold?: number;
  operator?: string;
  severity?: "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  channels?: string[];
}

/**
 * 获取系统指标
 * @param tenantId 租户 ID（可选）
 * @returns 指标列表
 */
export async function getMetrics(tenantId?: string): Promise<MonitorMetric[]> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/monitor/metrics${query}`);
}

/**
 * 获取指标详情
 * @param metricId 指标 ID
 * @returns 指标详情
 */
export async function getMetric(metricId: string): Promise<MonitorMetric> {
  return request(`/monitor/metrics/${metricId}`);
}

/**
 * 列出告警
 * @param tenantId 租户 ID（可选）
 * @param status 告警状态（可选）
 * @returns 告警列表
 */
export async function listAlerts(
  tenantId?: string,
  status?: string
): Promise<MonitorAlert[]> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  if (status) {
    params.append("status", status);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/monitor/alerts${query}`);
}

/**
 * 获取告警详情
 * @param alertId 告警 ID
 * @returns 告警详情
 */
export async function getAlert(alertId: string): Promise<MonitorAlert> {
  return request(`/monitor/alerts/${alertId}`);
}

/**
 * 创建告警
 * @param data 告警创建请求
 * @returns 创建后的告警信息
 */
export async function createAlert(data: AlertCreateRequest): Promise<MonitorAlert> {
  return request("/monitor/alerts", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 更新告警
 * @param alertId 告警 ID
 * @param data 告警更新请求
 * @returns 更新后的告警信息
 */
export async function updateAlert(
  alertId: string,
  data: AlertUpdateRequest
): Promise<MonitorAlert> {
  return request(`/monitor/alerts/${alertId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * 删除告警
 * @param alertId 告警 ID
 * @returns 操作结果
 */
export async function deleteAlert(alertId: string): Promise<{ message: string }> {
  return request(`/monitor/alerts/${alertId}`, {
    method: "DELETE",
  });
}

/**
 * 监控 API 模块导出
 */
export const monitorApi = {
  getMetrics,
  getMetric,
  listAlerts,
  getAlert,
  createAlert,
  updateAlert,
  deleteAlert,
};
