/**
 * 会话信息面板组件
 * v4.0 新增 - 展示六层标识体系和会话上下文
 */
import React from "react";
import { Descriptions, Tag, Avatar, Divider, Space, Tooltip, Button } from "antd";
import {
  UserOutlined,
  GroupOutlined,
  PhoneOutlined,
  WifiOutlined,
  RobotOutlined,
  ClockCircleOutlined,
  MessageOutlined,
} from "@ant-design/icons";
import type { SessionContextV2 } from "@/api/types";
import {
  adaptSessionContext,
  adaptUserProfile,
  adaptGroupContext,
  getSessionTitle,
  getSessionSubtitle,
} from "../adapter";

interface SessionInfoPanelProps {
  context: SessionContextV2;
  onClose?: () => void;
}

/**
 * 会话信息面板
 */
export const SessionInfoPanel: React.FC<SessionInfoPanelProps> = ({
  context,
  onClose,
}) => {
  const adapted = adaptSessionContext(context);
  const userProfile = context.user_profile ? adaptUserProfile(context.user_profile) : null;
  const groupContext = context.group_context ? adaptGroupContext(context.group_context) : null;

  return (
    <div style={{ padding: "16px" }}>
      {/* 会话标题 */}
      <div style={{ marginBottom: "16px" }}>
        <h3 style={{ margin: 0, fontSize: "18px" }}>
          {groupContext ? groupContext.displayName : userProfile?.displayName || "未知用户"}
        </h3>
        <div style={{ color: "#8c8c8c", fontSize: "14px", marginTop: "4px" }}>
          {getSessionSubtitle(context)}
        </div>
      </div>

      <Divider style={{ margin: "12px 0" }} />

      {/* 六层标识体系 */}
      <div style={{ marginBottom: "16px" }}>
        <h4 style={{ margin: "0 0 8px 0", fontSize: "14px" }}>
          <WifiOutlined /> 六层标识体系
        </h4>
        <Descriptions column={1} size="small" bordered>
          <Descriptions.Item label="频道 ID">
            <Tag color="blue">{context.channel_id}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="频道类型">
            <Tag color="cyan">{context.channel_type}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="调用方逻辑 ID">
            <Space>
              <UserOutlined />
              {context.caller_logical_id}
            </Space>
          </Descriptions.Item>
          {context.caller_physical_id && (
            <Descriptions.Item label="调用方物理 ID">
              <Space>
                <GroupOutlined />
                {context.caller_physical_id}
                <Tag color="orange">群聊</Tag>
              </Space>
            </Descriptions.Item>
          )}
          <Descriptions.Item label="被叫 ID">
            <Space>
              <PhoneOutlined />
              {context.called_id}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="会话 ID">
            <Tooltip title="唯一会话标识">
              <span style={{ fontSize: "12px", fontFamily: "monospace" }}>
                {context.session_id}
              </span>
            </Tooltip>
          </Descriptions.Item>
        </Descriptions>
      </div>

      <Divider style={{ margin: "12px 0" }} />

      {/* 会话统计 */}
      <div style={{ marginBottom: "16px" }}>
        <h4 style={{ margin: "0 0 8px 0", fontSize: "14px" }}>
          <ClockCircleOutlined /> 会话统计
        </h4>
        <Descriptions column={2} size="small" bordered>
          <Descriptions.Item label="消息数量">
            <Space>
              <MessageOutlined />
              {context.message_count}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="创建时间">
            {new Date(context.created_at).toLocaleString("zh-CN")}
          </Descriptions.Item>
          <Descriptions.Item label="最后消息">
            {new Date(context.last_message_at).toLocaleString("zh-CN")}
          </Descriptions.Item>
        </Descriptions>
      </div>

      {/* 用户画像（私聊场景） */}
      {userProfile && !groupContext && (
        <>
          <Divider style={{ margin: "12px 0" }} />
          <div style={{ marginBottom: "16px" }}>
            <h4 style={{ margin: "0 0 8px 0", fontSize: "14px" }}>
              <UserOutlined /> 用户信息
            </h4>
            <div style={{ display: "flex", alignItems: "center", marginBottom: "12px" }}>
              <Avatar
                src={userProfile.avatarUrl}
                size={64}
                icon={<UserOutlined />}
              />
              <div style={{ marginLeft: "12px" }}>
                <div style={{ fontSize: "16px", fontWeight: "bold" }}>
                  {userProfile.displayName}
                </div>
                <div style={{ color: "#8c8c8c", fontSize: "14px" }}>
                  {userProfile.userId}
                </div>
              </div>
            </div>
            <Descriptions column={2} size="small" bordered>
              {userProfile.department && (
                <Descriptions.Item label="部门">
                  {userProfile.department}
                </Descriptions.Item>
              )}
              {userProfile.position && (
                <Descriptions.Item label="职位">
                  {userProfile.position}
                </Descriptions.Item>
              )}
              {userProfile.email && (
                <Descriptions.Item label="邮箱">
                  {userProfile.email}
                </Descriptions.Item>
              )}
              {userProfile.phone && (
                <Descriptions.Item label="手机">
                  {userProfile.phone}
                </Descriptions.Item>
              )}
              {userProfile.tags && userProfile.tags.length > 0 && (
                <Descriptions.Item label="标签" span={2}>
                  <Space wrap>
                    {userProfile.tags.map((tag: string, index: number) => (
                      <Tag key={index} color="default">{tag}</Tag>
                    ))}
                  </Space>
                </Descriptions.Item>
              )}
            </Descriptions>
          </div>
        </>
      )}

      {/* 群聊上下文（群聊场景） */}
      {groupContext && (
        <>
          <Divider style={{ margin: "12px 0" }} />
          <div style={{ marginBottom: "16px" }}>
            <h4 style={{ margin: "0 0 8px 0", fontSize: "14px" }}>
              <GroupOutlined /> 群聊信息
            </h4>
            <div style={{ display: "flex", alignItems: "center", marginBottom: "12px" }}>
              <Avatar
                src={groupContext.groupAvatarUrl}
                size={64}
                icon={<GroupOutlined />}
              />
              <div style={{ marginLeft: "12px" }}>
                <div style={{ fontSize: "16px", fontWeight: "bold" }}>
                  {groupContext.displayName}
                </div>
                <div style={{ color: "#8c8c8c", fontSize: "14px" }}>
                  {groupContext.groupId} · {groupContext.memberCount} 人
                </div>
              </div>
            </div>
            {groupContext.description && (
              <div style={{ marginBottom: "8px", color: "#595959", fontSize: "14px" }}>
                {groupContext.description}
              </div>
            )}
            <Descriptions column={2} size="small" bordered>
              <Descriptions.Item label="群主">
                <Space>
                  <UserOutlined />
                  {groupContext.ownerId || "未知"}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="成员数">
                {groupContext.memberCount}
              </Descriptions.Item>
              {groupContext.tags && groupContext.tags.length > 0 && (
                <Descriptions.Item label="标签" span={2}>
                  <Space wrap>
                    {groupContext.tags.map((tag: string, index: number) => (
                      <Tag key={index} color="default">{tag}</Tag>
                    ))}
                  </Space>
                </Descriptions.Item>
              )}
            </Descriptions>
          </div>
        </>
      )}

      <Divider style={{ margin: "12px 0" }} />

      {/* 操作按钮 */}
      <Space style={{ width: "100%", justifyContent: "flex-end" }}>
        {onClose && (
          <Button onClick={onClose}>
            关闭
          </Button>
        )}
      </Space>
    </div>
  );
};

export default SessionInfoPanel;
