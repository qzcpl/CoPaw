/**
 * 灰度发布管理页面
 * v4.0 新增 - 支持灰度配置、流量分配、版本管理
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
  Progress,
  Slider,
  Alert,
  Timeline,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  RocketOutlined,
  ExperimentOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  PauseCircleOutlined,
} from "@ant-design/icons";
import type {
  GrayReleaseConfig,
  GrayReleaseRule,
  GrayReleaseHistory,
} from "@/api/types";
import { grayReleaseApi } from "@/api/modules/gray_release";
import { useTenantStore } from "@/stores/tenantStore";

const { TextArea } = Input;

/**
 * 灰度发布管理页面
 */
export const GrayReleaseManagement: React.FC = () => {
  const [configs, setConfigs] = useState<GrayReleaseConfig[]>([]);
  const [rules, setRules] = useState<GrayReleaseRule[]>([]);
  const [history, setHistory] = useState<GrayReleaseHistory[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState<GrayReleaseConfig | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [configModalOpen, setConfigModalOpen] = useState(false);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [form] = Form.useForm();
  const { currentTenantId } = useTenantStore();

  // 加载灰度配置
  useEffect(() => {
    loadGrayReleaseConfig();
  }, [currentTenantId]);

  const loadGrayReleaseConfig = async () => {
    setLoading(true);
    try {
      const configsData = await grayReleaseApi.listGrayReleaseConfigs(currentTenantId);
      setConfigs(configsData as unknown as GrayReleaseConfig[]);
      setHistory([]); // 暂不支持历史记录
    } catch (error) {
      console.error("加载灰度配置失败:", error);
      message.error("加载失败");
    } finally {
      setLoading(false);
    }
  };

  // 创建灰度配置
  const handleCreate = async (values: any) => {
    try {
      await grayReleaseApi.createGrayReleaseConfig({
        config_name: values.config_name,
        target_type: values.target_type || "agent",
        target_id: values.target_id,
        gray_strategy: "percentage",
        gray_percentage: values.traffic_percentage,
        description: values.description,
      });
      message.success("创建成功");
      setCreateModalOpen(false);
      loadGrayReleaseConfig();
    } catch (error) {
      console.error("创建失败:", error);
      message.error("创建失败");
    }
  };

  // 更新灰度配置
  const handleUpdate = async (values: any) => {
    if (!selectedConfig) return;
    try {
      await grayReleaseApi.updateGrayReleaseConfig(selectedConfig.config_id!, {
        config_name: values.config_name,
        gray_percentage: values.traffic_percentage,
        status: values.enabled ? "running" : "paused",
      });
      message.success("更新成功");
      setConfigModalOpen(false);
      loadGrayReleaseConfig();
    } catch (error) {
      console.error("更新失败:", error);
      message.error("更新失败");
    }
  };

  // 删除灰度配置
  const handleDelete = (config: GrayReleaseConfig) => {
    if (!config.config_id) {
      message.warning("配置 ID 不存在");
      return;
    }
    Modal.confirm({
      title: "确认删除",
      content: `确定要删除灰度配置 "${config.config_name}" 吗？`,
      okText: "确认",
      cancelText: "取消",
      okType: "danger",
      onOk: async () => {
        try {
          await grayReleaseApi.deleteGrayReleaseConfig(config.config_id!);
          message.success("删除成功");
          loadGrayReleaseConfig();
        } catch (error) {
          console.error("删除失败:", error);
          message.error("删除失败");
        }
      },
    });
  };

  // 配置灰度
  const handleConfig = (config: GrayReleaseConfig) => {
    setSelectedConfig(config);
    form.setFieldsValue({
      config_name: config.config_name,
      enabled: config.status === "active",
      gray_percentage: config.gray_percentage,
    });
    setConfigModalOpen(true);
  };

  // 查看历史
  const handleViewHistory = async () => {
    message.info("历史记录功能开发中");
    setHistoryModalOpen(true);
  };

  // 全量发布
  const handleFullRelease = async (config: GrayReleaseConfig) => {
    if (!config.config_id) {
      message.warning("配置 ID 不存在");
      return;
    }
    Modal.confirm({
      title: "确认全量发布",
      content: `确定要将 "${config.config_name}" 全量发布吗？`,
      okText: "确认",
      cancelText: "取消",
      okType: "danger",
      onOk: async () => {
        try {
          await grayReleaseApi.stopGrayRelease(config.config_id!);
          message.success("全量发布成功");
          loadGrayReleaseConfig();
        } catch (error) {
          console.error("全量发布失败:", error);
          message.error("全量发布失败");
        }
      },
    });
  };

  // 暂停灰度
  const handlePause = async (config: GrayReleaseConfig) => {
    if (!config.config_id) {
      message.warning("配置 ID 不存在");
      return;
    }
    try {
      await grayReleaseApi.pauseGrayRelease(config.config_id!);
      message.success("暂停成功");
      loadGrayReleaseConfig();
    } catch (error) {
      console.error("暂停失败:", error);
      message.error("暂停失败");
    }
  };

  // 恢复灰度
  const handleResume = async (config: GrayReleaseConfig) => {
    if (!config.config_id) {
      message.warning("配置 ID 不存在");
      return;
    }
    try {
      await grayReleaseApi.resumeGrayRelease(config.config_id!);
      message.success("恢复成功");
      loadGrayReleaseConfig();
    } catch (error) {
      console.error("恢复失败:", error);
      message.error("恢复失败");
    }
  };

  // 状态标签
  const getStatusTag = (enabled?: boolean, paused?: boolean, status?: string) => {
    // 优先使用 status 字段
    if (status) {
      if (status === "paused") {
        return <Tag color="orange" icon={<PauseCircleOutlined />}>暂停</Tag>;
      } else if (status === "completed") {
        return <Tag color="blue" icon={<CheckCircleOutlined />}>已完成</Tag>;
      } else if (status === "rolled_back") {
        return <Tag color="red" icon={<CloseCircleOutlined />}>已回滚</Tag>;
      } else if (status === "active") {
        return <Tag color="green" icon={<CheckCircleOutlined />}>运行中</Tag>;
      }
    }
    // 兼容旧代码
    if (paused) {
      return <Tag color="orange" icon={<PauseCircleOutlined />}>暂停</Tag>;
    }
    return enabled ? (
      <Tag color="green" icon={<CheckCircleOutlined />}>
        运行中
      </Tag>
    ) : (
      <Tag color="default" icon={<CloseCircleOutlined />}>
        未启动
      </Tag>
    );
  };

  // 阶段标签
  const getStageTag = (stage: string) => {
    const config: Record<string, string> = {
      canary: "orange",
      partial: "blue",
      full: "green",
      rolled_back: "red",
    };
    return <Tag color={config[stage] || "default"}>{stage}</Tag>;
  };

  // 配置表格列
  const configColumns = [
    {
      title: "发布 ID",
      dataIndex: "release_id",
      key: "release_id",
      render: (text: string) => (
        <Space>
          <ExperimentOutlined />
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: "配置名称",
      dataIndex: "config_name",
      key: "config_name",
    },
    {
      title: "目标类型",
      dataIndex: "target_type",
      key: "target_type",
      render: (text: string) => <Tag>{text}</Tag>,
    },
    {
      title: "目标 ID",
      dataIndex: "target_id",
      key: "target_id",
    },
    {
      title: "灰度策略",
      dataIndex: "gray_strategy",
      key: "gray_strategy",
    },
    {
      title: "流量比例",
      dataIndex: "gray_percentage",
      key: "gray_percentage",
      render: (percentage: number) => (
        <Space>
          <Progress
            percent={percentage}
            size="small"
            strokeColor="#1890ff"
            style={{ width: "100px" }}
          />
          <span>{percentage}%</span>
        </Space>
      ),
    },
    {
      title: "状态",
      key: "status",
      render: (_: any, record: GrayReleaseConfig) => getStatusTag(undefined, undefined, record.status),
    },
    {
      title: "操作",
      key: "action",
      render: (_: any, record: GrayReleaseConfig) => (
        <Space size={4}>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleConfig(record)}
          >
            配置
          </Button>
          {!record.paused && record.enabled ? (
            <Button
              type="link"
              size="small"
              onClick={() => handlePause(record)}
            >
              暂停
            </Button>
          ) : record.paused ? (
            <Button
              type="link"
              size="small"
              onClick={() => handleResume(record)}
            >
              恢复
            </Button>
          ) : null}
          <Button
            type="link"
            size="small"
            icon={<RocketOutlined />}
            onClick={() => handleFullRelease(record)}
          >
            全量发布
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
      title: "配置",
      dataIndex: "config_id",
      key: "config_id",
      render: (text: string) => {
        const config = configs.find((c) => c.config_id === text);
        return config?.config_name || text;
      },
    },
    {
      title: "匹配类型",
      dataIndex: "match_type",
      key: "match_type",
      render: (type: string) => <Tag>{type}</Tag>,
    },
    {
      title: "匹配条件",
      dataIndex: "match_condition",
      key: "match_condition",
      ellipsis: true,
    },
    {
      title: "目标版本",
      dataIndex: "target_version",
      key: "target_version",
    },
  ];

  return (
    <div>
      <Alert
        message="灰度发布管理"
        description="支持渐进式发布，通过流量控制实现平滑升级，降低发布风险"
        type="info"
        showIcon
        style={{ marginBottom: "16px" }}
      />

      {/* 灰度配置 */}
      <Card
        title="灰度配置"
        extra={
          <Space>
            <Button
              icon={<RocketOutlined />}
              onClick={handleViewHistory}
            >
              发布历史
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalOpen(true)}
            >
              新建配置
            </Button>
          </Space>
        }
      >
        <Table
          columns={configColumns}
          dataSource={configs}
          loading={loading}
          rowKey="release_id"
          pagination={false}
        />
      </Card>

      {/* 创建配置对话框 */}
      <Modal
        title="创建灰度发布"
        open={createModalOpen}
        onCancel={() => setCreateModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            name="release_name"
            label="发布名称"
            rules={[{ required: true, message: "请输入发布名称" }]}
          >
            <Input placeholder="例如：v2.0 灰度发布" />
          </Form.Item>
          <Form.Item
            name="call_id"
            label="callId"
            rules={[{ required: true, message: "请输入 callId" }]}
          >
            <Input placeholder="例如：400-001" />
          </Form.Item>
          <Form.Item
            name="target_agent_id"
            label="目标 Agent ID"
            rules={[{ required: true, message: "请输入目标 Agent ID" }]}
          >
            <Input placeholder="例如：agent-001" />
          </Form.Item>
          <Form.Item
            name="traffic_percentage"
            label="初始流量比例（%）"
            initialValue={10}
            rules={[{ required: true, message: "请输入流量比例" }]}
          >
            <Slider min={0} max={100} marks={{ 0: "0%", 10: "10%", 50: "50%", 100: "100%" }} />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="配置描述（可选）" />
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

      {/* 配置对话框 */}
      <Modal
        title="配置灰度发布"
        open={configModalOpen}
        onCancel={() => setConfigModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleUpdate}>
          <Form.Item
            name="release_name"
            label="发布名称"
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="traffic_percentage"
            label="流量比例（%）"
          >
            <Slider min={0} max={100} marks={{ 0: "0%", 25: "25%", 50: "50%", 75: "75%", 100: "100%" }} />
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
              <Button onClick={() => setConfigModalOpen(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 历史对话框 */}
      <Modal
        title="发布历史"
        open={historyModalOpen}
        onCancel={() => setHistoryModalOpen(false)}
        footer={null}
        width={800}
      >
        {history.length > 0 ? (
          <Timeline
            items={history.map((item, index) => ({
              key: item.release_id || index,
              color: item.event_type === "created" ? "green" : item.event_type === "rolled_back" ? "red" : "blue",
              children: (
                <div>
                  <div>
                    <strong>{item.event_type}</strong> - {item.description}
                  </div>
                  <div style={{ fontSize: "12px", color: "#8c8c8c" }}>
                    {new Date(item.occurred_at).toLocaleString("zh-CN")}
                  </div>
                </div>
              ),
            }))}
          />
        ) : (
          <div style={{ textAlign: "center", padding: "40px" }}>
            <p style={{ color: "#8c8c8c" }}>暂无历史记录</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default GrayReleaseManagement;
