/**
 * 聊天相关类型定义
 * v4.0 新增 - BusMessage v3、SessionContext v2 与后端 Python Schema 完全匹配
 */

/** 消息内容类型 */
export type ContentType = "text" | "image" | "file" | "voice" | "video";

/** 消息方向 */
export type MessageDirection = "inbound" | "outbound";

/**
 * BusMessage v3 - 六层标识体系完整支持
 * 与后端 BusMessageV3 完全匹配
 */
export interface BusMessageV3 {
  /** 消息 ID（唯一标识） */
  message_id: string;
  /** 频道 ID（如 dingtalk） */
  channel_id: string;
  /** 频道类型（如 dingtalk_robot） */
  channel_type: string;
  /** 调用方逻辑 ID（群 ID 或用户 ID） */
  caller_logical_id: string;
  /** 调用方物理 ID（实际发送者 ID，群聊场景使用） */
  caller_physical_id: string;
  /** 被叫 ID（callId，如 400-001） */
  called_id: string;
  /** 会话 ID */
  session_id: string;
  /** 内容类型 */
  content_type: ContentType;
  /** 消息内容 */
  content: string;
  /** 时间戳 */
  timestamp: string;
  /** 消息方向 */
  direction: MessageDirection;
  /** 元数据（可选，支持 null） */
  metadata?: null | Record<string, any>;
  // ===== 兼容字段（用于页面代码）=====
  /** 消息类型（兼容旧代码） */
  type?: string;
  /** 消息角色（兼容旧代码） */
  role?: "user" | "assistant" | "system";
  /** 消息 ID 别名（兼容旧代码） */
  id?: string;
}

/**
 * SessionContext v2 - 会话上下文完整信息
 * 与后端 SessionContextV2 完全匹配
 */
export interface SessionContextV2 {
  /** 会话 ID */
  session_id: string;
  /** 频道 ID */
  channel_id: string;
  /** 频道类型 */
  channel_type: string;
  /** 调用方逻辑 ID */
  caller_logical_id: string;
  /** 调用方物理 ID（可选，群聊场景使用） */
  caller_physical_id?: string;
  /** 被叫 ID（callId） */
  called_id: string;
  /** 用户画像（可选） */
  user_profile?: UserProfile;
  /** 群聊上下文（可选） */
  group_context?: GroupContext;
  /** 创建时间 */
  created_at: string;
  /** 最后消息时间 */
  last_message_at: string;
  /** 消息数量 */
  message_count: number;
}

/**
 * 用户画像 - 与后端 UserProfile 匹配
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
}

/**
 * 群聊上下文 - 与后端 GroupContext 匹配
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
  /** 管理员 IDs（可选） */
  admin_ids?: string[];
  /** 群公告（可选） */
  announcement?: string;
  /** 群描述（可选） */
  description?: string;
  /** 群标签（可选） */
  tags?: string[];
}

/**
 * 发送消息请求 - 与后端 SendMessageRequest 完全匹配
 */
export interface SendMessageRequest {
  /** callId */
  call_id: string;
  /** 消息内容 */
  content: string;
  /** 内容类型（默认 text） */
  content_type?: ContentType;
  /** 元数据（可选） */
  metadata?: Record<string, any>;
}

/**
 * 发送消息响应 - 与后端 SendMessageResponse 完全匹配
 */
export interface SendMessageResponse {
  /** 消息 ID */
  message_id: string;
  /** callId */
  call_id: string;
  /** 发送状态 */
  status: "sent" | "queued" | "failed";
  /** 时间戳 */
  timestamp: string;
}

/**
 * 会话信息 - 与后端 SessionResponse 完全匹配
 */
export interface SessionInfo {
  /** 会话 ID */
  session_id: string;
  /** callId */
  call_id: string;
  /** 频道 ID */
  channel_id: string;
  /** 调用方 ID */
  caller_id: string;
  /** 被叫 ID */
  called_id: string;
  /** 状态 */
  status: "active" | "paused" | "closed";
  /** 创建时间 */
  created_at: string;
  /** 最后消息时间 */
  last_message_at: string;
  /** 消息数量 */
  message_count: number;
  /** 会话上下文（可选） */
  context?: SessionContextV2;
}

/**
 * 会话列表响应 - 与后端 SessionListResponse 完全匹配
 */
export interface SessionListResponse {
  /** 会话列表 */
  sessions: SessionInfo[];
  /** 总数 */
  total: number;
  /** 当前页码 */
  page: number;
  /** 每页数量 */
  page_size: number;
}

/**
 * ChatSpec - 聊天会话规格（CoPaw 原有类型）
 * 用于聊天列表展示
 */
export interface ChatSpec {
  /** 会话 ID */
  id: string;
  /** 会话名称 */
  name?: string;
  /** 最后一条消息预览 */
  last_message?: string;
  /** 最后消息时间 */
  last_message_at?: string;
  /** 未读消息数 */
  unread_count?: number;
  /** 参与方 ID */
  participant_id?: string;
  /** 频道类型 */
  channel_type?: string;
  /** 状态（支持新旧两种类型） */
  status?: "active" | "paused" | "closed" | "idle" | "running";
  /** 元数据 */
  metadata?: Record<string, any>;
  // ===== 兼容字段（用于 sessionApi 和 ChatSessionDrawer）=====
  /** 会话 ID（别名） */
  session_id?: string;
  /** 用户 ID */
  user_id?: string;
  /** 频道 ID */
  channel?: string;
  /** 元数据（别名） */
  meta?: Record<string, any>;
  /** 创建时间 */
  created_at?: string | null;
}

/**
 * ChatHistory - 聊天历史（CoPaw 原有类型）
 * 用于聊天历史详情
 */
export interface ChatHistory {
  /** 会话 ID */
  id: string;
  /** 消息列表 */
  messages: BusMessageV3[];
  /** 会话信息 */
  session?: SessionInfo;
  /** 上下文信息 */
  context?: SessionContextV2;
  /** 总消息数 */
  total?: number;
  // ===== 兼容字段（用于 sessionApi）=====
  /** 会话 ID（别名） */
  session_id?: string;
  /** 用户 ID */
  user_id?: string;
  /** 状态 */
  status?: "active" | "paused" | "closed" | "idle" | "running";
}

/**
 * ChatDeleteResponse - 删除聊天响应（CoPaw 原有类型）
 */
export interface ChatDeleteResponse {
  /** 成功标志 */
  success: boolean;
  /** 消息 */
  message?: string;
  /** 删除的会话 ID */
  deleted_id?: string;
}

/**
 * Session - 会话（CoPaw 原有类型，兼容 SessionInfo）
 */
export type Session = SessionInfo;

/**
 * ChatStatus - 聊天状态（CoPaw 原有类型）
 */
export type ChatStatus = "active" | "paused" | "closed";

/**
 * Message - 消息（CoPaw 原有类型，兼容 BusMessageV3）
 */
export type Message = BusMessageV3;
