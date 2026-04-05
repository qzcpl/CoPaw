/**
 * 认证相关类型定义
 * v4.0 新增 - 与后端 Python Schema 完全匹配
 */

/** 用户角色 */
export type UserRole = "tenant_admin" | "user" | "guest" | "system_admin";

/**
 * 登录请求 - 与后端 LoginRequest 完全匹配
 */
export interface LoginRequest {
  /** 用户名或邮箱 */
  username: string;
  /** 密码 */
  password: string;
  /** 租户 ID（可选，多租户场景） */
  tenant_id?: string;
  /** 记住我（可选） */
  remember_me?: boolean;
}

/**
 * 登录响应 - 与后端 LoginResponse 完全匹配
 */
export interface LoginResponse {
  /** Token（后端字段） */
  token: string;
  /** Token 类型 */
  token_type?: string;
  /** 用户 ID（后端字段） */
  user_id?: string;
  /** 租户 ID（后端字段） */
  tenant_id?: string;
  /** 角色（后端字段） */
  role?: string;
  // ===== 兼容字段（可选，用于旧代码）=====
  access_token?: string;
  refresh_token?: string;
  expires_in?: number;
  user_info?: UserInfo;
}

/**
 * 注册请求 - 与后端 RegisterRequest 完全匹配
 */
export interface RegisterRequest {
  /** 用户名 */
  username: string;
  /** 邮箱（可选，前端需要但后端不需要） */
  email?: string;
  /** 密码 */
  password: string;
  /** 租户 ID（可选） */
  tenant_id?: string;
  /** 邀请码（可选） */
  invite_code?: string;
}

/**
 * 注册响应 - 与后端 RegisterResponse 完全匹配
 * 后端返回 LoginResponse 格式
 */
export interface RegisterResponse {
  /** Token（后端字段） */
  token?: string;
  /** Token 类型 */
  token_type?: string;
  /** 用户 ID（后端字段） */
  user_id?: string;
  /** 租户 ID（后端字段） */
  tenant_id?: string;
  /** 角色（后端字段） */
  role?: string;
  // ===== 兼容字段（可选，用于旧代码）=====
  username?: string;
  email?: string;
  created_at?: string;
  access_token?: string;
  refresh_token?: string;
}

/**
 * 刷新 Token 响应 - 与后端 RefreshTokenResponse 完全匹配
 */
export interface RefreshTokenResponse {
  /** 访问 Token */
  access_token: string;
  /** 刷新 Token */
  refresh_token: string;
  /** Token 类型 */
  token_type: "Bearer";
  /** 过期时间（秒） */
  expires_in: number;
}

/**
 * 用户信息响应 - 与后端 UserInfoResponse 完全匹配
 */
export interface UserInfoResponse {
  /** 用户 ID */
  user_id: string;
  /** 用户名 */
  username: string;
  /** 邮箱 */
  email: string;
  /** 角色 */
  role: UserRole;
  /** 租户 ID */
  tenant_id: string;
  /** 租户名称 */
  tenant_name?: string;
  /** 头像 URL（可选） */
  avatar_url?: string;
  /** 手机号（可选） */
  phone?: string;
  /** 部门（可选） */
  department?: string;
  /** 职位（可选） */
  position?: string;
  /** 创建时间 */
  created_at: string;
  /** 最后登录时间（可选） */
  last_login_at?: string;
  /** 是否激活 */
  is_active: boolean;
  /** 是否验证邮箱 */
  is_email_verified: boolean;
}

/**
 * 用户信息（登录响应中）
 */
export interface UserInfo {
  /** 用户 ID */
  user_id: string;
  /** 用户名 */
  username: string;
  /** 邮箱 */
  email: string;
  /** 角色 */
  role: UserRole;
  /** 租户 ID */
  tenant_id: string;
  /** 头像 URL（可选） */
  avatar_url?: string;
}

/**
 * 认证状态响应（前端自定义，用于 getStatus）
 */
export interface AuthStatusResponse {
  /** 是否已认证 */
  authenticated: boolean;
  /** 用户信息（可选） */
  user?: UserInfoResponse;
  /** 认证是否启用（可选） */
  enabled?: boolean;
  /** 是否有用户（可选，用于首次登录判断） */
  has_users?: boolean;
}

/**
 * 修改密码请求 - 与后端 ChangePasswordRequest 完全匹配
 */
export interface ChangePasswordRequest {
  /** 当前密码 */
  current_password: string;
  /** 新密码 */
  new_password: string;
}

/**
 * 重置密码请求 - 与后端 ResetPasswordRequest 完全匹配
 */
export interface ResetPasswordRequest {
  /** 邮箱 */
  email: string;
}

/**
 * 确认重置密码请求 - 与后端 ConfirmResetPasswordRequest 完全匹配
 */
export interface ConfirmResetPasswordRequest {
  /** Token */
  token: string;
  /** 新密码 */
  new_password: string;
}

/**
 * JWT Payload 接口 - 与后端 Python 实现完全匹配
 */
export interface JWTPayload {
  /** 用户 ID（sub） */
  sub: string;
  /** 租户 ID */
  tenant_id: string;
  /** 用户角色（后端返回 string，兼容 UserRole） */
  role: string | UserRole;
  /** 过期时间（秒） */
  exp: number;
  /** 签发时间（秒） */
  iat: number;
  /** Token 类型 */
  type?: "access" | "refresh";
  /** 权限列表（可选） */
  permissions?: string[];
}

/**
 * 权限定义
 */

export enum Permission {
  // 频道权限
  CHANNEL_READ = "channel:read",
  CHANNEL_WRITE = "channel:write",
  CHANNEL_DELETE = "channel:delete",
  
  // callId 权限
  CALLID_READ = "callid:read",
  CALLID_WRITE = "callid:write",
  CALLID_DELETE = "callid:delete",
  
  // Bot 权限
  BOT_READ = "bot:read",
  BOT_WRITE = "bot:write",
  BOT_DELETE = "bot:delete",
  
  // 租户权限
  TENANT_READ = "tenant:read",
  TENANT_WRITE = "tenant:write",
  TENANT_DELETE = "tenant:delete",
  
  // 监控权限
  MONITOR_READ = "monitor:read",
  MONITOR_WRITE = "monitor:write",
  
  // 路由权限
  ROUTING_READ = "routing:read",
  ROUTING_WRITE = "routing:write",
  
  // 队列权限
  QUEUE_READ = "queue:read",
  QUEUE_WRITE = "queue:write",
  
  // 系统权限
  SYSTEM_ADMIN = "system:admin",
  USER_MANAGEMENT = "user:manage",
}

/**
 * 角色权限映射
 */
export const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  guest: [
    Permission.CHANNEL_READ,
    Permission.CALLID_READ,
  ],
  user: [
    Permission.CHANNEL_READ,
    Permission.CHANNEL_WRITE,
    Permission.CALLID_READ,
    Permission.CALLID_WRITE,
    Permission.BOT_READ,
    Permission.MONITOR_READ,
    Permission.QUEUE_READ,
  ],
  tenant_admin: [
    Permission.CHANNEL_READ,
    Permission.CHANNEL_WRITE,
    Permission.CHANNEL_DELETE,
    Permission.CALLID_READ,
    Permission.CALLID_WRITE,
    Permission.CALLID_DELETE,
    Permission.BOT_READ,
    Permission.BOT_WRITE,
    Permission.BOT_DELETE,
    Permission.TENANT_READ,
    Permission.MONITOR_READ,
    Permission.MONITOR_WRITE,
    Permission.ROUTING_READ,
    Permission.ROUTING_WRITE,
    Permission.QUEUE_READ,
    Permission.QUEUE_WRITE,
  ],
  system_admin: [
    Permission.CHANNEL_READ,
    Permission.CHANNEL_WRITE,
    Permission.CHANNEL_DELETE,
    Permission.CALLID_READ,
    Permission.CALLID_WRITE,
    Permission.CALLID_DELETE,
    Permission.BOT_READ,
    Permission.BOT_WRITE,
    Permission.BOT_DELETE,
    Permission.TENANT_READ,
    Permission.TENANT_WRITE,
    Permission.TENANT_DELETE,
    Permission.MONITOR_READ,
    Permission.MONITOR_WRITE,
    Permission.ROUTING_READ,
    Permission.ROUTING_WRITE,
    Permission.QUEUE_READ,
    Permission.QUEUE_WRITE,
    Permission.SYSTEM_ADMIN,
    Permission.USER_MANAGEMENT,
  ],
};

/**
 * 检查角色是否有指定权限
 */
export function hasPermission(role: UserRole, permission: Permission): boolean {
  const permissions = ROLE_PERMISSIONS[role] || [];
  return permissions.includes(permission);
}

/**
 * 检查角色是否有所有指定权限
 */
export function hasAllPermissions(role: UserRole, permissions: Permission[]): boolean {
  const rolePermissions = ROLE_PERMISSIONS[role] || [];
  return permissions.every(p => rolePermissions.includes(p));
}
