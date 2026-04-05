/**
 * callId 管理页面组件
 * v4.0 新增 - 支持 callId 绑定、解绑、切换、暂停/恢复
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
  Drawer,
} from "antd";
import {
  PlusOutlined,
  PhoneOutlined,
  CheckCircleOutlined,
  PauseCircleOutlined,
  PlayCircleOutlined,
  SwapOutlined,
  DisconnectOutlined,
  HistoryOutlined,
} from "@ant-design/icons";
import type { CallIdBinding, CallIdChangeRecord } from "@/api/types";
import { callIdApi } from "@/api/modules/callid";
import { useTenantStore } from "@/stores/tenantStore";

const { TextArea } = Input;

/**
 * callId 管理页面
 */
export const CallIdManagement: React.FC = () => {
  const [callIds, setCallIds] = useState<CallIdBinding[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedCallId, setSelectedCallId] = useState<CallIdBinding | null>(null);
  const [bindModalOpen, setBindModalOpen] = useState(false);
  const [historyDrawerOpen, setHistoryDrawerOpen] = useState(false);
  const [history, setHistory] = useState<CallIdChangeRecord[]>([]);
  const [form] = Form.useForm();
  const { currentTenantId } = useTenantStore();

  // 加载 callId 列表
  useEffect(() => {
    loadCallIds();
  }, [currentTenantId]);

  const loadCallIds = async () => {
    setLoading(true);
    try {
      const data = await callIdApi.listCallIdBindings(currentTenantId);
      setCallIds(data);
    } catch (error) {
      console.error("加载 callId 失败:", error);
      message.error("加载失败");
    } finally {
      setLoading(false);
    }
  };

  // 绑定 callId
  const handleBind = async (values: any) => {
    try {
      await callIdApi.bindCallId({
        call_id: values.call_id,
        agent_id: values.agent_id,
        tenant_id: values.tenant_id || currentTenantId,
        channel_id: values.channel_id,
        routing_strategy: values.routing_strategy || "direct",
      });
      message.success("绑定成功");
      setBindModalOpen(false);
      loadCallIds();
    } catch (error) {
      console.error("绑定失败:", error);
      message.error("绑定失败");
    }
  };

  // 解绑 callId
  const handleUnbind = (callId: CallIdBinding) => {
    if (!callId.call_id) {
      message.warning("callId 不存在");
      return;
    }
    Modal.confirm({
      title: "确认解绑",
      content: `确定要解绑 callId "${callId.call_id}" 吗？`,
      okText: "确认",
      cancelText: "取消",
      okType: "danger",
      onOk: async () => {
        try {
          await callIdApi.unbindCallId({
            call_id: callId.call_id!,
            tenant_id: currentTenantId!,
          });
          message.success("解绑成功");
          loadCallIds();
        } catch (error) {
          console.error("解绑失败:", error);
          message.error("解绑失败");
        }
      },
    });
  };

  // 暂停 callId
  const handleSuspend = async (callId: CallIdBinding) => {
    if (!callId.call_id) {
      message.warning("callId 不存在");
      return;
    }
    Modal.confirm({
      title: "确认暂停",
      content: `确定要暂停 callId "${callId.call_id}" 吗？`,
      okText: "确认",
      cancelText: "取消",
      onOk: async () => {
        try {
          await callIdApi.suspendCallId(callId.call_id!, {
            call_id: callId.call_id!,
            tenant_id: currentTenantId!,
            reason: "手动暂停",
          });
          message.success("暂停成功");
          loadCallIds();
        } catch (error) {
          console.error("暂停失败:", error);
          message.error("暂停失败");
        }
      },
    });
  };

  // 恢复 callId
  const handleResume = async (callId: CallIdBinding) => {
    if (!callId.call_id) {
      message.warning("callId 不存在");
      return;
    }
    try {
      await callIdApi.resumeCallId(callId.call_id!, {
        call_id: callId.call_id!,
        tenant_id: currentTenantId!,
      });
      message.success("恢复成功");
      loadCallIds();
    } catch (error) {
      console.error("恢复失败:", error);
      message.error("恢复失败");
    }
  };

  // 查看历史
  const handleViewHistory = async (callId: CallIdBinding) => {
    if (!callId.call_id) {
      message.warning("callId 不存在");
      return;
    }
    setSelectedCallId(callId);
    try {
      const data = await callIdApi.getCallIdHistory(
        callId.call_id!,
        currentTenantId!,
        50
      );
      setHistory(data);
      setHistoryDrawerOpen(true);
    } catch (error) {
      console.error("加载历史失败:", error);
      message.error("加载历史失败");
    }
  };

  // 状态标签
  const getStatusTag = (status: string) => {
    const config: Record<string, any> = {
      active: { color: "green", icon: <CheckCircleOutlined /> },
      suspended: { color: "orange", icon: <PauseCircleOutlined /> },
      unbound: { color: "default", icon: <DisconnectOutlined /> },
    };
    const { color, icon } = config[status] || config.unbound;
    return <Tag icon={icon} color={color}>{status}</Tag>;
  };

  // 路由策略标签
  const getStrategyTag = (strategy: string) => {
    const config: Record<string, string> = {
      direct: "blue",
      round_robin: "green",
      weighted: "purple",
      skill_based: "cyan",
    };
    return <Tag color={config[strategy] || "default"}>{strategy}</Tag>;
  };

  // 表格列定义
  const columns = [
    {
      title: "callId",
      dataIndex: "call_id",
      key: "call_id",
      render: (text: string) => (
        <Space>
          <PhoneOutlined />
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: "类型",
      dataIndex: "call_type",
      key: "call_type",
      render: (type: string) => (
        <Tag color={type === "dedicated" ? "blue" : "default"}>
          {type === "dedicated" ? "专属" : "共享"}
        </Tag>
      ),
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      render: getStatusTag,
    },
    {
      title: "所属 Agent",
      dataIndex: "owner_agent_id",
      key: "owner_agent_id",
      ellipsis: true,
    },
    {
      title: "频道",
      dataIndex: "channel_id",
      key: "channel_id",
    },
    {
      title: "路由策略",
      dataIndex: "routing_strategy",
      key: "routing_strategy",
      render: getStrategyTag,
    },
    {
      title: "绑定时间",
      dataIndex: "bound_at",
      key: "bound_at",
      render: (text: string) => new Date(text).toLocaleString("zh-CN"),
    },
    {
      title: "操作",
      key: "action",
      render: (_: any, record: CallIdBinding) => (
        <Space size={4}>
          <Tooltip title="查看历史">
            <Button
              type="text"
              size="small"
              icon={<HistoryOutlined />}
              onClick={() => handleViewHistory(record)}
            />
          </Tooltip>
          {record.status === "active" ? (
            <Tooltip title="暂停">
              <Button
                type="text"
                size="small"
                danger
                icon={<PauseCircleOutlined />}
                onClick={() => handleSuspend(record)}
              />
            </Tooltip>
          ) : record.status === "suspended" ? (
            <Tooltip title="恢复">
              <Button
                type="text"
                size="small"
                icon={<PlayCircleOutlined />}
                onClick={() => handleResume(record)}
              />
            </Tooltip>
          ) : null}
          <Tooltip title="解绑">
            <Button
              type="text"
              size="small"
              danger
              icon={<DisconnectOutlined />}
              onClick={() => handleUnbind(record)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <>
      <Card
        title="callId 管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setBindModalOpen(true)}
          >
            绑定 callId
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={callIds}
          loading={loading}
          rowKey="call_id"
        />
      </Card>

      {/* 绑定 callId 对话框 */}
      <Modal
        title="绑定 callId"
        open={bindModalOpen}
        onCancel={() => setBindModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleBind}>
          <Form.Item
            name="call_id"
            label="callId"
            rules={[{ required: true, message: "请输入 callId" }]}
          >
            <Input placeholder="例如：400-001" />
          </Form.Item>
          <Form.Item
            name="agent_id"
            label="Agent ID"
            rules={[{ required: true, message: "请输入 Agent ID" }]}
          >
            <Input placeholder="例如：agent-001" />
          </Form.Item>
          <Form.Item
            name="channel_id"
            label="频道 ID"
            rules={[{ required: true, message: "请输入频道 ID" }]}
          >
            <Input placeholder="例如：dingtalk" />
          </Form.Item>
          <Form.Item
            name="routing_strategy"
            label="路由策略"
            initialValue="direct"
          >
            <Select>
              <Select.Option value="direct">直接路由</Select.Option>
              <Select.Option value="round_robin">轮询</Select.Option>
              <Select.Option value="weighted">加权轮询</Select.Option>
              <Select.Option value="skill_based">基于技能</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                绑定
              </Button>
              <Button onClick={() => setBindModalOpen(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 历史 drawer */}
      <Drawer
        title="变更历史"
        placement="right"
        width={600}
        open={historyDrawerOpen}
        onClose={() => setHistoryDrawerOpen(false)}
      >
        {selectedCallId && (
          <>
            <Descriptions title="callId 信息" column={1} bordered size="small">
              <Descriptions.Item label="callId">
                {selectedCallId.call_id}
              </Descriptions.Item>
              <Descriptions.Item label="类型">
                {selectedCallId.call_type}
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                {getStatusTag(selectedCallId.status)}
              </Descriptions.Item>
              <Descriptions.Item label="所属 Agent">
                {selectedCallId.owner_agent_id}
              </Descriptions.Item>
              <Descriptions.Item label="绑定时间">
                {new Date(selectedCallId.bound_at).toLocaleString("zh-CN")}
              </Descriptions.Item>
            </Descriptions>

            <div style={{ marginTop: "16px" }}>
              <h4>变更历史</h4>
              {history.length === 0 ? (
                <div style={{ textAlign: "center", color: "#8c8c8c" }}>
                  暂无变更记录
                </div>
              ) : (
                <Table
                  dataSource={history}
                  rowKey="created_at"
                  size="small"
                  columns={[
                    {
                      title: "变更类型",
                      dataIndex: "change_type",
                      key: "change_type",
                      render: (type: string) => <Tag>{type}</Tag>,
                    },
                    {
                      title: "操作人",
                      dataIndex: "operator",
                      key: "operator",
                    },
                    {
                      title: "原因",
                      dataIndex: "reason",
                      key: "reason",
                      ellipsis: true,
                    },
                    {
                      title: "时间",
                      dataIndex: "created_at",
                      key: "created_at",
                      render: (text: string) =>
                        new Date(text).toLocaleString("zh-CN"),
                    },
                  ]}
                />
              )}
            </div>
          </>
        )}
      </Drawer>
    </>
  );
};

export default CallIdManagement;
