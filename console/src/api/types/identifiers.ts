/**
 * 六层标识体系类型定义
 * v4.0 新增 - 核心标识符体系（与后端 Python 实现完全匹配）
 * 
 * 六层标识体系：
 * 1. channel_id - 频道 ID（如 dingtalk、feishu）
 * 2. channel_type - 频道类型（如 dingtalk_robot、feishu_bot）
 * 3. channel_instance_id - 频道实例 ID（多租户场景）
 * 4. caller_logical_id - 调用方逻辑 ID（群 ID 或用户 ID）
 * 5. caller_physical_id - 调用方物理 ID（实际发送者 ID，群聊场景使用）
 * 6. called_id - 被叫 ID（callId，如 400-001）
 */

/**
 * 频道标识符
 */
export interface ChannelIdentifier {
  /** 频道 ID（如 dingtalk） */
  channel_id: string;
  /** 频道类型（如 dingtalk_robot） */
  channel_type: string;
  /** 频道实例 ID（多租户场景，可选） */
  channel_instance_id?: string;
}

/**
 * 调用方标识符（双层设计，支持群聊）
 */
export interface CallerIdentifier {
  /** 调用方逻辑 ID（群 ID 或用户 ID） */
  logical_id: string;
  /** 调用方物理 ID（实际发送者 ID，群聊场景必填） */
  physical_id?: string;
}

/**
 * 被叫方标识符
 */
export interface CalledIdentifier {
  /** 被叫 ID（callId，如 400-001） */
  called_id: string;
  /** callId 类型 */
  call_type: CallIdType;
}

/**
 * callId 类型
 */
export type CallIdType = "shared" | "dedicated";

/**
 * 完整六层标识符
 * 与后端 SixLayerIdentifier 完全匹配
 */
export interface SixLayerIdentifier {
  /** 频道标识符 */
  channel: ChannelIdentifier;
  /** 调用方标识符 */
  caller: CallerIdentifier;
  /** 被叫方标识符 */
  called: CalledIdentifier;
}

/**
 * 会话标识符
 * 与后端 SessionIdentifier 完全匹配
 */
export interface SessionIdentifier {
  /** 会话 ID（唯一标识一次对话） */
  session_id: string;
  /** 六层标识符 */
  identifiers: SixLayerIdentifier;
  /** 创建时间 */
  created_at: string;
  /** 最后消息时间 */
  last_message_at: string;
}

/**
 * 消息标识符
 * 与后端 MessageIdentifier 完全匹配
 */
export interface MessageIdentifier {
  /** 消息 ID（唯一标识） */
  message_id: string;
  /** 会话 ID */
  session_id: string;
  /** 六层标识符 */
  identifiers: SixLayerIdentifier;
  /** 消息序号（会话内递增） */
  sequence_number: number;
}

/**
 * 标识符映射关系
 * 用于 callId 路由和携号转网场景
 */
export interface IdentifierMapping {
  /** 映射 ID */
  mapping_id: string;
  /** callId */
  called_id: string;
  /** 目标 Agent ID */
  target_agent_id: string;
  /** 租户 ID */
  tenant_id: string;
  /** 路由策略 */
  routing_strategy: RoutingStrategy;
  /** 路由配置 */
  routing_config: Record<string, any>;
  /** 状态 */
  status: IdentifierMappingStatus;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
}

/**
 * 标识符映射状态
 */
export type IdentifierMappingStatus = "active" | "suspended" | "unbound" | "archived";

/**
 * 路由策略类型
 */
export type RoutingStrategy =
  | "direct"         // 直接路由到绑定 Agent
  | "round_robin"    // 轮询
  | "weighted"       // 加权轮询
  | "skill_based"    // 基于技能路由
  | "least_busy"     // 最闲优先
  | "custom";        // 自定义策略

/**
 * 路由配置
 */
export interface RoutingConfig {
  /** 路由策略 */
  strategy: RoutingStrategy;
  /** 策略参数 */
  strategy_params: Record<string, any>;
  /** 故障转移配置 */
  failover?: FailoverConfig;
  /** 负载均衡配置 */
  load_balancing?: LoadBalancingConfig;
}

/**
 * 故障转移配置
 */
export interface FailoverConfig {
  /** 是否启用故障转移 */
  enabled: boolean;
  /** 故障转移目标 Agent ID 列表 */
  fallback_agent_ids: string[];
  /** 故障检测超时（毫秒） */
  timeout_ms: number;
  /** 最大重试次数 */
  max_retries: number;
}

/**
 * 负载均衡配置
 */
export interface LoadBalancingConfig {
  /** 权重（用于 weighted 策略） */
  weights?: Record<string, number>;
  /** 健康检查间隔（秒） */
  health_check_interval_sec: number;
  /** 最小活跃连接数 */
  min_active_connections: number;
}

/**
 * 标识符解析结果
 * 用于会话穿透场景
 */
export interface IdentifierResolution {
  /** 六层标识符 */
  identifiers: SixLayerIdentifier;
  /** 会话 ID */
  session_id: string;
  /** 目标 Agent ID */
  target_agent_id: string;
  /** 租户 ID */
  tenant_id: string;
  /** 用户画像（可选） */
  user_profile?: UserProfile;
  /** 群聊上下文（可选） */
  group_context?: GroupContext;
  /** 会话历史（可选） */
  session_history?: SessionHistory;
}

/**
 * 用户画像
 * 与后端 UserProfile 完全匹配
 */
export interface UserProfile {
  /** 用户 ID */
  user_id: string;
  /** 用户名 */
  username?: string;
  /** 昵称 */
  nickname?: string;
  /** 头像 URL */
  avatar_url?: string;
  /** 部门（可选） */
  department?: string;
  /** 职位（可选） */
  position?: string;
  /** 邮箱（可选） */
  email?: string;
  /** 手机（可选） */
  phone?: string;
  /** 标签（可选） */
  tags?: string[];
  /** 自定义属性（可选） */
  custom_properties?: Record<string, any>;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
}

/**
 * 群聊上下文
 * 与后端 GroupContext 完全匹配
 */
export interface GroupContext {
  /** 群 ID */
  group_id: string;
  /** 群名称 */
  group_name: string;
  /** 群头像 URL（可选） */
  group_avatar_url?: string;
  /** 群成员数量 */
  member_count: number;
  /** 群主 ID（可选） */
  owner_id?: string;
  /** 群管理员 ID 列表（可选） */
  admin_ids?: string[];
  /** 群描述（可选） */
  description?: string;
  /** 群标签（可选） */
  tags?: string[];
  /** 群公告（可选） */
  announcement?: string;
  /** 创建时间 */
  created_at: string;
}

/**
 * 会话历史
 */
export interface SessionHistory {
  /** 会话 ID */
  session_id: string;
  /** 消息数量 */
  message_count: number;
  /** 最近消息（最多 10 条） */
  recent_messages: Array<{
    message_id: string;
    content: string;
    content_type: string;
    direction: string;
    timestamp: string;
  }>;
  /** 会话摘要（可选） */
  summary?: string;
  /** 会话标签（可选） */
  tags?: string[];
}

/**
 * 标识符工具函数
 */
export namespace IdentifierUtils {
  /**
   * 构建完整六层标识符
   */
  export function buildSixLayerIdentifier(
    channelId: string,
    channelType: string,
    callerLogicalId: string,
    calledId: string,
    callType: CallIdType = "dedicated",
    callerPhysicalId?: string,
    channelInstanceId?: string
  ): SixLayerIdentifier {
    return {
      channel: {
        channel_id: channelId,
        channel_type: channelType,
        channel_instance_id: channelInstanceId,
      },
      caller: {
        logical_id: callerLogicalId,
        physical_id: callerPhysicalId,
      },
      called: {
        called_id: calledId,
        call_type: callType,
      },
    };
  }

  /**
   * 判断是否为群聊场景
   */
  export function isGroupChat(identifiers: SixLayerIdentifier): boolean {
    return !!identifiers.caller.physical_id;
  }

  /**
   * 获取实际发送者 ID
   */
  export function getActualSenderId(identifiers: SixLayerIdentifier): string {
    return identifiers.caller.physical_id || identifiers.caller.logical_id;
  }

  /**
   * 生成会话 ID
   */
  export function generateSessionId(
    channelId: string,
    callerLogicalId: string,
    calledId: string
  ): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 8);
    return `${channelId}_${callerLogicalId}_${calledId}_${timestamp}_${random}`;
  }
}
