/**
 * 认证状态管理 Store
 * v4.0 新增 - 管理用户认证状态（角色、租户 ID、用户 ID）
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

/** 用户角色类型 - 与后端 Python 实现完全匹配 */
export type UserRole = "tenant_admin" | "user" | "guest" | "system_admin";

/** 角色等级映射 - 用于权限比较 */
export const ROLE_HIERARCHY: Record<UserRole, number> = {
  guest: 0,
  user: 1,
  tenant_admin: 2,
  system_admin: 3,
};

/** 认证状态接口 */
interface AuthState {
  /** 用户角色 */
  userRole?: UserRole;
  /** 租户 ID */
  tenantId?: string;
  /** 用户 ID */
  userId?: string;
  /** 设置认证信息 */
  setAuthInfo: (role: UserRole, tenantId: string, userId: string) => void;
  /** 清除认证信息（登出） */
  clear: () => void;
  /** 检查是否有指定角色权限 */
  hasRole: (requiredRole: UserRole) => boolean;
  /** 检查是否有指定角色或更高权限 */
  hasRoleOrHigher: (requiredRole: UserRole) => boolean;
}

/**
 * 认证状态 Store
 * 使用 persist 中间件持久化到 localStorage
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      userRole: undefined,
      tenantId: undefined,
      userId: undefined,

      /**
       * 设置认证信息
       * @param role 用户角色
       * @param tenantId 租户 ID
       * @param userId 用户 ID
       */
      setAuthInfo: (role, tenantId, userId) => {
        set({ userRole: role, tenantId, userId });
      },

      /**
       * 清除认证信息（登出）
       */
      clear: () => {
        set({
          userRole: undefined,
          tenantId: undefined,
          userId: undefined,
        });
      },

      /**
       * 检查是否有指定角色
       * @param requiredRole 所需角色
       * @returns 是否有该角色
       */
      hasRole: (requiredRole: UserRole) => {
        const { userRole } = get();
        return userRole === requiredRole;
      },

      /**
       * 检查是否有指定角色或更高权限
       * @param requiredRole 所需角色
       * @returns 是否有该角色或更高权限
       */
      hasRoleOrHigher: (requiredRole: UserRole) => {
        const { userRole } = get();
        if (!userRole) return false;
        
        const userLevel = ROLE_HIERARCHY[userRole] ?? 0;
        const requiredLevel = ROLE_HIERARCHY[requiredRole] ?? 0;
        
        return userLevel >= requiredLevel;
      },
    }),
    {
      name: "copaw-auth-storage-v1",
    }
  )
);
