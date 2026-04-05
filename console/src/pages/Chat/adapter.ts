/**
 * 聊天页面适配层
 * v4.0 新增 - 适配 BusMessage v3 和 SessionContext v2
 */
import type { BusMessageV3, SessionContextV2, UserProfile, GroupContext } from "@/api/types";

/**
 * 将 BusMessage v3 转换为前端消息格式
 */
export function adaptBusMessageV3(msg: BusMessageV3): any {
  return {
    // 保留原始消息
    original: msg,
    
    // 前端展示字段
    id: msg.message_id,
    chatId: msg.session_id,
    role: msg.direction === "inbound" ? "user" : "assistant",
    content: msg.content,
    createdAt: msg.timestamp,
    
    // 元数据
    metadata: {
      messageId: msg.message_id,
      sessionId: msg.session_id,
      channelId: msg.channel_id,
      channelType: msg.channel_type,
      callerLogicalId: msg.caller_logical_id,
      callerPhysicalId: msg.caller_physical_id,
      calledId: msg.called_id,
      contentType: msg.content_type,
      direction: msg.direction,
      timestamp: msg.timestamp,
    },
  };
}

/**
 * 将前端消息格式转换为 BusMessage v3
 */
export function toBusMessageV3(
  content: string,
  sessionId: string,
  context: SessionContextV2,
  contentType: "text" | "image" | "file" | "voice" | "video" = "text"
): BusMessageV3 {
  return {
    message_id: generateMessageId(),
    channel_id: context.channel_id,
    channel_type: context.channel_type,
    caller_logical_id: context.caller_logical_id,
    caller_physical_id: context.caller_physical_id || context.caller_logical_id,
    called_id: context.called_id,
    session_id: sessionId,
    content_type: contentType,
    content: content,
    timestamp: new Date().toISOString(),
    direction: "outbound",
    metadata: {},
  };
}

/**
 * 适配会话上下文
 */
export function adaptSessionContext(ctx: SessionContextV2): any {
  return {
    // 保留原始上下文
    original: ctx,
    
    // 前端展示字段
    sessionId: ctx.session_id,
    channelId: ctx.channel_id,
    channelType: ctx.channel_type,
    callerId: ctx.caller_logical_id,
    callerPhysicalId: ctx.caller_physical_id,
    calledId: ctx.called_id,
    createdAt: ctx.created_at,
    lastMessageAt: ctx.last_message_at,
    messageCount: ctx.message_count,
    
    // 用户画像
    userProfile: ctx.user_profile ? adaptUserProfile(ctx.user_profile) : null,
    
    // 群聊上下文
    groupContext: ctx.group_context ? adaptGroupContext(ctx.group_context) : null,
  };
}

/**
 * 适配用户画像
 */
export function adaptUserProfile(profile: UserProfile): any {
  return {
    userId: profile.user_id,
    username: profile.username,
    nickname: profile.nickname,
    avatarUrl: profile.avatar_url,
    department: profile.department,
    position: profile.position,
    email: profile.email,
    phone: profile.phone,
    tags: profile.tags,
    customProperties: profile.custom_properties,
    
    // 显示名称（优先昵称，其次用户名）
    displayName: profile.nickname || profile.username || profile.user_id,
  };
}

/**
 * 适配群聊上下文
 */
export function adaptGroupContext(group: GroupContext): any {
  return {
    groupId: group.group_id,
    groupName: group.group_name,
    groupAvatarUrl: group.group_avatar_url,
    memberCount: group.member_count,
    ownerId: group.owner_id,
    adminIds: group.admin_ids,
    description: group.description,
    tags: group.tags,
    announcement: group.announcement,
    
    // 显示名称
    displayName: group.group_name || group.group_id,
  };
}

/**
 * 获取消息发送者信息
 */
export function getMessageSenderInfo(msg: BusMessageV3, userProfile?: UserProfile): {
  senderId: string;
  senderName: string;
  isGroup: boolean;
} {
  const isGroup = !!msg.caller_physical_id;
  const actualSenderId = msg.caller_physical_id || msg.caller_logical_id;
  
  let senderName = actualSenderId;
  if (userProfile) {
    senderName = userProfile.nickname || userProfile.username || userProfile.user_id;
  }
  
  return {
    senderId: actualSenderId,
    senderName,
    isGroup,
  };
}

/**
 * 获取会话标题
 */
export function getSessionTitle(context: SessionContextV2): string {
  // 群聊：显示群名称
  if (context.group_context) {
    return context.group_context.group_name || context.group_context.group_id;
  }
  
  // 私聊：显示用户昵称
  if (context.user_profile) {
    return context.user_profile.nickname || 
           context.user_profile.username || 
           context.user_profile.user_id;
  }
  
  // 默认：显示 callId
  return context.called_id;
}

/**
 * 获取会话副标题（显示频道信息）
 */
export function getSessionSubtitle(context: SessionContextV2): string {
  const parts: string[] = [];
  
  // 频道信息
  if (context.channel_id) {
    parts.push(context.channel_id);
  }
  
  // callId
  if (context.called_id) {
    parts.push(context.called_id);
  }
  
  return parts.join(" · ");
}

/**
 * 生成消息 ID
 */
function generateMessageId(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8);
  return `msg_${timestamp}_${random}`;
}

/**
 * 消息格式化工具
 */
export const MessageFormatter = {
  /**
   * 格式化消息时间
   */
  formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
      return date.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
    } else if (days === 1) {
      return "昨天";
    } else if (days < 7) {
      return `${days}天前`;
    } else {
      return date.toLocaleDateString("zh-CN", { month: "short", day: "numeric" });
    }
  },
  
  /**
   * 格式化消息内容（处理特殊格式）
   */
  formatContent(content: string, contentType: string): string {
    if (contentType === "text") {
      return content;
    } else if (contentType === "image") {
      return `[图片] ${content}`;
    } else if (contentType === "file") {
      return `[文件] ${content}`;
    } else if (contentType === "voice") {
      return `[语音] ${content}`;
    } else if (contentType === "video") {
      return `[视频] ${content}`;
    }
    return content;
  },
  
  /**
   * 判断是否显示发送者名称（群聊场景）
   */
  shouldShowSenderName(msg: BusMessageV3): boolean {
    // 群聊场景显示发送者名称
    return !!msg.caller_physical_id;
  },
};

/**
 * 会话状态工具
 */
export const SessionStatusUtils = {
  /**
   * 获取会话状态标签
   */
  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      active: "进行中",
      paused: "已暂停",
      closed: "已关闭",
    };
    return labels[status] || status;
  },
  
  /**
   * 获取会话状态颜色
   */
  getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      active: "#52c41a",    // 绿色
      paused: "#faad14",    // 橙色
      closed: "#8c8c8c",    // 灰色
    };
    return colors[status] || "#8c8c8c";
  },
};
