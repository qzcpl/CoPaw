/**
 * API 模块导出
 * v4.0 新增：频道架构重构相关 API 模块
 */

// 原有模块
export * from "./agents";
export * from "./channel";
export * from "./chat";
export * from "./mcp";
export * from "./skill";
export * from "./workspace";

// ✅ v4.0 新增：频道架构重构 API 模块
export * from "./auth";          // 认证
export * from "./callid";        // callId 管理
export * from "./bot";           // Bot 管理
export * from "./tenant";        // 租户管理
export * from "./monitor";       // 监控管理
export * from "./routing";       // 路由配置
export * from "./queue";         // 队列管理
export * from "./gray_release";  // 灰度发布
