/**
 * 频道列表组件 v4.0
 * 支持新频道 API 和六层标识体系展示
 */
import React, { useState, useEffect } from "react";
import {
  Card,
  Table,
  Tag,
  Space,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  message,
  Tooltip,
  Badge,
  Progress,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PoweroffOutlined,
  SyncOutlined,
  WifiOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import type {
  ChannelConfig,
  ChannelInstance,
  ChannelStatsResponse,
  ChannelHealthStatus,
} from "@/api/types";
import { channelApi } from "@/api/modules/channel";

const { TextArea } = Input;

interface ChannelListProps {
  tenantId?: string;
  onChannelSelect?: (channel: ChannelConfig) => void;
}

/**
 * 频道列表
 */
export const ChannelList: React.FC<ChannelListProps> = ({
  tenantId,
  onChannelSelect,
}) => {
  const [channels, setChannels] = useState<ChannelConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedChannel, setSelectedChannel] = useState<ChannelConfig | null>(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [form] = Form.useForm();

  // 加载频道列表
  useEffect(() => {
    loadChannels();
  }, [tenantId]);

  const loadChannels = async () => {
    setLoading(true);
    try {
      const data = await channelApi.listChannels(tenantId);
      setChannels(data);
    } catch (error) {
      console.error("加载频道失败:", error);
      message.error("加载频道失败");
    } finally {
      setLoading(false);
    }
  };

  // 处理删除
  const handleDelete = (channel: ChannelConfig) => {
    Modal.confirm({
      title: "确认删除",
      content: `确定要删除频道 "${channel.channel_name}" 吗？`,
      okText: "确认",
      cancelText: "取消",
      okType: "danger",
      onOk: async () => {
        try {
          await channelApi.deleteChannel(channel.channel_id, tenantId);
          message.success("删除成功");
          loadChannels();
        } catch (error) {
          console.error("删除失败:", error);
          message.error("删除失败");
        }
      },
    });
  };

  // 查看详情
  const handleViewDetail = async (channel: ChannelConfig) => {
    setSelectedChannel(channel);
    setDetailModalOpen(true);
  };

  // 创建频道
  const handleCreate = async (values: any) => {
    try {
      await channelApi.createChannel({
        channel_id: values.channel_id,
        channel_name: values.channel_name,
        platform: values.platform,
        config: values.config || {},
        description: values.description,
      });
      message.success("创建成功");
      setCreateModalOpen(false);
      loadChannels();
    } catch (error) {
      console.error("创建失败:", error);
      message.error("创建失败");
    }
  };

  // 平台选项
  const platformOptions = [
    { value: "dingtalk", label: "钉钉" },
    { value: "feishu", label: "飞书" },
    { value: "wechat", label: "微信" },
    { value: "web", label: "Web" },
    { value: "discord", label: "Discord" },
    { value: "telegram", label: "Telegram" },
  ];

  // 状态标签
  const getStatusTag = (status: string) => {
    const config: Record<string, any> = {
      active: { color: "green", icon: <CheckCircleOutlined /> },
      inactive: { color: "default", icon: <CloseCircleOutlined /> },
      error: { color: "red", icon: <ExclamationCircleOutlined /> },
      maintenance: { color: "orange", icon: <SyncOutlined spin /> },
    };
    const { color, icon } = config[status] || config.inactive;
    return <Tag icon={icon} color={color}>{status}</Tag>;
  };

  // 表格列定义
  const columns = [
    {
      title: "频道 ID",
      dataIndex: "channel_id",
      key: "channel_id",
      render: (text: string) => <strong>{text}</strong>,
    },
    {
      title: "频道名称",
      dataIndex: "channel_name",
      key: "channel_name",
    },
    {
      title: "平台",
      dataIndex: "platform",
      key: "platform",
      render: (platform: string) => (
        <Tag color="blue">{platformOptions.find((p) => p.value === platform)?.label || platform}</Tag>
      ),
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      render: getStatusTag,
    },
    {
      title: "租户 ID",
      dataIndex: "tenant_id",
      key: "tenant_id",
      ellipsis: true,
    },
    {
      title: "创建时间",
      dataIndex: "created_at",
      key: "created_at",
      render: (text: string) => new Date(text).toLocaleString("zh-CN"),
    },
    {
      title: "操作",
      key: "action",
      render: (_: any, record: ChannelConfig) => (
        <Space size={4}>
          <Button
            type="link"
            size="small"
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          <Button
            type="link"
            size="small"
            danger
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <>
      <Card
        title="频道管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalOpen(true)}>
            新建频道
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={channels}
          loading={loading}
          rowKey="channel_id"
          onRow={(record) => ({
            onClick: () => onChannelSelect?.(record),
            style: { cursor: "pointer" },
          })}
        />
      </Card>

      {/* 创建频道对话框 */}
      <Modal
        title="创建频道"
        open={createModalOpen}
        onCancel={() => setCreateModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            name="channel_id"
            label="频道 ID"
            rules={[{ required: true, message: "请输入频道 ID" }]}
          >
            <Input placeholder="例如：dingtalk" />
          </Form.Item>
          <Form.Item
            name="channel_name"
            label="频道名称"
            rules={[{ required: true, message: "请输入频道名称" }]}
          >
            <Input placeholder="例如：钉钉机器人" />
          </Form.Item>
          <Form.Item
            name="platform"
            label="平台类型"
            rules={[{ required: true, message: "请选择平台类型" }]}
          >
            <Select options={platformOptions} />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="频道描述（可选）" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                创建
              </Button>
              <Button onClick={() => setCreateModalOpen(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 详情对话框 */}
      {selectedChannel && (
        <ChannelDetailModal
          channel={selectedChannel}
          open={detailModalOpen}
          onClose={() => setDetailModalOpen(false)}
          tenantId={tenantId}
        />
      )}
    </>
  );
};

/**
 * 频道详情对话框
 */
interface ChannelDetailModalProps {
  channel: ChannelConfig;
  open: boolean;
  onClose: () => void;
  tenantId?: string;
}

const ChannelDetailModal: React.FC<ChannelDetailModalProps> = ({
  channel,
  open,
  onClose,
  tenantId,
}) => {
  const [instances, setInstances] = useState<ChannelInstance[]>([]);
  const [stats, setStats] = useState<ChannelStatsResponse | null>(null);
  const [health, setHealth] = useState<ChannelHealthStatus | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      loadDetails();
    }
  }, [open, channel]);

  const loadDetails = async () => {
    setLoading(true);
    try {
      const [instancesData, statsData, healthData] = await Promise.all([
        channelApi.listChannelInstances(channel.channel_id, tenantId),
        channelApi.getChannelStats(channel.channel_id, tenantId),
        channelApi.getChannelHealth(channel.channel_id),
      ]);
      setInstances(instancesData);
      setStats(statsData);
      setHealth(healthData);
    } catch (error) {
      console.error("加载详情失败:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={
        <Space>
          <WifiOutlined />
          <span>{channel.channel_name}</span>
          <Tag>{channel.channel_id}</Tag>
        </Space>
      }
      open={open}
      onCancel={onClose}
      footer={null}
      width={800}
    >
      {loading ? (
        <div style={{ textAlign: "center", padding: "40px" }}>加载中...</div>
      ) : (
        <div>
          {/* 基本信息 */}
          <Card title="基本信息" size="small" style={{ marginBottom: "16px" }}>
            <Space direction="vertical" style={{ width: "100%" }}>
              <Space>
                <strong>频道 ID:</strong> {channel.channel_id}
              </Space>
              <Space>
                <strong>平台:</strong> {channel.platform}
              </Space>
              <Space>
                <strong>状态:</strong>
                <Tag color={channel.status === "active" ? "green" : "default"}>
                  {channel.status}
                </Tag>
              </Space>
              <Space>
                <strong>描述:</strong> {channel.description || "无"}
              </Space>
              <Space>
                <strong>创建时间:</strong> {new Date(channel.created_at).toLocaleString("zh-CN")}
              </Space>
            </Space>
          </Card>

          {/* 统计信息 */}
          {stats && (
            <Card title="统计信息" size="small" style={{ marginBottom: "16px" }}>
              <Space direction="vertical" style={{ width: "100%" }}>
                <Space>
                  <strong>实例数量:</strong> {stats.instance_count}
                </Space>
                <Space>
                  <strong>24h 消息数:</strong> {stats.message_count_24h}
                </Space>
                <Space>
                  <strong>活跃会话:</strong> {stats.active_sessions}
                </Space>
                <Space>
                  <strong>平均响应时间:</strong> {stats.avg_response_time_ms}ms
                </Space>
              </Space>
            </Card>
          )}

          {/* 健康状态 */}
          {health && (
            <Card title="健康状态" size="small" style={{ marginBottom: "16px" }}>
              <Space direction="vertical" style={{ width: "100%" }}>
                <Space>
                  <strong>状态:</strong>
                  <Badge
                    status={
                      health.status === "healthy"
                        ? "success"
                        : health.status === "degraded"
                        ? "warning"
                        : "error"
                    }
                    text={health.status}
                  />
                </Space>
                <Space>
                  <strong>健康分数:</strong>
                  <Progress
                    percent={health.health_score}
                    strokeColor={
                      health.health_score >= 80
                        ? "#52c41a"
                        : health.health_score >= 60
                        ? "#faad14"
                        : "#ff4d4f"
                    }
                    size="small"
                    style={{ width: "200px" }}
                  />
                </Space>
                {health.issues.length > 0 && (
                  <div>
                    <strong>问题:</strong>
                    <ul>
                      {health.issues.map((issue, i) => (
                        <li key={i}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {health.recommendations.length > 0 && (
                  <div>
                    <strong>建议:</strong>
                    <ul>
                      {health.recommendations.map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </Space>
            </Card>
          )}

          {/* 频道实例 */}
          <Card title="频道实例" size="small">
            {instances.length === 0 ? (
              <div style={{ textAlign: "center", color: "#8c8c8c" }}>暂无实例</div>
            ) : (
              <Table
                dataSource={instances}
                rowKey="instance_id"
                size="small"
                columns={[
                  {
                    title: "实例 ID",
                    dataIndex: "instance_id",
                    key: "instance_id",
                  },
                  {
                    title: "Bot ID",
                    dataIndex: "bot_id",
                    key: "bot_id",
                  },
                  {
                    title: "状态",
                    dataIndex: "status",
                    key: "status",
                    render: (status: string) => (
                      <Tag color={status === "active" ? "green" : "default"}>
                        {status}
                      </Tag>
                    ),
                  },
                  {
                    title: "消息数",
                    dataIndex: "message_count",
                    key: "message_count",
                  },
                  {
                    title: "错误数",
                    dataIndex: "error_count",
                    key: "error_count",
                  },
                ]}
              />
            )}
          </Card>
        </div>
      )}
    </Modal>
  );
};

export default ChannelList;
