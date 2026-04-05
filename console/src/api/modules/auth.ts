/**
 * 认证 API 模块
 * v4.0 新增 - 4 个 API 接口，与后端 routes/auth.py 完全匹配
 */
import { request } from "../request";
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  RefreshTokenResponse,
  UserInfoResponse,
  AuthStatusResponse,
} from "../types/auth";
import { setAuthToken, clearAuthToken } from "../config";
import { decodeToken, verifyToken } from "../auth";
import { useAuthStore } from "../../stores/authStore";
import { useTenantStore } from "../../stores/tenantStore";

/**
 * 用户登录
 * @param data 登录请求
 * @returns 登录响应（自动存储 Token 和认证信息）
 */
export async function login(data: LoginRequest): Promise<LoginResponse>;
/**
 * 用户登录（兼容旧调用方式）
 * @param username 用户名
 * @param password 密码
 * @returns 登录响应
 */
export async function login(username: string, password: string): Promise<LoginResponse>;
export async function login(dataOrUsername: LoginRequest | string, password?: string): Promise<LoginResponse> {
  // 兼容旧调用方式：login(username, password)
  const data: LoginRequest = typeof dataOrUsername === 'string' 
    ? { username: dataOrUsername, password: password! }
    : dataOrUsername;

  const response = await request<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });

  // 存储 Token（兼容 token 和 access_token 字段）
  const token = response.token || response.access_token;
  if (token) {
    setAuthToken(token);

    // 解码 Token 提取信息
    const payload = decodeToken(token);

    // 更新认证状态
    useAuthStore.getState().setAuthInfo(
      payload.role,
      payload.tenant_id,
      payload.sub
    );

    // 更新租户状态
    useTenantStore.getState().setTenant(payload.tenant_id);
  }

  return response;
}

/**
 * 用户注册
 * @param data 注册请求
 * @returns 注册响应
 */
export async function register(data: RegisterRequest): Promise<RegisterResponse>;
/**
 * 用户注册（兼容旧调用方式）
 * @param username 用户名
 * @param password 密码
 * @returns 注册响应
 */
export async function register(username: string, password: string): Promise<RegisterResponse>;
export async function register(dataOrUsername: RegisterRequest | string, password?: string): Promise<RegisterResponse> {
  // 兼容旧调用方式：register(username, password)
  const data: RegisterRequest = typeof dataOrUsername === 'string'
    ? { username: dataOrUsername, password: password! }
    : dataOrUsername;

  const response = await request<RegisterResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });

  // 存储 Token（兼容 token 和 access_token 字段）
  const token = response.token || response.access_token;
  if (token) {
    setAuthToken(token);
  }

  return response;
}

/**
 * 刷新 Token
 * @param refreshToken 刷新 Token
 * @returns 新的 Token
 */
export async function refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
  const response = await request<RefreshTokenResponse>("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  // 更新 Token
  if (response.access_token) {
    setAuthToken(response.access_token);

    // 解码 Token 提取信息
    const payload = decodeToken(response.access_token);

    // 更新认证状态
    useAuthStore.getState().setAuthInfo(
      payload.role,
      payload.tenant_id,
      payload.sub
    );
  }

  return response;
}

/**
 * 获取当前用户信息
 * @returns 用户信息
 */
export async function getCurrentUserInfo(): Promise<UserInfoResponse> {
  return request<UserInfoResponse>("/auth/me");
}

/**
 * 用户登出
 */
export function logout(): void {
  // 清除 Token
  clearAuthToken();

  // 清除认证状态
  useAuthStore.getState().clear();

  // 清除租户状态
  useTenantStore.getState().clear();
}

/**
 * 检查 Token 是否有效
 * @returns Token 是否有效
 */
export function isTokenValid(): boolean {
  const token = localStorage.getItem("copaw_auth_token");
  if (!token) return false;
  return verifyToken(token);
}

/**
 * 检查 Token 是否即将过期
 * @param thresholdMinutes 阈值（分钟，默认 5 分钟）
 * @returns 是否即将过期
 */
export function isTokenExpiringSoon(thresholdMinutes: number = 5): boolean {
  const token = localStorage.getItem("copaw_auth_token");
  if (!token) return true;
  
  try {
    const payload = decodeToken(token);
    const now = Date.now();
    const expTime = payload.exp * 1000;
    const threshold = thresholdMinutes * 60 * 1000;
    return expTime - now < threshold;
  } catch {
    return true;
  }
}

/**
 * 获取认证状态
 * @returns 认证状态
 */
export async function getStatus(): Promise<AuthStatusResponse> {
  try {
    const response = await request<AuthStatusResponse>("/auth/status", {
      method: "GET",
    });
    return { ...response, authenticated: true };
  } catch {
    return { authenticated: false, enabled: false, has_users: false };
  }
}

/**
 * 更新用户资料
 * @param data 更新数据
 * @returns 更新后的用户信息
 */
export async function updateProfile(data: {
  username?: string;
  email?: string;
  avatar_url?: string;
  phone?: string;
  department?: string;
  position?: string;
}): Promise<UserInfoResponse>;
/**
 * 更新用户资料（兼容旧调用方式）
 * @param currentPassword 当前密码
 * @param username 新用户名
 * @param password 新密码
 * @returns 更新后的用户信息
 */
export async function updateProfile(currentPassword: string, username?: string, password?: string): Promise<UserInfoResponse>;
export async function updateProfile(
  dataOrPassword: { username?: string; email?: string; avatar_url?: string; phone?: string; department?: string; position?: string } | string,
  username?: string,
  password?: string
): Promise<UserInfoResponse> {
  // 兼容旧调用方式：updateProfile(currentPassword, username, password)
  if (typeof dataOrPassword === 'string') {
    const currentPassword = dataOrPassword;
    const data: any = { 
      current_password: currentPassword,
    };
    if (username) data.username = username;
    if (password) data.new_password = password;
    return request<UserInfoResponse>("/auth/me", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }
  
  // 新调用方式：updateProfile(data)
  return request<UserInfoResponse>("/auth/me", {
    method: "PUT",
    body: JSON.stringify(dataOrPassword),
  });
}

/**
 * 认证 API 模块导出
 */
export const authApi = {
  login,
  register,
  refreshToken,
  getCurrentUserInfo,
  getStatus,
  updateProfile,
  logout,
  isTokenValid,
  isTokenExpiringSoon,
};
