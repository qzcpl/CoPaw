/**
 * 租户管理页面组件
 * v4.0 新增 - 支持租户创建、编辑、删除、配额管理
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
  Progress,
} from "antd";
import {
  PlusOutlined,
  ApartmentOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  DashboardOutlined,
} from "@ant-design/icons";
import type { TenantInfo, TenantCreateRequest, TenantUpdateRequest } from "@/api/types";
import { tenantApi } from "@/api/modules/tenant";

const { TextArea } = Input;

/**
 * 租户管理页面
 */
export const TenantManagement: React.FC = () => {
  const [tenants, setTenants] = useState<TenantInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedTenant, setSelectedTenant] = useState<TenantInfo | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [form] = Form.useForm();

  // 加载租户列表
  useEffect(() => {
    loadTenants();
  }, []);

  const loadTenants = async () => {
    setLoading(true);
    try {
      const data = await tenantApi.listTenants();
      setTenants(data);
    } catch (error) {
      console.error("加载租户失败:", error);
      message.error("加载失败");
    } finally {
      setLoading(false);
    }
  };

  // 创建租户
  const handleCreate = async (values: any) => {
    try {
      const req: TenantCreateRequest = {
        tenant_id: values.tenant_id,
        tenant_name: values.tenant_name,
        max_agents: values.max_agents || 10,
        max_callids: values.max_callids || 100,
        config: {
          description: values.description,
          max_bots: values.max_bots || 10,
          max_channels: values.max_channels || 5,
        },
      };
      await tenantApi.createTenant(req);
      message.success("创建成功");
      setCreateModalOpen(false);
      loadTenants();
    } catch (error) {
      console.error("创建失败:", error);
      message.error("创建失败");
    }
  };

  // 更新租户
  const handleUpdate = async (values: any) => {
    if (!selectedTenant) return;
    try {
      const req: TenantUpdateRequest = {
        tenant_name: values.tenant_name,
        max_agents: values.max_agents,
        max_callids: values.max_callids,
        config: {
          description: values.description,
          enabled: values.enabled,
          max_bots: values.max_bots,
          max_channels: values.max_channels,
        },
      };
      await tenantApi.updateTenant(selectedTenant.tenant_id, req);
      message.success("更新成功");
      setEditModalOpen(false);
      loadTenants();
    } catch (error) {
      console.error("更新失败:", error);
      message.error("更新失败");
    }
  };

  // 删除租户
  const handleDelete = (tenant: TenantInfo) => {
    Modal.confirm({
      title: "确认删除",
      content: `确定要删除租户 "${tenant.tenant_name}" 吗？此操作不可恢复！`,
      okText: "确认",
      cancelText: "取消",
      okType: "danger",
      onOk: async () => {
        try {
          await tenantApi.deleteTenant(tenant.tenant_id);
          message.success("删除成功");
          loadTenants();
        } catch (error) {
          console.error("删除失败:", error);
          message.error("删除失败");
        }
      },
    });
  };

  // 查看详情
  const handleViewDetail = (tenant: TenantInfo) => {
    setSelectedTenant(tenant);
    setDetailModalOpen(true);
  };

  // 编辑租户
  const handleEdit = (tenant: TenantInfo) => {
    setSelectedTenant(tenant);
    form.setFieldsValue({
      tenant_name: tenant.tenant_name,
      description: tenant.description,
      enabled: tenant.enabled,
      max_bots: tenant.max_bots,
      max_channels: tenant.max_channels,
      max_callids: tenant.max_callids,
    });
    setEditModalOpen(true);
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

  // 使用率计算
  const getUsagePercent = (used: number | undefined, max: number | undefined) => {
    if (!used || !max) return 0;
    return Math.round((used / max) * 100);
  };

  // 使用率进度条
  const getUsageProgress = (used: number | undefined, max: number | undefined) => {
    const percent = getUsagePercent(used, max);
    return (
      <Tooltip title={`${used || 0}/${max || 0}`}>
        <Progress
          percent={percent}
          strokeColor={
            percent >= 90 ? "#ff4d4f" : percent >= 70 ? "#faad14" : "#52c41a"
          }
          size="small"
          style={{ width: "120px" }}
        />
      </Tooltip>
    );
  };

  // 表格列定义
  const columns = [
    {
      title: "租户 ID",
      dataIndex: "tenant_id",
      key: "tenant_id",
      render: (text: string) => (
        <Space>
          <ApartmentOutlined />
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: "租户名称",
      dataIndex: "tenant_name",
      key: "tenant_name",
    },
    {
      title: "状态",
      key: "status",
      render: (_: any, record: TenantInfo) => getStatusTag(record.enabled),
    },
    {
      title: "Bot 使用",
      key: "bot_usage",
      render: (_: any, record: TenantInfo) =>
        getUsageProgress(record.bot_count, record.max_bots),
    },
    {
      title: "频道使用",
      key: "channel_usage",
      render: (_: any, record: TenantInfo) =>
        getUsageProgress(record.channel_count, record.max_channels),
    },
    {
      title: "callId 使用",
      key: "callid_usage",
      render: (_: any, record: TenantInfo) =>
        getUsageProgress(record.callid_count, record.max_callids),
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
      render: (_: any, record: TenantInfo) => (
        <Space size={4}>
          <Tooltip title="详情">
            <Button
              type="text"
              size="small"
              icon={<DashboardOutlined />}
              onClick={() => handleViewDetail(record)}
            />
          </Tooltip>
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
    <>
      <Card
        title="租户管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalOpen(true)}
          >
            新建租户
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={tenants}
          loading={loading}
          rowKey="tenant_id"
        />
      </Card>

      {/* 创建租户对话框 */}
      <Modal
        title="创建租户"
        open={createModalOpen}
        onCancel={() => setCreateModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            name="tenant_id"
            label="租户 ID"
            rules={[{ required: true, message: "请输入租户 ID" }]}
          >
            <Input placeholder="例如：tenant-001" />
          </Form.Item>
          <Form.Item
            name="tenant_name"
            label="租户名称"
            rules={[{ required: true, message: "请输入租户名称" }]}
          >
            <Input placeholder="例如：测试租户" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="租户描述（可选）" />
          </Form.Item>
          <Form.Item
            name="max_bots"
            label="最大 Bot 数"
            initialValue={10}
          >
            <Input type="number" min={1} />
          </Form.Item>
          <Form.Item
            name="max_channels"
            label="最大频道数"
            initialValue={5}
          >
            <Input type="number" min={1} />
          </Form.Item>
          <Form.Item
            name="max_callids"
            label="最大 callId 数"
            initialValue={100}
          >
            <Input type="number" min={1} />
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

      {/* 编辑租户对话框 */}
      <Modal
        title="编辑租户"
        open={editModalOpen}
        onCancel={() => setEditModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleUpdate}>
          <Form.Item
            name="tenant_name"
            label="租户名称"
            rules={[{ required: true, message: "请输入租户名称" }]}
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
          <Form.Item name="max_bots" label="最大 Bot 数">
            <Input type="number" min={1} />
          </Form.Item>
          <Form.Item name="max_channels" label="最大频道数">
            <Input type="number" min={1} />
          </Form.Item>
          <Form.Item name="max_callids" label="最大 callId 数">
            <Input type="number" min={1} />
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
      {selectedTenant && detailModalOpen && (
        <Modal
          title={
            <Space>
              <ApartmentOutlined />
              <span>{selectedTenant.tenant_name}</span>
              <Tag>{selectedTenant.tenant_id}</Tag>
            </Space>
          }
          open={detailModalOpen}
          onCancel={() => setDetailModalOpen(false)}
          footer={null}
          width={800}
        >
          <Descriptions title="租户信息" column={1} bordered>
            <Descriptions.Item label="租户 ID">
              {selectedTenant.tenant_id}
            </Descriptions.Item>
            <Descriptions.Item label="租户名称">
              {selectedTenant.tenant_name}
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              {getStatusTag(selectedTenant.enabled)}
            </Descriptions.Item>
            <Descriptions.Item label="描述">
              {selectedTenant.description || "无"}
            </Descriptions.Item>
            <Descriptions.Item label="Bot 配额">
              {selectedTenant.bot_count}/{selectedTenant.max_bots}
              {getUsageProgress(selectedTenant.bot_count, selectedTenant.max_bots)}
            </Descriptions.Item>
            <Descriptions.Item label="频道配额">
              {selectedTenant.channel_count}/{selectedTenant.max_channels}
              {getUsageProgress(selectedTenant.channel_count, selectedTenant.max_channels)}
            </Descriptions.Item>
            <Descriptions.Item label="callId 配额">
              {selectedTenant.callid_count}/{selectedTenant.max_callids}
              {getUsageProgress(selectedTenant.callid_count, selectedTenant.max_callids)}
            </Descriptions.Item>
            <Descriptions.Item label="创建时间">
              {new Date(selectedTenant.created_at).toLocaleString("zh-CN")}
            </Descriptions.Item>
            <Descriptions.Item label="更新时间">
              {new Date(selectedTenant.updated_at).toLocaleString("zh-CN")}
            </Descriptions.Item>
          </Descriptions>
        </Modal>
      )}
    </>
  );
};

export default TenantManagement;
