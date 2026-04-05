/**
 * 会话上下文展示组件
 * v4.0 新增 - 展示 SessionContext v2 完整信息
 */
import React, { useState } from "react";
import { Card, Tag, Space, Typography, Divider, Button, Modal, Drawer } from "antd";
import {
  InfoCircleOutlined,
  UserOutlined,
  GroupOutlined,
  WifiOutlined,
  PhoneOutlined,
} from "@ant-design/icons";
import type { SessionContextV2 } from "@/api/types";
import { adaptSessionContext, getSessionTitle, getSessionSubtitle } from "../adapter";
import SessionInfoPanel from "./SessionInfoPanel";

const { Text, Paragraph } = Typography;

interface SessionContextDisplayProps {
  context: SessionContextV2;
  compact?: boolean;
  showDetails?: boolean;
}

/**
 * 会话上下文展示
 */
export const SessionContextDisplay: React.FC<SessionContextDisplayProps> = ({
  context,
  compact = false,
  showDetails = true,
}) => {
  const [infoDrawerOpen, setInfoDrawerOpen] = useState(false);
  const adapted = adaptSessionContext(context);
  const isGroup = !!context.caller_physical_id;

  if (compact) {
    // 紧凑模式：仅显示基本信息
    return (
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        {isGroup ? (
          <GroupOutlined style={{ color: "#faad14" }} />
        ) : (
          <UserOutlined style={{ color: "#52c41a" }} />
        )}
        <Text strong style={{ fontSize: "14px" }}>
          {getSessionTitle(context)}
        </Text>
        <Tag color={isGroup ? "orange" : "green"}>
          {isGroup ? "群聊" : "私聊"}
        </Tag>
        {showDetails && (
          <Button
            type="text"
            size="small"
            icon={<InfoCircleOutlined />}
            onClick={() => setInfoDrawerOpen(true)}
          />
        )}
      </div>
    );
  }

  // 详细模式
  return (
    <>
      <Card
        size="small"
        style={{ marginBottom: "16px" }}
        title={
          <Space>
            {isGroup ? (
              <GroupOutlined style={{ color: "#faad14" }} />
            ) : (
              <UserOutlined style={{ color: "#52c41a" }} />
            )}
            <span>{getSessionTitle(context)}</span>
            {isGroup && (
              <Tag color="orange">群聊</Tag>
            )}
          </Space>
        }
        extra={
          showDetails && (
            <Button
              type="text"
              size="small"
              icon={<InfoCircleOutlined />}
              onClick={() => setInfoDrawerOpen(true)}
            >
              详情
            </Button>
          )
        }
      >
        {/* 六层标识体系 */}
        <div style={{ marginBottom: "12px" }}>
          <Text type="secondary" style={{ fontSize: "12px", display: "block", marginBottom: "6px" }}>
            <WifiOutlined /> 六层标识体系
          </Text>
          <Space wrap size={8}>
            <Tag color="blue">{context.channel_id}</Tag>
            <Tag color="cyan">{context.channel_type}</Tag>
            <Tag color="purple">{context.caller_logical_id}</Tag>
            {context.caller_physical_id && (
              <Tag color="orange">{context.caller_physical_id}</Tag>
            )}
            <Tag color="green">{context.called_id}</Tag>
          </Space>
        </div>

        {/* 会话统计 */}
        <div style={{ display: "flex", gap: "16px", fontSize: "13px" }}>
          <div>
            <Text type="secondary">消息数：</Text>
            <Text strong>{context.message_count}</Text>
          </div>
          <div>
            <Text type="secondary">创建时间：</Text>
            <Text>{new Date(context.created_at).toLocaleString("zh-CN")}</Text>
          </div>
          <div>
            <Text type="secondary">最后消息：</Text>
            <Text>{new Date(context.last_message_at).toLocaleString("zh-CN")}</Text>
          </div>
        </div>

        {/* 用户画像摘要（私聊场景） */}
        {adapted.userProfile && !adapted.groupContext && (
          <>
            <Divider style={{ margin: "12px 0" }} />
            <div>
              <Text type="secondary" style={{ fontSize: "12px", display: "block", marginBottom: "6px" }}>
                <UserOutlined /> 用户信息
              </Text>
              <Space wrap>
                {adapted.userProfile.department && (
                  <Tag>{adapted.userProfile.department}</Tag>
                )}
                {adapted.userProfile.position && (
                  <Tag>{adapted.userProfile.position}</Tag>
                )}
                {adapted.userProfile.tags?.slice(0, 3).map((tag: string, i: number) => (
                  <Tag key={i}>{tag}</Tag>
                ))}
              </Space>
            </div>
          </>
        )}

        {/* 群聊上下文摘要（群聊场景） */}
        {adapted.groupContext && (
          <>
            <Divider style={{ margin: "12px 0" }} />
            <div>
              <Text type="secondary" style={{ fontSize: "12px", display: "block", marginBottom: "6px" }}>
                <GroupOutlined /> 群聊信息
              </Text>
              <Paragraph ellipsis={{ rows: 2 }} style={{ marginBottom: "8px", fontSize: "13px" }}>
                {adapted.groupContext.description || "暂无群描述"}
              </Paragraph>
              <Space>
                <Text type="secondary">成员数：</Text>
                <Text strong>{adapted.groupContext.memberCount}</Text>
              </Space>
            </div>
          </>
        )}
      </Card>

      {/* 详情抽屉 */}
      <Drawer
        title="会话详情"
        placement="right"
        width={450}
        open={infoDrawerOpen}
        onClose={() => setInfoDrawerOpen(false)}
      >
        <SessionInfoPanel context={context} onClose={() => setInfoDrawerOpen(false)} />
      </Drawer>
    </>
  );
};

/**
 * 六层标识体系标签组
 */
export const SixLayerIdentifierTags: React.FC<{
  channelId: string;
  channelType: string;
  callerLogicalId: string;
  callerPhysicalId?: string;
  calledId: string;
  sessionId: string;
  showSessionId?: boolean;
}> = ({
  channelId,
  channelType,
  callerLogicalId,
  callerPhysicalId,
  calledId,
  sessionId,
  showSessionId = false,
}) => {
  return (
    <Space wrap size={4}>
      <Tooltip title="频道 ID">
        <Tag color="blue" style={{ fontSize: "11px" }}>{channelId}</Tag>
      </Tooltip>
      <Tooltip title="频道类型">
        <Tag color="cyan" style={{ fontSize: "11px" }}>{channelType}</Tag>
      </Tooltip>
      <Tooltip title="调用方逻辑 ID">
        <Tag color="purple" style={{ fontSize: "11px" }}>{callerLogicalId}</Tag>
      </Tooltip>
      {callerPhysicalId && (
        <Tooltip title="调用方物理 ID（实际发送者）">
          <Tag color="orange" style={{ fontSize: "11px" }}>{callerPhysicalId}</Tag>
        </Tooltip>
      )}
      <Tooltip title="被叫 ID">
        <Tag color="green" style={{ fontSize: "11px" }}>{calledId}</Tag>
      </Tooltip>
      {showSessionId && (
        <Tooltip title="会话 ID">
          <Tag style={{ fontSize: "11px", fontFamily: "monospace" }}>
            {sessionId.substring(0, 8)}...
          </Tag>
        </Tooltip>
      )}
    </Space>
  );
};

/**
 * 导入 Tooltip 组件
 */
import { Tooltip } from "antd";

export default SessionContextDisplay;
