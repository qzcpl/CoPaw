/**
 * JWT 认证工具
 * v4.0 新增 - 用于解码后端 JWT Token
 */
import { jwtDecode } from "jwt-decode";

/** JWT Payload 接口 - 与后端 Python 实现完全匹配 */
export interface JWTPayload {
  sub: string;        // user_id
  tenant_id: string;  // 租户 ID
  role: "tenant_admin" | "user" | "guest" | "system_admin";  // UserRole
  exp: number;        // 过期时间（秒）
  iat: number;        // 签发时间（秒）
}

/**
 * 解码 JWT Token
 * @param token JWT Token 字符串
 * @returns 解码后的 Payload
 */
export function decodeToken(token: string): JWTPayload {
  return jwtDecode<JWTPayload>(token);
}

/**
 * 验证 Token 是否有效（检查过期时间）
 * @param token JWT Token 字符串
 * @returns Token 是否有效
 */
export function verifyToken(token: string): boolean {
  try {
    const payload = decodeToken(token);
    // 检查过期时间（exp 是秒，需要乘以 1000 转换为毫秒）
    return payload.exp * 1000 > Date.now();
  } catch {
    return false;
  }
}

/**
 * 获取 Token 中的租户 ID
 * @param token JWT Token 字符串
 * @returns 租户 ID，如果无效则返回 null
 */
export function getTenantIdFromToken(token: string): string | null {
  try {
    const payload = decodeToken(token);
    return payload.tenant_id || null;
  } catch {
    return null;
  }
}

/**
 * 获取 Token 中的用户角色
 * @param token JWT Token 字符串
 * @returns 用户角色，如果无效则返回 null
 */
export function getRoleFromToken(token: string): string | null {
  try {
    const payload = decodeToken(token);
    return payload.role || null;
  } catch {
    return null;
  }
}

/**
 * 获取 Token 中的用户 ID
 * @param token JWT Token 字符串
 * @returns 用户 ID，如果无效则返回 null
 */
export function getUserIdFromToken(token: string): string | null {
  try {
    const payload = decodeToken(token);
    return payload.sub || null;
  } catch {
    return null;
  }
}

/**
 * 检查 Token 是否即将过期（5 分钟内）
 * @param token JWT Token 字符串
 * @returns 是否即将过期
 */
export function isTokenExpiringSoon(token: string, thresholdMinutes: number = 5): boolean {
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
