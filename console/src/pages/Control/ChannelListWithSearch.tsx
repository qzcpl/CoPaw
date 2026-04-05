/**
 * 频道列表高级搜索示例
 * v4.0 新增 - 演示高级搜索功能在频道管理中的应用
 */
import React, { useState, useEffect, useMemo } from "react";
import { Card, Table, Tag, Space, Button, Alert } from "antd";
import { PlusOutlined, ExportOutlined } from "@ant-design/icons";
import type { ChannelConfig } from "@/api/types";
import { channelApi } from "@/api/modules/channel";
import { useTenantStore } from "@/stores/tenantStore";
import AdvancedSearch, { type SearchCondition } from "@/components/AdvancedSearch";
import Highlight, { HighlightCell } from "@/components/Highlight";

/**
 * 频道列表高级搜索页面
 */
export const ChannelListWithSearch: React.FC = () => {
  const [channels, setChannels] = useState<ChannelConfig[]>([]);
  const [filteredChannels, setFilteredChannels] = useState<ChannelConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [keyword, setKeyword] = useState("");
  const [conditions, setConditions] = useState<SearchCondition[]>([]);
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
      setFilteredChannels(data);
    } catch (error) {
      console.error("加载频道失败:", error);
    } finally {
      setLoading(false);
    }
  };

  // 搜索处理
  const handleSearch = (searchKeyword: string, searchConditions: SearchCondition[]) => {
    setKeyword(searchKeyword);
    setConditions(searchConditions);
    filterData(searchKeyword, searchConditions);
  };

  // 清空搜索
  const handleClear = () => {
    setKeyword("");
    setConditions([]);
    setFilteredChannels(channels);
  };

  // 条件变更
  const handleConditionsChange = (newConditions: SearchCondition[]) => {
    setConditions(newConditions);
    filterData(keyword, newConditions);
  };

  // 数据筛选
  const filterData = (searchKeyword: string, searchConditions: SearchCondition[]) => {
    let result = [...channels];

    // 关键词搜索（搜索名称、ID、描述）
    if (searchKeyword.trim()) {
      const keywordLower = searchKeyword.toLowerCase();
      result = result.filter(
        (channel) =>
          channel.channel_name.toLowerCase().includes(keywordLower) ||
          channel.channel_id.toLowerCase().includes(keywordLower) ||
          (channel.description && channel.description.toLowerCase().includes(keywordLower))
      );
    }

    // 条件筛选
    searchConditions.forEach((condition) => {
      result = result.filter((channel) => {
        let value: string | number | undefined;

        // 获取字段值
        switch (condition.field) {
          case "name":
            value = channel.channel_name;
            break;
          case "id":
            value = channel.channel_id;
            break;
          case "platform":
            value = channel.platform;
            break;
          case "status":
            value = channel.status;
            break;
          default:
            value = undefined;
        }

        if (value === undefined) return false;

        const strValue = String(value).toLowerCase();
        const conditionValue = String(condition.value).toLowerCase();

        // 应用运算符
        switch (condition.operator) {
          case "contains":
            return strValue.includes(conditionValue);
          case "equals":
            return strValue === conditionValue;
          case "startsWith":
            return strValue.startsWith(conditionValue);
          case "endsWith":
            return strValue.endsWith(conditionValue);
          default:
            return true;
        }
      });
    });

    setFilteredChannels(result);
  };

  // 搜索字段选项
  const searchFields = [
    { label: "频道名称", value: "name" },
    { label: "频道 ID", value: "id" },
    { label: "平台", value: "platform" },
    { label: "状态", value: "status" },
  ];

  // 运算符选项
  const operators = [
    { label: "包含", value: "contains" as const },
    { label: "等于", value: "equals" as const },
    { label: "开始于", value: "startsWith" as const },
    { label: "结束于", value: "endsWith" as const },
  ];

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
      render: (text: string) => (
        <HighlightCell text={text} keyword={keyword} />
      ),
    },
    {
      title: "频道名称",
      dataIndex: "channel_name",
      key: "channel_name",
      render: (text: string) => (
        <HighlightCell text={text} keyword={keyword} />
      ),
    },
    {
      title: "平台",
      dataIndex: "platform",
      key: "platform",
      render: (platform: string) => getPlatformTag(platform),
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      render: getStatusTag,
    },
    {
      title: "描述",
      dataIndex: "description",
      key: "description",
      ellipsis: true,
      render: (text: string) => (
        <HighlightCell text={text || "-"} keyword={keyword} maxLength={50} />
      ),
    },
  ];

  return (
    <div>
      <Alert
        message="高级搜索演示"
        description="支持关键词搜索和多条件筛选，搜索结果会自动高亮显示"
        type="info"
        showIcon
        style={{ marginBottom: "16px" }}
      />

      {/* 高级搜索栏 */}
      <Card style={{ marginBottom: "16px" }}>
        <AdvancedSearch
          placeholder="搜索频道名称、ID 或描述..."
          searchFields={searchFields}
          operators={operators}
          initialKeyword={keyword}
          initialConditions={conditions}
          onSearch={handleSearch}
          onClear={handleClear}
          onConditionsChange={handleConditionsChange}
        />
      </Card>

      {/* 搜索结果统计 */}
      {(keyword || conditions.length > 0) && (
        <Alert
          message={`搜索到 ${filteredChannels.length} 个频道`}
          description={
            <Space size={4}>
              <span>关键词："{keyword}"</span>
              {conditions.map((condition, index) => (
                <Tag key={index} color="blue">
                  {searchFields.find((f) => f.value === condition.field)?.label}:{" "}
                  {condition.value}
                </Tag>
              ))}
            </Space>
          }
          type="success"
          showIcon
          style={{ marginBottom: "16px" }}
        />
      )}

      {/* 频道列表 */}
      <Card
        title="频道列表"
        extra={
          <Space>
            <Button
              icon={<ExportOutlined />}
              onClick={() => alert("导出功能开发中")}
            >
              导出
            </Button>
            <Button type="primary" icon={<PlusOutlined />}>
              新建频道
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={filteredChannels}
          loading={loading}
          rowKey="channel_id"
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个`,
          }}
        />
      </Card>
    </div>
  );
};

export default ChannelListWithSearch;
