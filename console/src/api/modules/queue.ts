/**
 * 队列管理 API 模块
 * v4.0 新增 - 6 个 API 接口，与后端 routes/queue.py 完全匹配
 */
import { request } from "../request";
import type {
  MessageQueue,
  MessageQueueCreateRequest,
  MessageQueueUpdateRequest,
  QueueMessage,
  QueueStatsResponse,
  QueueDepthHistory,
  DeadLetterMessage,
  QueueConsumer,
  QueueAlertThreshold,
} from "../types/queue";

/**
 * 列出消息队列
 * @param tenantId 租户 ID（可选）
 * @param queueType 队列类型（可选）
 * @returns 消息队列列表
 */
export async function listMessageQueues(
  tenantId?: string,
  queueType?: string
): Promise<MessageQueue[]> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  if (queueType) {
    params.append("queue_type", queueType);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/queue${query}`);
}

/**
 * 查询队列详情
 * @param queueId 队列 ID
 * @returns 队列详情
 */
export async function getQueue(queueId: string): Promise<MessageQueue> {
  return request(`/queue/${queueId}`);
}

/**
 * 创建队列
 * @param data 队列创建请求
 * @returns 创建后的队列
 */
export async function createQueue(
  data: MessageQueueCreateRequest
): Promise<MessageQueue> {
  return request("/queue", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 更新队列
 * @param queueId 队列 ID
 * @param data 队列更新请求
 * @returns 更新后的队列
 */
export async function updateQueue(
  queueId: string,
  data: MessageQueueUpdateRequest
): Promise<MessageQueue> {
  return request(`/queue/${queueId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * 删除队列
 * @param queueId 队列 ID
 * @returns 操作结果
 */
export async function deleteQueue(queueId: string): Promise<{ message: string }> {
  return request(`/queue/${queueId}`, {
    method: "DELETE",
  });
}

/**
 * 查询队列状态
 * @param queueId 队列 ID
 * @returns 队列状态
 */
export async function getQueueStatus(queueId: string): Promise<MessageQueue> {
  return request(`/queue/${queueId}/status`);
}

/**
 * 查询队列统计
 * @param queueId 队列 ID
 * @returns 队列统计
 */
export async function getQueueStats(queueId: string): Promise<QueueStatsResponse> {
  return request(`/queue/${queueId}/stats`);
}

/**
 * 查询队列深度历史
 * @param queueId 队列 ID
 * @param startTime 开始时间
 * @param endTime 结束时间
 * @param aggregationInterval 聚合间隔（秒，默认 60）
 * @returns 队列深度历史
 */
export async function getQueueDepthHistory(
  queueId: string,
  startTime: string,
  endTime: string,
  aggregationInterval: number = 60
): Promise<QueueDepthHistory> {
  const params = new URLSearchParams({
    start_time: startTime,
    end_time: endTime,
    aggregation_interval_sec: aggregationInterval.toString(),
  });
  return request(`/queue/${queueId}/depth/history?${params.toString()}`);
}

/**
 * 列出队列消息
 * @param queueId 队列 ID
 * @param status 消息状态（可选）
 * @param limit 返回数量（默认 50）
 * @returns 队列消息列表
 */
export async function listQueueMessages(
  queueId: string,
  status?: string,
  limit: number = 50
): Promise<QueueMessage[]> {
  const params = new URLSearchParams({
    limit: limit.toString(),
  });
  if (status) {
    params.append("status", status);
  }
  return request(`/queue/${queueId}/messages?${params.toString()}`);
}

/**
 * 查询队列消息详情
 * @param queueId 队列 ID
 * @param messageId 消息 ID
 * @returns 队列消息详情
 */
export async function getQueueMessage(
  queueId: string,
  messageId: string
): Promise<QueueMessage> {
  return request(`/queue/${queueId}/messages/${messageId}`);
}

/**
 * 列出死信队列消息
 * @param queueId 队列 ID
 * @param limit 返回数量（默认 50）
 * @returns 死信队列消息列表
 */
export async function listDeadLetterMessages(
  queueId: string,
  limit: number = 50
): Promise<DeadLetterMessage[]> {
  const params = new URLSearchParams({
    limit: limit.toString(),
  });
  return request(`/queue/${queueId}/dead-letter?${params.toString()}`);
}

/**
 * 重新处理死信消息
 * @param queueId 队列 ID
 * @param messageId 消息 ID
 * @returns 操作结果
 */
export async function reprocessDeadLetterMessage(
  queueId: string,
  messageId: string
): Promise<{ message: string }> {
  return request(`/queue/${queueId}/dead-letter/${messageId}/reprocess`, {
    method: "POST",
  });
}

/**
 * 删除死信消息
 * @param queueId 队列 ID
 * @param messageId 消息 ID
 * @returns 操作结果
 */
export async function deleteDeadLetterMessage(
  queueId: string,
  messageId: string
): Promise<{ message: string }> {
  return request(`/queue/${queueId}/dead-letter/${messageId}`, {
    method: "DELETE",
  });
}

/**
 * 列出队列消费者
 * @param queueId 队列 ID
 * @returns 队列消费者列表
 */
export async function listQueueConsumers(queueId: string): Promise<QueueConsumer[]> {
  return request(`/queue/${queueId}/consumers`);
}

/**
 * 暂停队列
 * @param queueId 队列 ID
 * @returns 操作结果
 */
export async function pauseQueue(queueId: string): Promise<{ message: string }> {
  return request(`/queue/${queueId}/pause`, {
    method: "POST",
  });
}

/**
 * 恢复队列
 * @param queueId 队列 ID
 * @returns 操作结果
 */
export async function resumeQueue(queueId: string): Promise<{ message: string }> {
  return request(`/queue/${queueId}/resume`, {
    method: "POST",
  });
}

/**
 * 清空队列
 * @param queueId 队列 ID
 * @param status 消息状态过滤（可选）
 * @returns 操作结果
 */
export async function purgeQueue(
  queueId: string,
  status?: string
): Promise<{ message: string; purged_count: number }> {
  const params = new URLSearchParams();
  if (status) {
    params.append("status", status);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/queue/${queueId}/purge${query}`, {
    method: "POST",
  });
}

/**
 * 列出队列告警阈值
 * @param queueId 队列 ID
 * @returns 队列告警阈值列表
 */
export async function listQueueAlertThresholds(
  queueId: string
): Promise<QueueAlertThreshold[]> {
  return request(`/queue/${queueId}/alerts/thresholds`);
}

/**
 * 创建队列告警阈值
 * @param queueId 队列 ID
 * @param data 告警阈值创建请求
 * @returns 创建后的告警阈值
 */
export async function createQueueAlertThreshold(
  queueId: string,
  data: Omit<QueueAlertThreshold, "threshold_id" | "queue_id" | "created_at">
): Promise<QueueAlertThreshold> {
  return request(`/queue/${queueId}/alerts/thresholds`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 更新队列告警阈值
 * @param queueId 队列 ID
 * @param thresholdId 阈值 ID
 * @param data 告警阈值更新请求
 * @returns 更新后的告警阈值
 */
export async function updateQueueAlertThreshold(
  queueId: string,
  thresholdId: string,
  data: Partial<Omit<QueueAlertThreshold, "threshold_id" | "queue_id" | "created_at">>
): Promise<QueueAlertThreshold> {
  return request(`/queue/${queueId}/alerts/thresholds/${thresholdId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * 删除队列告警阈值
 * @param queueId 队列 ID
 * @param thresholdId 阈值 ID
 * @returns 操作结果
 */
export async function deleteQueueAlertThreshold(
  queueId: string,
  thresholdId: string
): Promise<{ message: string }> {
  return request(`/queue/${queueId}/alerts/thresholds/${thresholdId}`, {
    method: "DELETE",
  });
}

/**
 * 队列 API 模块导出
 */
export const queueApi = {
  listMessageQueues,
  listQueues: listMessageQueues,  // 别名，与后端匹配
  listQueueConfigs: listMessageQueues,  // 别名，与后端匹配
  getQueue,
  getQueueConfig: getQueue,  // 别名，与后端匹配
  createQueue,
  updateQueue,
  updateQueueConfig: updateQueue,  // 别名，与后端匹配
  deleteQueue,
  getQueueStatus,
  getQueueStats,
  getQueueDepthHistory,
  listQueueMessages,
  getQueueMessage,
  listDeadLetterMessages,
  reprocessDeadLetterMessage,
  deleteDeadLetterMessage,
  listQueueConsumers,
  pauseQueue,
  resumeQueue,
  purgeQueue,
  listQueueAlertThresholds,
  createQueueAlertThreshold,
  updateQueueAlertThreshold,
  deleteQueueAlertThreshold,
};
