/**
 * 租户状态管理 Store
 * v4.0 新增 - 管理当前租户状态
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

/** 租户信息接口 - 与后端 Schema 匹配 */
export interface TenantInfo {
  tenant_id: string;
  tenant_name: string;
  status: string;
  max_agents?: number;
  max_callids?: number;
}

/** 租户状态接口 */
interface TenantState {
  /** 当前租户 ID */
  currentTenantId?: string;
  /** 当前租户信息 */
  currentTenant?: TenantInfo;
  /** 可用租户列表 */
  availableTenants: TenantInfo[];
  /** 设置当前租户 */
  setTenant: (tenantId: string, tenantInfo?: TenantInfo) => void;
  /** 设置可用租户列表 */
  setAvailableTenants: (tenants: TenantInfo[]) => void;
  /** 清除租户信息 */
  clear: () => void;
}

/**
 * 租户状态 Store
 * 使用 persist 中间件持久化到 localStorage
 */
export const useTenantStore = create<TenantState>()(
  persist(
    (set) => ({
      currentTenantId: undefined,
      currentTenant: undefined,
      availableTenants: [],

      /**
       * 设置当前租户
       * @param tenantId 租户 ID
       * @param tenantInfo 租户信息（可选）
       */
      setTenant: (tenantId, tenantInfo) => {
        set({
          currentTenantId: tenantId,
          currentTenant: tenantInfo,
        });
      },

      /**
       * 设置可用租户列表
       * @param tenants 租户列表
       */
      setAvailableTenants: (tenants) => {
        set({ availableTenants: tenants });
      },

      /**
       * 清除租户信息
       */
      clear: () => {
        set({
          currentTenantId: undefined,
          currentTenant: undefined,
        });
      },
    }),
    {
      name: "copaw-tenant-storage-v1",
    }
  )
);
