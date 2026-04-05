/**
 * API 错误类型定义
 * v4.0 新增 - 与后端 Python 错误码完全匹配
 */

/**
 * API 错误码枚举 - 与后端 core/exceptions.py 完全一致
 */
export enum ApiErrorCode {
  // 认证相关
  AUTH_FAILED = "AUTH_FAILED",
  TOKEN_EXPIRED = "TOKEN_EXPIRED",
  TOKEN_INVALID = "TOKEN_INVALID",
  PERMISSION_DENIED = "PERMISSION_DENIED",
  
  // callId 相关
  CALLID_ALREADY_BOUND = "CALLID_ALREADY_BOUND",
  CALLID_NOT_FOUND = "CALLID_NOT_FOUND",
  CALLID_SWITCH_FAILED = "CALLID_SWITCH_FAILED",
  CALLID_SUSPEND_FAILED = "CALLID_SUSPEND_FAILED",
  CALLID_RESUME_FAILED = "CALLID_RESUME_FAILED",
  
  // Bot 相关
  BOT_NOT_FOUND = "BOT_NOT_FOUND",
  BOT_ALREADY_EXISTS = "BOT_ALREADY_EXISTS",
  BOT_CONNECT_FAILED = "BOT_CONNECT_FAILED",
  
  // 租户相关
  TENANT_NOT_FOUND = "TENANT_NOT_FOUND",
  TENANT_ACCESS_DENIED = "TENANT_ACCESS_DENIED",
  TENANT_ALREADY_EXISTS = "TENANT_ALREADY_EXISTS",
  
  // 队列相关
  QUEUE_FULL = "QUEUE_FULL",
  QUEUE_NOT_FOUND = "QUEUE_NOT_FOUND",
  QUEUE_CONFIG_INVALID = "QUEUE_CONFIG_INVALID",
  
  // 监控相关
  METRIC_NOT_FOUND = "METRIC_NOT_FOUND",
  ALERT_NOT_FOUND = "ALERT_NOT_FOUND",
  
  // 路由相关
  ROUTING_STRATEGY_NOT_FOUND = "ROUTING_STRATEGY_NOT_FOUND",
  ROUTING_CONFIG_INVALID = "ROUTING_CONFIG_INVALID",
  
  // 通用
  INTERNAL_ERROR = "INTERNAL_ERROR",
  INVALID_PARAMS = "INVALID_PARAMS",
  NOT_FOUND = "NOT_FOUND",
  NOT_IMPLEMENTED = "NOT_IMPLEMENTED",
}

/**
 * 错误码分类
 */
export enum ErrorCategory {
  /** 认证错误 */
  AUTH = "AUTH",
  /** callId 相关错误 */
  CALLID = "CALLID",
  /** Bot 相关错误 */
  BOT = "BOT",
  /** 租户相关错误 */
  TENANT = "TENANT",
  /** 队列相关错误 */
  QUEUE = "QUEUE",
  /** 监控相关错误 */
  MONITOR = "MONITOR",
  /** 路由相关错误 */
  ROUTING = "ROUTING",
  /** 通用错误 */
  GENERAL = "GENERAL",
}

/**
 * 获取错误码对应的分类
 */
export function getErrorCategory(code: string): ErrorCategory {
  if (code.startsWith("AUTH_") || code.startsWith("TOKEN_")) {
    return ErrorCategory.AUTH;
  }
  if (code.startsWith("CALLID_")) {
    return ErrorCategory.CALLID;
  }
  if (code.startsWith("BOT_")) {
    return ErrorCategory.BOT;
  }
  if (code.startsWith("TENANT_")) {
    return ErrorCategory.TENANT;
  }
  if (code.startsWith("QUEUE_")) {
    return ErrorCategory.QUEUE;
  }
  if (code.startsWith("METRIC_") || code.startsWith("ALERT_")) {
    return ErrorCategory.MONITOR;
  }
  if (code.startsWith("ROUTING_")) {
    return ErrorCategory.ROUTING;
  }
  return ErrorCategory.GENERAL;
}

/**
 * 获取错误码的中文描述
 */
export function getErrorDescription(code: string): string {
  const descriptions: Record<string, string> = {
    [ApiErrorCode.AUTH_FAILED]: "认证失败",
    [ApiErrorCode.TOKEN_EXPIRED]: "Token 已过期",
    [ApiErrorCode.TOKEN_INVALID]: "Token 无效",
    [ApiErrorCode.PERMISSION_DENIED]: "权限不足",
    [ApiErrorCode.CALLID_ALREADY_BOUND]: "callId 已被绑定",
    [ApiErrorCode.CALLID_NOT_FOUND]: "callId 不存在",
    [ApiErrorCode.CALLID_SWITCH_FAILED]: "callId 切换失败",
    [ApiErrorCode.CALLID_SUSPEND_FAILED]: "callId 暂停失败",
    [ApiErrorCode.CALLID_RESUME_FAILED]: "callId 恢复失败",
    [ApiErrorCode.BOT_NOT_FOUND]: "Bot 不存在",
    [ApiErrorCode.BOT_ALREADY_EXISTS]: "Bot 已存在",
    [ApiErrorCode.BOT_CONNECT_FAILED]: "Bot 连接失败",
    [ApiErrorCode.TENANT_NOT_FOUND]: "租户不存在",
    [ApiErrorCode.TENANT_ACCESS_DENIED]: "租户访问被拒绝",
    [ApiErrorCode.TENANT_ALREADY_EXISTS]: "租户已存在",
    [ApiErrorCode.QUEUE_FULL]: "队列已满",
    [ApiErrorCode.QUEUE_NOT_FOUND]: "队列不存在",
    [ApiErrorCode.QUEUE_CONFIG_INVALID]: "队列配置无效",
    [ApiErrorCode.METRIC_NOT_FOUND]: "指标不存在",
    [ApiErrorCode.ALERT_NOT_FOUND]: "告警不存在",
    [ApiErrorCode.ROUTING_STRATEGY_NOT_FOUND]: "路由策略不存在",
    [ApiErrorCode.ROUTING_CONFIG_INVALID]: "路由配置无效",
    [ApiErrorCode.INTERNAL_ERROR]: "内部错误",
    [ApiErrorCode.INVALID_PARAMS]: "参数无效",
    [ApiErrorCode.NOT_FOUND]: "资源不存在",
    [ApiErrorCode.NOT_IMPLEMENTED]: "功能未实现",
  };
  
  return descriptions[code] || "未知错误";
}
