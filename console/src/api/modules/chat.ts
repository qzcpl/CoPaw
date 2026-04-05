/**
 * 聊天 API 模块
 * v4.0 更新 - 新增发送消息、会话管理 API（与后端 routes/chat.py 完全匹配）
 */
import { request } from "../request";
import { getApiUrl, getApiToken } from "../config";
import { buildAuthHeaders } from "../authHeaders";
import type {
  ChatSpec,
  ChatHistory,
  ChatDeleteResponse,
  Session,
  BusMessageV3,
  SessionContextV2,
  SendMessageRequest,
  SendMessageResponse,
  SessionInfo,
  SessionListResponse,
} from "../types";

/** Response from POST /console/upload. url = filename only; agent_id from header. */
export interface ChatUploadResponse {
  url: string;
  file_name: string;
  stored_name?: string;
}

const FILES_PREVIEW = "/files/preview";

/**
 * 发送消息（v4.0 新增）
 * @param data 发送消息请求
 * @returns 发送结果
 */
export async function sendMessage(data: SendMessageRequest): Promise<SendMessageResponse> {
  return request("/chat/send", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * 获取会话详情（v4.0 更新）
 * @param sessionId 会话 ID
 * @param tenantId 租户 ID（可选）
 * @returns 会话详情（含 BusMessage v3 消息列表）
 */
export async function getSessionDetail(
  sessionId: string,
  tenantId?: string
): Promise<SessionContextV2 & { messages: BusMessageV3[] }> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/chat/sessions/${sessionId}${query}`);
}

/**
 * 列出会话（v4.0 更新）
 * @param tenantId 租户 ID（可选）
 * @param callId callId（可选）
 * @param status 会话状态（可选）
 * @param page 页码（默认 1）
 * @param pageSize 每页数量（默认 20）
 * @returns 会话列表（分页）
 */
export async function listSessions(
  tenantId?: string,
  callId?: string,
  status?: string,
  page: number = 1,
  pageSize: number = 20
): Promise<SessionListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  if (callId) {
    params.append("call_id", callId);
  }
  if (status) {
    params.append("status", status);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/chat/sessions${query}`);
}

/**
 * 删除会话（v4.0 新增）
 * @param sessionId 会话 ID
 * @param tenantId 租户 ID（可选）
 * @returns 操作结果
 */
export async function deleteSession(
  sessionId: string,
  tenantId?: string
): Promise<{ message: string }> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/chat/sessions/${sessionId}${query}`, {
    method: "DELETE",
  });
}

/**
 * 关闭会话（v4.0 新增）
 * @param sessionId 会话 ID
 * @param tenantId 租户 ID（可选）
 * @returns 操作结果
 */
export async function closeSession(
  sessionId: string,
  tenantId?: string
): Promise<{ message: string }> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/chat/sessions/${sessionId}/close${query}`, {
    method: "POST",
  });
}

/**
 * 暂停会话（v4.0 新增）
 * @param sessionId 会话 ID
 * @param tenantId 租户 ID（可选）
 * @returns 操作结果
 */
export async function pauseSession(
  sessionId: string,
  tenantId?: string
): Promise<{ message: string }> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/chat/sessions/${sessionId}/pause${query}`, {
    method: "POST",
  });
}

/**
 * 恢复会话（v4.0 新增）
 * @param sessionId 会话 ID
 * @param tenantId 租户 ID（可选）
 * @returns 操作结果
 */
export async function resumeSession(
  sessionId: string,
  tenantId?: string
): Promise<{ message: string }> {
  const params = new URLSearchParams();
  if (tenantId) {
    params.append("tenant_id", tenantId);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/chat/sessions/${sessionId}/resume${query}`, {
    method: "POST",
  });
}

/**
 * 获取会话历史消息（v4.0 新增）
 * @param sessionId 会话 ID
 * @param limit 返回消息数（默认 50）
 * @param before 在此时间之前（可选）
 * @returns 历史消息列表
 */
export async function getSessionHistory(
  sessionId: string,
  limit: number = 50,
  before?: string
): Promise<BusMessageV3[]> {
  const params = new URLSearchParams({
    limit: limit.toString(),
  });
  if (before) {
    params.append("before", before);
  }
  return request(`/chat/sessions/${sessionId}/history?${params.toString()}`);
}

// ── 保留原有 API（向后兼容） ─────────────────────────────────────────────────

export const legacyChatApi = {
  /** Upload a file for chat attachment. Returns URL path for content. */
  uploadFile: async (file: File): Promise<ChatUploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(getApiUrl("/console/upload"), {
      method: "POST",
      headers: buildAuthHeaders(),
      body: formData,
    });
    if (!response.ok) {
      const text = await response.text().catch(() => "");
      throw new Error(
        `Upload failed: ${response.status} ${response.statusText}${
          text ? ` - ${text}` : ""
        }`,
      );
    }
    return response.json();
  },

  filePreviewUrl: (filename: string): string => {
    if (!filename) return "";
    if (filename.startsWith("http://") || filename.startsWith("https://"))
      return filename;
    const path = `${FILES_PREVIEW}/${filename.replace(/^\/+/, "")}`;
    const url = getApiUrl(path);

    const token = getApiToken();
    if (token) {
      return `${url}?token=${encodeURIComponent(token)}`;
    }

    return url;
  },

  listChats: (params?: { user_id?: string; channel?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.user_id) searchParams.append("user_id", params.user_id);
    if (params?.channel) searchParams.append("channel", params.channel);
    const query = searchParams.toString();
    return request<ChatSpec[]>(`/chats${query ? `?${query}` : ""}`);
  },

  createChat: (chat: Partial<ChatSpec>) =>
    request<ChatSpec>("/chats", {
      method: "POST",
      body: JSON.stringify(chat),
    }),

  getChat: (chatId: string) =>
    request<ChatHistory>(`/chats/${encodeURIComponent(chatId)}`),

  updateChat: (chatId: string, chat: Partial<ChatSpec>) =>
    request<ChatSpec>(`/chats/${encodeURIComponent(chatId)}`, {
      method: "PUT",
      body: JSON.stringify(chat),
    }),

  deleteChat: (chatId: string) =>
    request<ChatDeleteResponse>(`/chats/${encodeURIComponent(chatId)}`, {
      method: "DELETE",
    }),

  batchDeleteChats: (chatIds: string[]) =>
    request<{ success: boolean; deleted_count: number }>(
      "/chats/batch-delete",
      {
        method: "POST",
        body: JSON.stringify(chatIds),
      },
    ),

  stopChat: (chatId: string) =>
    request<void>(`/console/chat/stop?chat_id=${encodeURIComponent(chatId)}`, {
      method: "POST",
    }),
};

/**
 * 聊天 API 模块导出
 */
export const chatApi = {
  // v4.0 新增 API
  sendMessage,
  getSessionDetail,
  listSessions,
  deleteSession,
  closeSession,
  pauseSession,
  resumeSession,
  getSessionHistory,

  // 保留原有 API（向后兼容）
  ...legacyChatApi,
};

/**
 * 会话 API 模块导出（别名）
 */
export const sessionApi = {
  list: listSessions,
  getDetail: getSessionDetail,
  delete: deleteSession,
  close: closeSession,
  pause: pauseSession,
  resume: resumeSession,
  getHistory: getSessionHistory,
};
