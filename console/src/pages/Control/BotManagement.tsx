/**
 * Bot 管理页面组件
 * v4.0 新增 - 支持 Bot 创建、编辑、删除、密钥管理
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
  Tooltip,
  Descriptions,
  Switch,
} from "antd";
import {
  PlusOutlined,
  RobotOutlined,
  EditOutlined,
  DeleteOutlined,
  KeyOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  CopyOutlined,
} from "@ant-design/icons";
import type { BotInfo, BotCreateRequest, BotUpdateRequest } from "@/api/types";
import { botApi } from "@/api/modules/bot";
import { useTenantStore } from "@/stores/tenantStore";

const { TextArea } = Input;

/**
 * Bot 管理页面
 */
export const BotManagement: React.FC = () => {
  const [bots, setBots] = useState<BotInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedBot, setSelectedBot] = useState<BotInfo | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [form] = Form.useForm();
  const { currentTenantId } = useTenantStore();

  // 加载 Bot 列表
  useEffect(() => {
    loadBots();
  }, [currentTenantId]);

  const loadBots = async () => {
    setLoading(true);
    try {
      const data = await botApi.listBots(currentTenantId);
      setBots(data);
    } catch (error) {
      console.error("加载 Bot 失败:", error);
      message.error("加载失败");
    } finally {
      setLoading(false);
    }
  };

  // 创建 Bot
  const handleCreate = async (values: any) => {
    try {
      const req: BotCreateRequest = {
        bot_name: values.name,
        platform: values.platform,
        tenant_id: values.tenant_id || currentTenantId,
        config: {
          description: values.description,
          bot_id: values.bot_id,
          bot_secret: values.bot_secret,
        },
      };
      await botApi.createBot(req);
      message.success("创建成功");
      setCreateModalOpen(false);
      loadBots();
    } catch (error) {
      console.error("创建失败:", error);
      message.error("创建失败");
    }
  };

  // 更新 Bot
  const handleUpdate = async (values: any) => {
    if (!selectedBot) return;
    try {
      const req: BotUpdateRequest = {
        bot_name: values.name,
        config: {
          description: values.description,
          enabled: values.enabled,
        },
      };
      await botApi.updateBot(selectedBot.bot_id, req);
      message.success("更新成功");
      setEditModalOpen(false);
      loadBots();
    } catch (error) {
      console.error("更新失败:", error);
      message.error("更新失败");
    }
  };

  // 删除 Bot
  const handleDelete = (bot: BotInfo) => {
    Modal.confirm({
      title: "确认删除",
      content: `确定要删除 Bot "${bot.bot_name}" 吗？`,
      okText: "确认",
      cancelText: "取消",
      okType: "danger",
      onOk: async () => {
        try {
          await botApi.deleteBot(bot.bot_id);
          message.success("删除成功");
          loadBots();
        } catch (error) {
          console.error("删除失败:", error);
          message.error("删除失败");
        }
      },
    });
  };

  // 查看详情
  const handleViewDetail = (bot: BotInfo) => {
    setSelectedBot(bot);
    setDetailModalOpen(true);
  };

  // 编辑 Bot
  const handleEdit = (bot: BotInfo) => {
    setSelectedBot(bot);
    form.setFieldsValue({
      name: bot.name,
      description: bot.description,
      enabled: bot.enabled,
    });
    setEditModalOpen(true);
  };

  // 复制密钥
  const handleCopySecret = (secret: string | undefined) => {
    if (secret) {
      navigator.clipboard.writeText(secret);
      message.success("已复制到剪贴板");
    }
  };

  // 状态标签
  const getStatusTag = (enabled: boolean | undefined) => {
    return enabled ? (
      <Tag color="green" icon={<CheckCircleOutlined />}>
        启用
      </Tag>
    ) : (
      <Tag color="default" icon={<CloseCircleOutlined />}>
        禁用
      </Tag>
    );
  };

  // 平台标签
  const getPlatformTag = (platform: string) => {
    const config: Record<string, string> = {
      dingtalk: "blue",
      feishu: "cyan",
      wechat: "green",
      web: "default",
      discord: "purple",
      telegram: "orange",
    };
    return <Tag color={config[platform] || "default"}>{platform}</Tag>;
  };

  // 表格列定义
  const columns = [
    {
      title: "Bot ID",
      dataIndex: "bot_id",
      key: "bot_id",
      render: (text: string) => (
        <Space>
          <RobotOutlined />
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: "名称",
      dataIndex: "bot_name",
      key: "bot_name",
    },
    {
      title: "平台",
      dataIndex: "platform",
      key: "platform",
      render: getPlatformTag,
    },
    {
      title: "状态",
      key: "status",
      render: (_: any, record: BotInfo) => getStatusTag(record.enabled),
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
      render: (_: any, record: BotInfo) => (
        <Space size={4}>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
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
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  // 平台选项
  const platformOptions = [
    { value: "dingtalk", label: "钉钉" },
    { value: "feishu", label: "飞书" },
    { value: "wechat", label: "微信" },
    { value: "web", label: "Web" },
    { value: "discord", label: "Discord" },
    { value: "telegram", label: "Telegram" },
  ];

  return (
    <>
      <Card
        title="Bot 管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalOpen(true)}
          >
            新建 Bot
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={bots}
          loading={loading}
          rowKey="bot_id"
        />
      </Card>

      {/* 创建 Bot 对话框 */}
      <Modal
        title="创建 Bot"
        open={createModalOpen}
        onCancel={() => setCreateModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            name="bot_id"
            label="Bot ID"
            rules={[{ required: true, message: "请输入 Bot ID" }]}
          >
            <Input placeholder="例如：dingtalk-bot-001" />
          </Form.Item>
          <Form.Item
            name="name"
            label="Bot 名称"
            rules={[{ required: true, message: "请输入 Bot 名称" }]}
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
          <Form.Item
            name="bot_secret"
            label="Bot Secret"
            rules={[{ required: true, message: "请输入 Bot Secret" }]}
          >
            <Input.Password placeholder="从平台获取" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="Bot 描述（可选）" />
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

      {/* 编辑 Bot 对话框 */}
      <Modal
        title="编辑 Bot"
        open={editModalOpen}
        onCancel={() => setEditModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleUpdate}>
          <Form.Item
            name="name"
            label="Bot 名称"
            rules={[{ required: true, message: "请输入 Bot 名称" }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item
            name="enabled"
            label="启用状态"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                保存
              </Button>
              <Button onClick={() => setEditModalOpen(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 详情对话框 */}
      {selectedBot && detailModalOpen && (
        <Modal
          title={
            <Space>
              <RobotOutlined />
              <span>{selectedBot.name}</span>
              <Tag>{selectedBot.bot_id}</Tag>
            </Space>
          }
          open={detailModalOpen}
          onCancel={() => setDetailModalOpen(false)}
          footer={null}
          width={700}
        >
          <Descriptions title="Bot 信息" column={1} bordered>
            <Descriptions.Item label="Bot ID">
              {selectedBot.bot_id}
            </Descriptions.Item>
            <Descriptions.Item label="名称">
              {selectedBot.bot_name}
            </Descriptions.Item>
            <Descriptions.Item label="平台">
              {getPlatformTag(selectedBot.platform)}
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              {getStatusTag(selectedBot.enabled)}
            </Descriptions.Item>
            <Descriptions.Item label="租户 ID">
              {selectedBot.tenant_id}
            </Descriptions.Item>
            <Descriptions.Item label="描述">
              {selectedBot.description || "无"}
            </Descriptions.Item>
            <Descriptions.Item label="Bot Secret">
              <Space>
                <Input.Password
                  value={selectedBot.bot_secret}
                  readOnly
                  style={{ width: "300px" }}
                />
                <Tooltip title="复制">
                  <Button
                    icon={<CopyOutlined />}
                    onClick={() => handleCopySecret(selectedBot.bot_secret)}
                  />
                </Tooltip>
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="创建时间">
              {new Date(selectedBot.created_at).toLocaleString("zh-CN")}
            </Descriptions.Item>
            <Descriptions.Item label="更新时间">
              {new Date(selectedBot.updated_at).toLocaleString("zh-CN")}
            </Descriptions.Item>
          </Descriptions>
        </Modal>
      )}
    </>
  );
};

export default BotManagement;
