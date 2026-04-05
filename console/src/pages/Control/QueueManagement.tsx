/**
 * 队列管理页面
 * v4.0 新增 - 支持消息队列管理、死信队列、队列监控
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
  message,
  Descriptions,
  Progress,
  Statistic,
  Row,
  Col,
  Alert,
  Badge,
} from "antd";
import {
  PlusOutlined,
  DeleteOutlined,
  ClearOutlined,
  DownloadOutlined,
  BarsOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
} from "@ant-design/icons";
import type {
  MessageQueue,
  QueueMessage,
  QueueStatsResponse,
  DeadLetterMessage,
} from "@/api/types";
import { queueApi } from "@/api/modules/queue";
import { useTenantStore } from "@/stores/tenantStore";

const { TextArea } = Input;

/**
 * 队列管理页面
 */
export const QueueManagement: React.FC = () => {
  const [queues, setQueues] = useState<MessageQueue[]>([]);
  const [stats, setStats] = useState<QueueStatsResponse | null>(null);
  const [dlqMessages, setDlqMessages] = useState<DeadLetterMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedQueue, setSelectedQueue] = useState<MessageQueue | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [dlqModalOpen, setDlqModalOpen] = useState(false);
  const [form] = Form.useForm();
  const { currentTenantId } = useTenantStore();

  // 加载队列数据
  useEffect(() => {
    loadQueueData();
  }, [currentTenantId]);

  const loadQueueData = async () => {
    setLoading(true);
    try {
      const [queuesData, dlqData] = await Promise.all([
        queueApi.listQueues(currentTenantId!),
        queueApi.listDeadLetterMessages(currentTenantId!, 50),
      ]);
      setQueues(queuesData);
      setDlqMessages(dlqData);
      // 获取第一个队列的统计信息
      if (queuesData.length > 0) {
        const statsData = await queueApi.getQueueStats(queuesData[0].queue_id);
        setStats(statsData);
      }
    } catch (error) {
      console.error("加载队列数据失败:", error);
      message.error("加载失败");
    } finally {
      setLoading(false);
    }
  };

  // 创建队列
  const handleCreate = async (values: any) => {
    try {
      await queueApi.createQueue({
        queue_name: values.queue_name,
        queue_type: values.queue_type || "standard",
        config: {
          max_size: values.max_size || 10000,
          message_ttl_sec: values.ttl_seconds || 3600,
          visibility_timeout_sec: 30,
          max_retries: 3,
          retry_interval_sec: 60,
          backend_config: {},
        },
      });
      message.success("创建成功");
      setCreateModalOpen(false);
      loadQueueData();
    } catch (error) {
      console.error("创建失败:", error);
      message.error("创建失败");
    }
  };

  // 删除队列
  const handleDelete = (queue: MessageQueue) => {
    Modal.confirm({
      title: "确认删除",
      content: `确定要删除队列 "${queue.queue_name}" 吗？这将删除所有消息！`,
      okText: "确认",
      cancelText: "取消",
      okType: "danger",
      onOk: async () => {
        try {
          await queueApi.deleteQueue(queue.queue_id);
          message.success("删除成功");
          loadQueueData();
        } catch (error) {
          console.error("删除失败:", error);
          message.error("删除失败");
        }
      },
    });
  };

  // 清空队列
  const handleClear = (queue: MessageQueue) => {
    Modal.confirm({
      title: "确认清空",
      content: `确定要清空队列 "${queue.queue_name}" 吗？`,
      okText: "确认",
      cancelText: "取消",
      okType: "danger",
      onOk: async () => {
        try {
          await queueApi.purgeQueue(queue.queue_id);
          message.success("清空成功");
          loadQueueData();
        } catch (error) {
          console.error("清空失败:", error);
          message.error("清空失败");
        }
      },
    });
  };

  // 查看死信队列
  const handleViewDLQ = async () => {
    try {
      const data = await queueApi.listDeadLetterMessages(currentTenantId!, 100);
      setDlqMessages(data as DeadLetterMessage[]);
      setDlqModalOpen(true);
    } catch (error) {
      console.error("加载死信队列失败:", error);
      message.error("加载失败");
    }
  };

  // 重试死信消息
  const handleRetryDLQ = async (messageId: string) => {
    try {
      await queueApi.reprocessDeadLetterMessage(messageId, currentTenantId!);
      message.success("重试成功");
      loadQueueData();
    } catch (error) {
      console.error("重试失败:", error);
      message.error("重试失败");
    }
  };

  // 删除死信消息
  const handleDeleteDLQ = async (messageId: string) => {
    try {
      await queueApi.deleteDeadLetterMessage(messageId, currentTenantId!);
      message.success("删除成功");
      loadQueueData();
    } catch (error) {
      console.error("删除失败:", error);
      message.error("删除失败");
    }
  };

  // 后端类型标签
  const getBackendTag = (backend: string) => {
    const config: Record<string, string> = {
      redis: "red",
      sqlite: "blue",
      memory: "default",
    };
    return <Tag color={config[backend] || "default"}>{backend}</Tag>;
  };

  // 状态标签
  const getStatusTag = (status: string) => {
    const config: Record<string, any> = {
      active: { color: "green", icon: <CheckCircleOutlined /> },
      paused: { color: "orange", icon: <WarningOutlined /> },
      error: { color: "red", icon: <CloseCircleOutlined /> },
    };
    const { color, icon } = config[status] || config.error;
    return <Tag color={color} icon={icon}>{status}</Tag>;
  };

  // 消息状态标签
  const getMessageStatusTag = (status: string) => {
    const config: Record<string, string> = {
      pending: "blue",
      processing: "orange",
      completed: "green",
      failed: "red",
      dead_letter: "red",
    };
    return <Tag color={config[status] || "default"}>{status}</Tag>;
  };

  // 使用率计算
  const getUsagePercent = (used: number, max: number) => {
    if (max === 0) return 0;
    return Math.round((used / max) * 100);
  };

  // 队列表格列
  const queueColumns = [
    {
      title: "队列名称",
      dataIndex: "queue_name",
      key: "queue_name",
      render: (text: string) => (
        <Space>
          <BarsOutlined />
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: "类型",
      dataIndex: "queue_type",
      key: "queue_type",
      render: (type: string) => <Tag>{type}</Tag>,
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      render: (status: string) => <Tag>{status}</Tag>,
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
      render: (_: any, record: MessageQueue) => (
        <Space size={4}>
          <Button
            type="link"
            size="small"
            icon={<ClearOutlined />}
            onClick={() => handleClear(record)}
          >
            清空
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Alert
        message="队列管理"
        description="管理消息队列，支持 Redis/SQLite/Memory 三种后端，包含死信队列处理"
        type="info"
        showIcon
        style={{ marginBottom: "16px" }}
      />

      {/* 统计信息 */}
      {stats && (
        <Card style={{ marginBottom: "16px" }}>
          <Row gutter={16}>
            <Col span={8}>
              <Statistic
                title="总消息数"
                value={stats.total_messages}
                valueStyle={{ color: "#1890ff" }}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="待处理消息"
                value={stats.pending_messages}
                valueStyle={{ color: "#faad14" }}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="死信消息"
                value={stats.dead_letter_messages || 0}
                valueStyle={{ color: (stats.dead_letter_messages || 0) > 0 ? "#ff4d4f" : "#52c41a" }}
              />
            </Col>
          </Row>
        </Card>
      )}

      {/* 队列列表 */}
      <Card
        title="消息队列"
        extra={
          <Space>
            <Button
              icon={<DownloadOutlined />}
              onClick={() => message.info("导出功能开发中")}
            >
              导出
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalOpen(true)}
            >
              新建队列
            </Button>
          </Space>
        }
      >
        <Table
          columns={queueColumns}
          dataSource={queues}
          loading={loading}
          rowKey="queue_id"
          pagination={false}
        />
      </Card>

      {/* 死信队列对话框 */}
      <Modal
        title="死信队列"
        open={dlqModalOpen}
        onCancel={() => setDlqModalOpen(false)}
        footer={null}
        width={900}
      >
        <Alert
          message={`共 ${dlqMessages.length} 条死信消息`}
          description="死信消息是处理失败的消息，可以选择重试或删除"
          type="warning"
          showIcon
          style={{ marginBottom: "16px" }}
        />
        <Table
          dataSource={dlqMessages as any}
          rowKey="message_id"
          size="small"
          columns={[
            {
              title: "消息 ID",
              dataIndex: "message_id",
              key: "message_id",
            },
            {
              title: "队列",
              dataIndex: "queue_id",
              key: "queue_id",
            },
            {
              title: "状态",
              dataIndex: "status",
              key: "status",
              render: getMessageStatusTag,
            },
            {
              title: "重试次数",
              dataIndex: "retry_count",
              key: "retry_count",
              render: (count: number) => (
                <Tag color={count > 3 ? "red" : "blue"}>{count}</Tag>
              ),
            },
            {
              title: "错误信息",
              dataIndex: "error_message",
              key: "error_message",
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
              render: (_: any, record: QueueMessage) => (
                <Space size={4}>
                  <Button
                    type="link"
                    size="small"
                    onClick={() => handleRetryDLQ(record.message_id)}
                  >
                    重试
                  </Button>
                  <Button
                    type="link"
                    size="small"
                    danger
                    onClick={() => handleDeleteDLQ(record.message_id)}
                  >
                    删除
                  </Button>
                </Space>
              ),
            },
          ]}
        />
      </Modal>

      {/* 创建队列对话框 */}
      <Modal
        title="创建队列"
        open={createModalOpen}
        onCancel={() => setCreateModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            name="queue_id"
            label="队列 ID"
            rules={[{ required: true, message: "请输入队列 ID" }]}
          >
            <Input placeholder="例如：message-queue-001" />
          </Form.Item>
          <Form.Item
            name="queue_name"
            label="队列名称"
            rules={[{ required: true, message: "请输入队列名称" }]}
          >
            <Input placeholder="例如：消息队列" />
          </Form.Item>
          <Form.Item
            name="backend"
            label="后端类型"
            rules={[{ required: true, message: "请选择后端类型" }]}
          >
            <Select>
              <Select.Option value="redis">Redis（生产推荐）</Select.Option>
              <Select.Option value="sqlite">SQLite（降级/开发）</Select.Option>
              <Select.Option value="memory">Memory（测试用）</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="max_size"
            label="最大容量"
            initialValue={10000}
          >
            <Input type="number" min={100} />
          </Form.Item>
          <Form.Item
            name="ttl_seconds"
            label="消息 TTL（秒）"
            initialValue={3600}
          >
            <Input type="number" min={60} />
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
    </div>
  );
};

export default QueueManagement;
