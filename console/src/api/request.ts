/**
 * API 请求封装
 * v4.0 改造 - 新增 tenant_id 传递和结构化错误处理
 */
import { getApiUrl, clearAuthToken } from "./config";
import { buildAuthHeaders } from "./authHeaders";

/**
 * API 错误接口 - 与后端 Python 实现完全匹配
 */
export interface ApiErrorBody {
  code: string;
  message: string;
  details?: Record<string, any>;
  path?: string;
}

/**
 * API 错误类 - 支持结构化错误信息
 */
export class ApiError extends Error {
  /** 错误码（如 CALLID_NOT_FOUND） */
  code: string;
  /** 错误详情 */
  details?: Record<string, any>;
  /** 请求路径 */
  path?: string;

  constructor(code: string, message: string, details?: Record<string, any>, path?: string) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.details = details;
    this.path = path;
  }
}

/**
 * 从响应体提取错误消息
 */
function getErrorMessageFromBody(
  text: string,
  contentType: string,
): string | null {
  if (!text) {
    return null;
  }

  if (!contentType.includes("application/json")) {
    return text;
  }

  try {
    const payload = JSON.parse(text) as {
      detail?: unknown;
      message?: unknown;
      error?: unknown;
    };

    if (typeof payload.detail === "string" && payload.detail) {
      return payload.detail;
    }
    if (typeof payload.message === "string" && payload.message) {
      return payload.message;
    }
    if (typeof payload.error === "string" && payload.error) {
      return payload.error;
    }
  } catch {
    return text;
  }

  return text;
}

/**
 * 构建请求头
 * ✅ v4.0 改造：authHeaders.ts 中已添加 X-Tenant-ID
 */
function buildHeaders(method?: string, extra?: HeadersInit): Headers {
  // Normalize extra to a Headers instance for consistent handling
  const headers = extra instanceof Headers ? extra : new Headers(extra);

  // Only add Content-Type for methods that typically have a body
  if (method && ["POST", "PUT", "PATCH"].includes(method.toUpperCase())) {
    // Don't override if caller explicitly set Content-Type
    if (!headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
  }

  // ✅ v4.0: authHeaders.ts 中已添加 X-Tenant-ID（从 localStorage 读取）
  for (const [key, value] of Object.entries(buildAuthHeaders())) {
    if (!headers.has(key)) {
      headers.set(key, value);
    }
  }

  return headers;
}

/**
 * API 请求函数
 * @param path API 路径
 * @param options 请求选项
 * @returns 响应数据
 */
export async function request<T = unknown>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = getApiUrl(path);
  const method = options.method || "GET";
  const headers = buildHeaders(method, options.headers);

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    // Handle 401: clear token and redirect to login
    if (response.status === 401) {
      clearAuthToken();
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
      throw new ApiError("AUTH_FAILED", "Not authenticated");
    }

    // 尝试解析结构化错误响应
    const text = await response.text().catch(() => "");
    const contentType = response.headers.get("content-type") || "";
    
    // 尝试解析后端返回的结构化错误
    let apiError: ApiError | null = null;
    if (contentType.includes("application/json")) {
      try {
        const errorBody: ApiErrorBody = JSON.parse(text);
        if (errorBody.code && errorBody.message) {
          apiError = new ApiError(
            errorBody.code,
            errorBody.message,
            errorBody.details,
            errorBody.path
          );
        }
      } catch {
        // 解析失败，使用普通错误
      }
    }

    // 如果有结构化错误，抛出 ApiError
    if (apiError) {
      throw apiError;
    }

    // 否则使用传统错误处理
    const errorMessage = getErrorMessageFromBody(text, contentType);
    throw new Error(
      errorMessage || `Request failed: ${response.status} ${response.statusText}`
    );
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  // Parse JSON response
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return (await response.text()) as unknown as T;
  }

  return (await response.json()) as T;
}
