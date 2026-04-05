/**
 * 路由配置管理页面
 * v4.0 新增 - 支持路由策略配置、Agent 管理、故障转移设置
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
  Descriptions,
  Slider,
  InputNumber,
  Alert,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SettingOutlined,
  SyncOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from "@ant-design/icons";
import type {
  RoutingStrategy,
  RoutingRule,
  AgentRoutingStatus,
  FailoverConfig,
} from "@/api/types";
import { routingApi } from "@/api/modules/routing";
import { useTenantStore } from "@/stores/tenantStore";

const { TextArea } = Input;

/**
 * 路由配置管理页面
 */
export const RoutingManagement: React.FC = () => {
  const [strategies, setStrategies] = useState<RoutingStrategy[]>([]);
  const [rules, setRules] = useState<RoutingRule[]>([]);
  const [agentStatus, setAgentStatus] = useState<AgentRoutingStatus[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState<RoutingStrategy | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [configModalOpen, setConfigModalOpen] = useState(false);
  const [form] = Form.useForm();
  const { currentTenantId } = useTenantStore();

  // 加载路由配置
  useEffect(() => {
    loadRoutingConfig();
  }, [currentTenantId]);

  const loadRoutingConfig = async () => {
    setLoading(true);
    try {
      const [strategiesData, configsData, agentStatusData] = await Promise.all([
        routingApi.listRoutingStrategies(currentTenantId!),
        routingApi.listRoutingConfigs(currentTenantId!),
        routingApi.getAgentRoutingStatus(currentTenantId!),
      ]);
      setStrategies(strategiesData);
      setRules(configsData as any);
      setAgentStatus(agentStatusData);
    } catch (error) {
      console.error("加载路由配置失败:", error);
      message.error("加载失败");
    } finally {
      setLoading(false);
    }
  };

  // 创建路由策略
  const handleCreate = async (values: any) => {
    try {
      await routingApi.createRoutingStrategy({
        strategy_name: values.strategy_name,
        strategy_type: values.strategy_type,
        tenant_id: values.tenant_id || currentTenantId!,
        config: values.config || {},
      });
      message.success("创建成功");
      setCreateModalOpen(false);
      loadRoutingConfig();
    } catch (error) {
      console.error("创建失败:", error);
      message.error("创建失败");
    }
  };

  // 更新路由策略
  const handleUpdate = async (values: any) => {
    if (!selectedStrategy) return;
    try {
      await routingApi.updateRoutingStrategy(selectedStrategy.strategy_id, {
        strategy_name: values.strategy_name,
        status: values.enabled ? "active" as const : "inactive" as const,
        config: values.config,
      });
      message.success("更新成功");
      setConfigModalOpen(false);
      loadRoutingConfig();
    } catch (error) {
      console.error("更新失败:", error);
      message.error("更新失败");
    }
  };

  // 删除路由策略
  const handleDelete = (strategy: RoutingStrategy) => {
    Modal.confirm({
      title: "确认删除",
      content: `确定要删除路由策略 "${strategy.strategy_name}" 吗？`,
      okText: "确认",
      cancelText: "取消",
      okType: "danger",
      onOk: async () => {
        try {
          await routingApi.deleteRoutingStrategy(strategy.strategy_id);
          message.success("删除成功");
          loadRoutingConfig();
        } catch (error) {
          console.error("删除失败:", error);
          message.error("删除失败");
        }
      },
    });
  };

  // 配置路由策略
  const handleConfig = (strategy: RoutingStrategy) => {
    setSelectedStrategy(strategy);
    form.setFieldsValue({
      strategy_name: strategy.strategy_name,
      enabled: strategy.status === "active",
      config: strategy.config,
    });
    setConfigModalOpen(true);
  };

  // 策略类型标签
  const getTypeTag = (type: string) => {
    const config: Record<string, string> = {
      direct: "blue",
      round_robin: "green",
      weighted: "purple",
      skill_based: "cyan",
      least_busy: "orange",
      priority: "red",
    };
    return <Tag color={config[type] || "default"}>{type}</Tag>;
  };

  // 状态标签
  const getStatusTag = (status: string) => {
    if (status === "active") {
      return (
        <Tag color="green" icon={<CheckCircleOutlined />}>
          启用
        </Tag>
      );
    } else if (status === "inactive") {
      return (
        <Tag color="default" icon={<CloseCircleOutlined />}>
          禁用
        </Tag>
      );
    } else {
      return (
        <Tag color="orange">{status}</Tag>
      );
    }
  };

  // Agent 状态标签
  const getAgentStatusTag = (status: string) => {
    const config: Record<string, any> = {
      available: { color: "green", icon: <CheckCircleOutlined /> },
      busy: { color: "orange", icon: <SyncOutlined /> },
      offline: { color: "red", icon: <CloseCircleOutlined /> },
    };
    const { color, icon } = config[status] || config.offline;
    return <Tag color={color} icon={icon}>{status}</Tag>;
  };

  // 策略表格列
  const strategyColumns = [
    {
      title: "策略 ID",
      dataIndex: "strategy_id",
      key: "strategy_id",
      render: (text: string) => <strong>{text}</strong>,
    },
    {
      title: "策略名称",
      dataIndex: "strategy_name",
      key: "strategy_name",
    },
    {
      title: "类型",
      dataIndex: "strategy_type",
      key: "strategy_type",
      render: getTypeTag,
    },
    {
      title: "状态",
      key: "status",
      render: (_: any, record: RoutingStrategy) => getStatusTag(record.status),
    },
    {
      title: "描述",
      dataIndex: "description",
      key: "description",
      ellipsis: true,
    },
    {
      title: "操作",
      key: "action",
      render: (_: any, record: RoutingStrategy) => (
        <Space size={4}>
          <Button
            type="link"
            size="small"
            icon={<SettingOutlined />}
            onClick={() => handleConfig(record)}
          >
            配置
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

  // 规则表格列
  const ruleColumns = [
    {
      title: "规则 ID",
      dataIndex: "rule_id",
      key: "rule_id",
    },
    {
      title: "策略",
      dataIndex: "strategy_id",
      key: "strategy_id",
      render: (text: string) => {
        const strategy = strategies.find((s) => s.strategy_id === text);
        return strategy?.strategy_name || text;
      },
    },
    {
      title: "优先级",
      dataIndex: "priority",
      key: "priority",
      render: (priority: number) => <Tag color={priority > 50 ? "red" : "blue"}>{priority}</Tag>,
    },
    {
      title: "条件",
      dataIndex: "condition",
      key: "condition",
      ellipsis: true,
    },
    {
      title: "目标 Agent",
      dataIndex: "target_agent_id",
      key: "target_agent_id",
    },
  ];

  // 策略类型选项
  const strategyTypeOptions = [
    { value: "direct", label: "直接路由" },
    { value: "round_robin", label: "轮询" },
    { value: "weighted", label: "加权轮询" },
    { value: "skill_based", label: "基于技能" },
    { value: "least_busy", label: "最闲优先" },
    { value: "priority", label: "优先级" },
  ];

  return (
    <div>
      <Alert
        message="路由配置管理"
        description="配置消息路由策略，支持 6 种路由算法和故障转移机制"
        type="info"
        showIcon
        style={{ marginBottom: "16px" }}
      />

      {/* 路由策略 */}
      <Card
        title="路由策略"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalOpen(true)}
          >
            新建策略
          </Button>
        }
      >
        <Table
          columns={strategyColumns}
          dataSource={strategies}
          loading={loading}
          rowKey="strategy_id"
          pagination={false}
        />
      </Card>

      {/* 路由规则 */}
      <Card title="路由规则" style={{ marginTop: "16px" }}>
        <Table
          columns={ruleColumns}
          dataSource={rules}
          loading={loading}
          rowKey="rule_id"
          pagination={false}
        />
      </Card>

      {/* Agent 路由状态 */}
      <Card title="Agent 路由状态" style={{ marginTop: "16px" }}>
        <Table
          dataSource={agentStatus}
          loading={loading}
          rowKey="agent_id"
          pagination={false}
          columns={[
            {
              title: "Agent ID",
              dataIndex: "agent_id",
              key: "agent_id",
            },
            {
              title: "状态",
              dataIndex: "status",
              key: "status",
              render: getAgentStatusTag,
            },
            {
              title: "当前会话数",
              dataIndex: "active_sessions",
              key: "active_sessions",
            },
            {
              title: "最大会话数",
              dataIndex: "max_sessions",
              key: "max_sessions",
            },
            {
              title: "负载率",
              key: "load",
              render: (_: any, record: AgentRoutingStatus) => {
                const loadPercent = Math.round((record.current_load / record.max_load) * 100);
                return (
                  <Space>
                    <Slider
                      value={loadPercent}
                      disabled
                      style={{ width: "150px" }}
                      tipFormatter={(value: number | undefined) => `${value}%`}
                    />
                    <span>{loadPercent}%</span>
                  </Space>
                );
              },
            },
          ]}
        />
      </Card>

      {/* 创建策略对话框 */}
      <Modal
        title="创建路由策略"
        open={createModalOpen}
        onCancel={() => setCreateModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            name="strategy_id"
            label="策略 ID"
            rules={[{ required: true, message: "请输入策略 ID" }]}
          >
            <Input placeholder="例如：round-robin-001" />
          </Form.Item>
          <Form.Item
            name="strategy_name"
            label="策略名称"
            rules={[{ required: true, message: "请输入策略名称" }]}
          >
            <Input placeholder="例如：轮询策略" />
          </Form.Item>
          <Form.Item
            name="strategy_type"
            label="策略类型"
            rules={[{ required: true, message: "请选择策略类型" }]}
          >
            <Select options={strategyTypeOptions} />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="策略描述（可选）" />
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

      {/* 配置策略对话框 */}
      <Modal
        title="配置路由策略"
        open={configModalOpen}
        onCancel={() => setConfigModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleUpdate}>
          <Form.Item
            name="strategy_name"
            label="策略名称"
            rules={[{ required: true, message: "请输入策略名称" }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="enabled"
            label="启用状态"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          <Form.Item
            name="config.weight"
            label="权重（加权轮询）"
            tooltip="仅加权轮询策略使用"
          >
            <InputNumber min={1} max={100} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item
            name="config.priority"
            label="优先级（优先级策略）"
            tooltip="仅优先级策略使用"
          >
            <InputNumber min={1} max={10} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item
            name="config.failover_enabled"
            label="故障转移"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          <Form.Item
            name="config.failover_timeout"
            label="故障转移超时（秒）"
            tooltip="超时后自动切换到备用 Agent"
          >
            <InputNumber min={5} max={300} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                保存
              </Button>
              <Button onClick={() => setConfigModalOpen(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default RoutingManagement;
