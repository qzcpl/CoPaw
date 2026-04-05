/**
 * 监控中心页面组件
 * v4.0 新增 - 支持系统监控、告警管理、指标展示
 */
import React, { useState, useEffect } from "react";
import {
  Card,
  Table,
  Tag,
  Space,
  Button,
  Select,
  Statistic,
  Row,
  Col,
  Progress,
  Badge,
  Descriptions,
  Alert,
  Tabs,
} from "antd";
import {
  DashboardOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  BellOutlined,
  LineChartOutlined,
} from "@ant-design/icons";
import type {
  MonitorMetric,
  MonitorAlert,
} from "@/api/types";
import { monitorApi } from "@/api/modules/monitor";
import { useTenantStore } from "@/stores/tenantStore";

const { TabPane } = Tabs;

/**
 * 监控中心页面
 */
export const MonitorCenter: React.FC = () => {
  const [metrics, setMetrics] = useState<MonitorMetric[]>([]);
  const [alerts, setAlerts] = useState<MonitorAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState("1h");
  const { currentTenantId } = useTenantStore();

  // 加载监控数据
  useEffect(() => {
    loadMonitorData();
    const interval = setInterval(loadMonitorData, 30000); // 30 秒刷新
    return () => clearInterval(interval);
  }, [currentTenantId, timeRange]);

  const loadMonitorData = async () => {
    setLoading(true);
    try {
      const [metricsData, alertsData] = await Promise.all([
        monitorApi.getMetrics(currentTenantId),
        monitorApi.listAlerts(currentTenantId, "active"),
      ]);
      setMetrics(metricsData as MonitorMetric[]);
      setAlerts(alertsData as MonitorAlert[]);
    } catch (error) {
      console.error("加载监控数据失败:", error);
    } finally {
      setLoading(false);
    }
  };

  // 告警级别标签
  const getLevelTag = (level: string) => {
    const config: Record<string, any> = {
      info: { color: "blue", icon: <DashboardOutlined /> },
      warning: { color: "orange", icon: <WarningOutlined /> },
      error: { color: "red", icon: <CloseCircleOutlined /> },
      critical: { color: "red", icon: <WarningOutlined /> },
    };
    const { color, icon } = config[level] || config.info;
    return <Tag color={color} icon={icon}>{level.toUpperCase()}</Tag>;
  };

  // 告警状态标签
  const getStatusTag = (status: string) => {
    const config: Record<string, any> = {
      active: { color: "red", icon: <BellOutlined /> },
      acknowledged: { color: "orange", icon: <SyncOutlined /> },
      resolved: { color: "green", icon: <CheckCircleOutlined /> },
    };
    const { color, icon } = config[status] || config.active;
    return <Tag color={color} icon={icon}>{status}</Tag>;
  };

  // 组件健康状态
  const getComponentHealthBadge = (status: string) => {
    const config: Record<string, "success" | "warning" | "error" | "default"> = {
      healthy: "success",
      degraded: "warning",
      unhealthy: "error",
      unknown: "default",
    };
    return <Badge status={config[status] || "default"} text={status} />;
  };

  // 时间范围选项
  const timeRangeOptions = [
    { value: "1h", label: "最近 1 小时" },
    { value: "6h", label: "最近 6 小时" },
    { value: "24h", label: "最近 24 小时" },
    { value: "7d", label: "最近 7 天" },
  ];

  return (
    <div>
      {/* 系统健康概览 */}
      <Card title="系统健康" style={{ marginBottom: "16px" }}>
        <Row gutter={16}>
          <Col span={8}>
            <Statistic
              title="指标数量"
              value={metrics.length}
              prefix={<LineChartOutlined />}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="活跃告警"
              value={alerts.length}
              valueStyle={{ color: alerts.length > 0 ? "#ff4d4f" : "#52c41a" }}
              prefix={<BellOutlined />}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="时间范围"
              value={timeRange}
              suffix="/ 100"
            />
          </Col>
        </Row>
      </Card>

      {/* 告警信息 */}
      {alerts.length > 0 && (
        <Alert
          message={`当前有 ${alerts.length} 个活跃告警`}
          type="warning"
          showIcon
          style={{ marginBottom: "16px" }}
        />
      )}

      {/* 监控指标和告警 */}
      <Tabs defaultActiveKey="metrics">
        <TabPane tab="监控指标" key="metrics">
          <Card
            title="监控指标"
            extra={
              <Select
                value={timeRange}
                options={timeRangeOptions}
                onChange={setTimeRange}
                style={{ width: "150px" }}
              />
            }
          >
            <Table
              dataSource={metrics}
              rowKey="metric_name"
              loading={loading}
              columns={[
                {
                  title: "指标名称",
                  dataIndex: "metric_name",
                  key: "metric_name",
                  render: (text: string) => <strong>{text}</strong>,
                },
                {
                  title: "当前值",
                  dataIndex: "current_value",
                  key: "current_value",
                  render: (value: number, record: MonitorMetric) => (
                    <span>
                      {value} {record.unit}
                    </span>
                  ),
                },
                {
                  title: "平均值",
                  dataIndex: "avg_value",
                  key: "avg_value",
                  render: (value: number, record: MonitorMetric) => (
                    <span>
                      {value} {record.unit}
                    </span>
                  ),
                },
                {
                  title: "最大值",
                  dataIndex: "max_value",
                  key: "max_value",
                  render: (value: number, record: MonitorMetric) => (
                    <span>
                      {value} {record.unit}
                    </span>
                  ),
                },
                {
                  title: "最小值",
                  dataIndex: "min_value",
                  key: "min_value",
                  render: (value: number, record: MonitorMetric) => (
                    <span>
                      {value} {record.unit}
                    </span>
                  ),
                },
                {
                  title: "值",
                  dataIndex: "value",
                  key: "value",
                  render: (value: number, record: MonitorMetric) => (
                    <span>
                      {value} {record.unit}
                    </span>
                  ),
                },
                {
                  title: "类型",
                  dataIndex: "metric_type",
                  key: "metric_type",
                  render: (type: string) => <Tag>{type}</Tag>,
                },
                {
                  title: "时间",
                  dataIndex: "timestamp",
                  key: "timestamp",
                  render: (timestamp: string) => new Date(timestamp).toLocaleString("zh-CN"),
                },
              ]}
            />
          </Card>
        </TabPane>

        <TabPane tab="活跃告警" key="alerts">
          <Card title="活跃告警">
            <Table
              dataSource={alerts}
              rowKey="alert_id"
              loading={loading}
              columns={[
                {
                  title: "告警 ID",
                  dataIndex: "alert_id",
                  key: "alert_id",
                },
                {
                  title: "级别",
                  dataIndex: "level",
                  key: "level",
                  render: getLevelTag,
                },
                {
                  title: "状态",
                  dataIndex: "status",
                  key: "status",
                  render: getStatusTag,
                },
                {
                  title: "标题",
                  dataIndex: "title",
                  key: "title",
                  render: (text: string) => <strong>{text}</strong>,
                },
                {
                  title: "消息",
                  dataIndex: "message",
                  key: "message",
                  ellipsis: true,
                },
                {
                  title: "组件",
                  dataIndex: "component",
                  key: "component",
                },
                {
                  title: "创建时间",
                  dataIndex: "created_at",
                  key: "created_at",
                  render: (text: string) =>
                    new Date(text).toLocaleString("zh-CN"),
                },
              ]}
            />
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default MonitorCenter;
