/**
 * 频道列表批量操作示例
 * v4.0 新增 - 演示批量操作功能在频道管理中的应用
 */
import React, { useState, useEffect } from "react";
import { Card, Table, Tag, Space, Button, Modal, message, Alert } from "antd";
import { PlusOutlined, ExportOutlined, ImportOutlined } from "@ant-design/icons";
import type { ChannelConfig } from "@/api/types";
import { channelApi } from "@/api/modules/channel";
import { useTenantStore } from "@/stores/tenantStore";
import BatchTable, { createBatchActions } from "@/components/BatchTable";
import { exportData } from "@/utils/export";

/**
 * 频道列表批量操作页面
 */
export const ChannelListWithBatch: React.FC = () => {
  const [channels, setChannels] = useState<ChannelConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const { currentTenantId } = useTenantStore();

  // 加载频道列表
  useEffect(() => {
    loadChannels();
  }, [currentTenantId]);

  const loadChannels = async () => {
    setLoading(true);
    try {
      const data = await channelApi.listChannels(currentTenantId);
      setChannels(data);
    } catch (error) {
      console.error("加载频道失败:", error);
    } finally {
      setLoading(false);
    }
  };

  // 批量删除
  const handleBatchDelete = async (selectedKeys: React.Key[], selectedRows: ChannelConfig[]) => {
    // 逐个删除
    const results = await Promise.allSettled(
      selectedRows.map((channel) =>
        channelApi.deleteChannel(channel.channel_id, currentTenantId)
      )
    );

    const successCount = results.filter((r) => r.status === "fulfilled").length;
    const failCount = results.filter((r) => r.status === "rejected").length;

    if (failCount === 0) {
      message.success(`成功删除 ${successCount} 个频道`);
      loadChannels();
    } else {
      message.warning(`删除完成：成功 ${successCount} 个，失败 ${failCount} 个`);
      loadChannels();
    }
  };

  // 批量启用
  const handleBatchEnable = async (selectedKeys: React.Key[], selectedRows: ChannelConfig[]) => {
    // 这里调用后端 API 批量启用
    message.info(`批量启用功能开发中：${selectedRows.length} 个频道`);
  };

  // 批量禁用
  const handleBatchDisable = async (selectedKeys: React.Key[], selectedRows: ChannelConfig[]) => {
    // 这里调用后端 API 批量禁用
    message.info(`批量禁用功能开发中：${selectedRows.length} 个频道`);
  };

  // 批量导出
  const handleBatchExport = async (selectedKeys: React.Key[], selectedRows: ChannelConfig[]) => {
    const columns = [
      { title: "频道 ID", dataIndex: "channel_id" },
      { title: "频道名称", dataIndex: "channel_name" },
      { title: "平台", dataIndex: "platform" },
      { title: "状态", dataIndex: "status" },
      { title: "描述", dataIndex: "description" },
    ];

    await exportData({
      filename: `channels_${Date.now()}`,
      format: "excel",
      data: selectedRows,
      columns,
    });
  };

  // 批量导入
  const handleBatchImport = () => {
    message.info("批量导入功能开发中");
  };

  // 创建批量操作
  const batchActions = createBatchActions<ChannelConfig>({
    onDelete: handleBatchDelete,
    onEnable: handleBatchEnable,
    onDisable: handleBatchDisable,
    onExport: handleBatchExport,
    onImport: handleBatchImport,
    deleteConfirmTitle: "确认删除频道",
    deleteConfirmContent: "删除频道将同时删除所有关联的会话和消息，确定要删除选中的频道吗？",
  });

  // 状态标签
  const getStatusTag = (status: string) => {
    const config: Record<string, any> = {
      active: { color: "green" },
      inactive: { color: "default" },
      error: { color: "red" },
      maintenance: { color: "orange" },
    };
    const { color } = config[status] || config.inactive;
    return <Tag color={color}>{status}</Tag>;
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
      title: "频道 ID",
      dataIndex: "channel_id",
      key: "channel_id",
      sorter: (a: ChannelConfig, b: ChannelConfig) =>
        a.channel_id.localeCompare(b.channel_id),
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
      render: getPlatformTag,
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      render: getStatusTag,
      filters: [
        { text: "活跃", value: "active" },
        { text: "未激活", value: "inactive" },
        { text: "错误", value: "error" },
        { text: "维护中", value: "maintenance" },
      ],
      onFilter: (value: any, record: ChannelConfig) => record.status === value,
    },
    {
      title: "描述",
      dataIndex: "description",
      key: "description",
      ellipsis: true,
    },
  ];

  return (
    <div>
      <Alert
        message="批量操作演示"
        description="支持批量选择、批量删除、批量启用/禁用、批量导出等功能"
        type="info"
        showIcon
        style={{ marginBottom: "16px" }}
      />

      {/* 频道列表 */}
      <Card
        title="频道列表"
        extra={
          <Space>
            <Button icon={<ImportOutlined />} onClick={handleBatchImport}>
              批量导入
            </Button>
            <Button icon={<ExportOutlined />} onClick={() => handleBatchExport(channels.map(c => c.channel_id), channels)}>
              导出全部
            </Button>
            <Button type="primary">
              新建频道
            </Button>
          </Space>
        }
      >
        <BatchTable<ChannelConfig>
          dataSource={channels}
          columns={columns}
          loading={loading}
          getRowKey={(record) => record.channel_id}
          batchActions={batchActions}
          maxSelection={50}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个`,
          }}
          onSelectionChange={(keys, rows) => {
            console.log("选择变更:", keys.length, rows.length);
          }}
        />
      </Card>

      {/* 使用说明 */}
      <Card title="使用说明" style={{ marginTop: "16px" }}>
        <ul>
          <li>点击表格左侧复选框选择单个项目</li>
          <li>点击表头复选框全选/取消全选</li>
          <li>选择项目后，顶部会显示批量操作栏</li>
          <li>支持批量删除、批量启用/禁用、批量导出等操作</li>
          <li>最多可选择 50 个项目</li>
          <li>删除操作需要二次确认</li>
        </ul>
      </Card>
    </div>
  );
};

export default ChannelListWithBatch;
