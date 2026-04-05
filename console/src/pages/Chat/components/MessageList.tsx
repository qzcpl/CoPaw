/**
 * 消息列表组件
 * v4.0 更新 - 支持 BusMessage v3 和六层标识体系展示
 */
import React from "react";
import { Avatar, List, Tag, Space, Typography, Tooltip } from "antd";
import { UserOutlined, RobotOutlined, GroupOutlined } from "@ant-design/icons";
import type { BusMessageV3, UserProfile } from "@/api/types";
import { adaptBusMessageV3, MessageFormatter, getMessageSenderInfo } from "../adapter";

const { Text } = Typography;

interface MessageListProps {
  messages: BusMessageV3[];
  currentUserProfile?: UserProfile;
  onMessageClick?: (message: BusMessageV3) => void;
  showSenderName?: boolean;
}

/**
 * 消息列表
 */
export const MessageList: React.FC<MessageListProps> = ({
  messages,
  currentUserProfile,
  onMessageClick,
  showSenderName = false,
}) => {
  // 按时间排序消息
  const sortedMessages = [...messages].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  return (
    <List
      dataSource={sortedMessages}
      renderItem={(msg) => {
        const adapted = adaptBusMessageV3(msg);
        const senderInfo = getMessageSenderInfo(msg, currentUserProfile);
        const isOutbound = msg.direction === "outbound";
        const shouldShowSender = showSenderName || MessageFormatter.shouldShowSenderName(msg);

        return (
          <List.Item
            className={`message-item ${isOutbound ? "message-outbound" : "message-inbound"}`}
            onClick={() => onMessageClick?.(msg)}
            style={{
              padding: "12px 16px",
              cursor: onMessageClick ? "pointer" : "default",
              backgroundColor: isOutbound ? "#f0f7ff" : "transparent",
              borderBottom: "1px solid #f0f0f0",
            }}
          >
            <div style={{ display: "flex", gap: "12px", width: "100%" }}>
              {/* 头像 */}
              <Avatar
                icon={isOutbound ? <RobotOutlined /> : <UserOutlined />}
                size={40}
                style={{
                  backgroundColor: isOutbound ? "#1890ff" : "#52c41a",
                  flexShrink: 0,
                }}
              />

              {/* 消息内容 */}
              <div style={{ flex: 1, minWidth: 0 }}>
                {/* 发送者信息（群聊场景或显式要求） */}
                {shouldShowSender && (
                  <div style={{ marginBottom: "4px" }}>
                    <Space size={4}>
                      <Text strong style={{ fontSize: "14px" }}>
                        {senderInfo.senderName}
                      </Text>
                      {senderInfo.isGroup && (
                        <Tag icon={<GroupOutlined />} color="orange" style={{ fontSize: "12px" }}>
                          群聊
                        </Tag>
                      )}
                      <Text type="secondary" style={{ fontSize: "12px" }}>
                        {MessageFormatter.formatTime(msg.timestamp)}
                      </Text>
                    </Space>
                  </div>
                )}

                {/* 消息内容 */}
                <div style={{ fontSize: "14px", lineHeight: "1.6" }}>
                  {MessageFormatter.formatContent(msg.content, msg.content_type)}
                </div>

                {/* 消息元数据（调试用） */}
                <div style={{ marginTop: "4px", fontSize: "12px", color: "#8c8c8c" }}>
                  <Space size={8}>
                    <Tooltip title="消息 ID">
                      <Text code style={{ fontSize: "11px" }}>
                        {msg.message_id.substring(0, 8)}...
                      </Text>
                    </Tooltip>
                    <Tooltip title="频道 ID">
                      <Tag color="blue" style={{ fontSize: "11px", padding: "0 4px" }}>
                        {msg.channel_id}
                      </Tag>
                    </Tooltip>
                    <Tooltip title="callId">
                      <Tag color="cyan" style={{ fontSize: "11px", padding: "0 4px" }}>
                        {msg.called_id}
                      </Tag>
                    </Tooltip>
                    {!isOutbound && msg.caller_physical_id && (
                      <Tooltip title="实际发送者">
                        <Tag color="orange" style={{ fontSize: "11px", padding: "0 4px" }}>
                          {msg.caller_physical_id.substring(0, 8)}...
                        </Tag>
                      </Tooltip>
                    )}
                  </Space>
                </div>
              </div>
            </div>
          </List.Item>
        );
      }}
    />
  );
};

/**
 * 消息日期分隔符
 */
export const MessageDateDivider: React.FC<{ timestamp: string }> = ({ timestamp }) => {
  const date = new Date(timestamp);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  let labelText = "";
  if (date.toDateString() === today.toDateString()) {
    labelText = "今天";
  } else if (date.toDateString() === yesterday.toDateString()) {
    labelText = "昨天";
  } else {
    labelText = date.toLocaleDateString("zh-CN", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }

  return (
    <div style={{ textAlign: "center", margin: "16px 0" }}>
      <Tag color="default" style={{ fontSize: "12px" }}>
        {labelText}
      </Tag>
    </div>
  );
};

/**
 * 系统消息
 */
export const SystemMessage: React.FC<{
  content: string;
  timestamp?: string;
  type?: "info" | "warning" | "error" | "success";
}> = ({ content, timestamp, type = "info" }) => {
  const colors = {
    info: "#1890ff",
    warning: "#faad14",
    error: "#ff4d4f",
    success: "#52c41a",
  };

  return (
    <div style={{ textAlign: "center", margin: "12px 0" }}>
      <Tag color={colors[type]} style={{ fontSize: "13px" }}>
        {content}
      </Tag>
      {timestamp && (
        <div style={{ fontSize: "12px", color: "#8c8c8c", marginTop: "4px" }}>
          {MessageFormatter.formatTime(timestamp)}
        </div>
      )}
    </div>
  );
};

/**
 * 消息状态指示器
 */
export const MessageStatusIndicator: React.FC<{
  status: "sending" | "sent" | "delivered" | "read" | "failed";
}> = ({ status }) => {
  const indicators = {
    sending: { color: "#1890ff", text: "发送中..." },
    sent: { color: "#52c41a", text: "已发送" },
    delivered: { color: "#13c2c2", text: "已送达" },
    read: { color: "#722ed1", text: "已读" },
    failed: { color: "#ff4d4f", text: "发送失败" },
  };

  const { color, text } = indicators[status];

  return (
    <Space size={4}>
      <span
        style={{
          width: "8px",
          height: "8px",
          borderRadius: "50%",
          backgroundColor: color,
          display: "inline-block",
        }}
      />
      <span style={{ fontSize: "12px", color: "#8c8c8c" }}>{text}</span>
    </Space>
  );
};

export default MessageList;
