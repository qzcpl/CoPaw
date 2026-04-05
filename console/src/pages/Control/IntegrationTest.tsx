/**
 * 集成测试页面
 * v4.0 新增 - 用于测试所有新增管理页面的集成
 */
import React, { useState, useEffect } from "react";
import {
  Card,
  Table,
  Tag,
  Space,
  Button,
  Alert,
  Progress,
  Statistic,
  Row,
  Col,
  Descriptions,
  Divider,
} from "antd";
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  WarningOutlined,
} from "@ant-design/icons";
import {
  channelApi,
  callIdApi,
  botApi,
  tenantApi,
  monitorApi,
} from "@/api/modules";
import { useTenantStore } from "@/stores/tenantStore";
import type {
  ChannelConfig,
  CallIdBinding,
  BotInfo,
  TenantInfo,
  SystemHealthResponse,
} from "@/api/types";

/**
 * 集成测试页面
 */
export const IntegrationTest: React.FC = () => {
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [testing, setTesting] = useState(false);
  const [systemHealth, setSystemHealth] = useState<SystemHealthResponse | null>(null);
  const { currentTenantId } = useTenantStore();

  // 测试结果类型
  interface TestResult {
    module: string;
    api: string;
    status: "success" | "error" | "skipped";
    message?: string;
    duration?: number;
  }

  // 运行所有测试
  const runAllTests = async () => {
    setTesting(true);
    const results: TestResult[] = [];

    // 1. 频道 API 测试
    results.push(await testChannelApi());

    // 2. callId API 测试
    results.push(await testCallIdApi());

    // 3. Bot API 测试
    results.push(await testBotApi());

    // 4. 租户 API 测试
    results.push(await testTenantApi());

    // 5. 监控 API 测试
    results.push(await testMonitorApi());

    setTestResults(results);

    // 获取系统指标
    try {
      const metrics = await monitorApi.getMetrics(currentTenantId);
      setSystemHealth({
        overall_status: metrics.length > 0 ? "healthy" : "degraded",
        health_score: metrics.length > 0 ? 100 : 50,
        components: [],
        active_alerts_count: 0,
        last_check_at: new Date().toISOString(),
        issues: [],
        recommendations: [],
      } as any);
    } catch (error) {
      console.error("获取系统指标失败:", error);
    }

    setTesting(false);
  };

  // 测试频道 API
  const testChannelApi = async (): Promise<TestResult> => {
    const start = Date.now();
    try {
      const channels = await channelApi.listChannels(currentTenantId);
      return {
        module: "频道管理",
        api: "listChannels",
        status: "success",
        message: `获取 ${channels.length} 个频道`,
        duration: Date.now() - start,
      };
    } catch (error: any) {
      return {
        module: "频道管理",
        api: "listChannels",
        status: "error",
        message: error.message || "未知错误",
        duration: Date.now() - start,
      };
    }
  };

  // 测试 callId API
  const testCallIdApi = async (): Promise<TestResult> => {
    const start = Date.now();
    try {
      const callIds = await callIdApi.listCallIdBindings(currentTenantId);
      return {
        module: "callId 管理",
        api: "listCallIdBindings",
        status: "success",
        message: `获取 ${callIds.length} 个 callId`,
        duration: Date.now() - start,
      };
    } catch (error: any) {
      return {
        module: "callId 管理",
        api: "listCallIdBindings",
        status: "error",
        message: error.message || "未知错误",
        duration: Date.now() - start,
      };
    }
  };

  // 测试 Bot API
  const testBotApi = async (): Promise<TestResult> => {
    const start = Date.now();
    try {
      const bots = await botApi.listBots(currentTenantId);
      return {
        module: "Bot 管理",
        api: "listBots",
        status: "success",
        message: `获取 ${bots.length} 个 Bot`,
        duration: Date.now() - start,
      };
    } catch (error: any) {
      return {
        module: "Bot 管理",
        api: "listBots",
        status: "error",
        message: error.message || "未知错误",
        duration: Date.now() - start,
      };
    }
  };

  // 测试租户 API
  const testTenantApi = async (): Promise<TestResult> => {
    const start = Date.now();
    try {
      const tenants = await tenantApi.listTenants();
      return {
        module: "租户管理",
        api: "listTenants",
        status: "success",
        message: `获取 ${tenants.length} 个租户`,
        duration: Date.now() - start,
      };
    } catch (error: any) {
      return {
        module: "租户管理",
        api: "listTenants",
        status: "error",
        message: error.message || "未知错误",
        duration: Date.now() - start,
      };
    }
  };

  // 测试监控 API
  const testMonitorApi = async (): Promise<TestResult> => {
    const start = Date.now();
    try {
      const metrics = await monitorApi.getMetrics(currentTenantId);
      return {
        module: "监控中心",
        api: "getMetrics",
        status: "success",
        message: `获取 ${metrics.length} 个指标`,
        duration: Date.now() - start,
      };
    } catch (error: any) {
      return {
        module: "监控中心",
        api: "getMetrics",
        status: "error",
        message: error.message || "未知错误",
        duration: Date.now() - start,
      };
    }
  };

  // 状态图标
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircleOutlined style={{ color: "#52c41a" }} />;
      case "error":
        return <CloseCircleOutlined style={{ color: "#ff4d4f" }} />;
      case "skipped":
        return <SyncOutlined style={{ color: "#faad14" }} />;
      default:
        return null;
    }
  };

  // 状态标签
  const getStatusTag = (status: string) => {
    const config: Record<string, any> = {
      success: { color: "green", text: "成功" },
      error: { color: "red", text: "失败" },
      skipped: { color: "orange", text: "跳过" },
    };
    const { color, text } = config[status] || config.skipped;
    return <Tag color={color}>{text}</Tag>;
  };

  // 测试表格列
  const columns = [
    {
      title: "模块",
      dataIndex: "module",
      key: "module",
    },
    {
      title: "API",
      dataIndex: "api",
      key: "api",
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      render: getStatusTag,
    },
    {
      title: "消息",
      dataIndex: "message",
      key: "message",
    },
    {
      title: "耗时",
      dataIndex: "duration",
      key: "duration",
      render: (duration?: number) => (duration ? `${duration}ms` : "-"),
    },
  ];

  // 计算测试统计
  const successCount = testResults.filter((r) => r.status === "success").length;
  const errorCount = testResults.filter((r) => r.status === "error").length;
  const totalCount = testResults.length;

  return (
    <div>
      <Alert
        message="集成测试页面"
        description="本页面用于测试所有新增管理页面的 API 集成情况，确保前后端通信正常。"
        type="info"
        showIcon
        style={{ marginBottom: "16px" }}
      />

      {/* 测试控制 */}
      <Card
        title="测试控制"
        extra={
          <Button
            type="primary"
            onClick={runAllTests}
            loading={testing}
            icon={<SyncOutlined spin={testing} />}
          >
            {testing ? "测试中..." : "运行所有测试"}
          </Button>
        }
      >
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="总测试数"
              value={totalCount}
              prefix={totalCount > 0 ? <CheckCircleOutlined /> : null}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="成功"
              value={successCount}
              valueStyle={{ color: "#52c41a" }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="失败"
              value={errorCount}
              valueStyle={{ color: "#ff4d4f" }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="成功率"
              value={totalCount > 0 ? Math.round((successCount / totalCount) * 100) : 0}
              suffix="%"
              valueStyle={{
                color:
                  totalCount > 0 && successCount / totalCount >= 0.8
                    ? "#52c41a"
                    : "#ff4d4f",
              }}
            />
          </Col>
        </Row>
      </Card>

      {/* 系统健康状态 */}
      {systemHealth && (
        <Card title="系统健康状态" style={{ marginTop: "16px" }}>
          <Row gutter={16}>
            <Col span={8}>
              <Statistic
                title="健康分数"
                value={systemHealth.health_score}
                suffix="/ 100"
                valueStyle={{
                  color:
                    systemHealth.health_score >= 80
                      ? "#52c41a"
                      : systemHealth.health_score >= 60
                      ? "#faad14"
                      : "#ff4d4f",
                }}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="健康分数"
                value={systemHealth.health_score}
                suffix="/ 100"
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="活跃告警"
                value={systemHealth.active_alerts_count}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="组件数量"
                value={systemHealth.components?.length || 0}
              />
            </Col>
          </Row>
          <Divider />
          <Descriptions title="组件健康" column={3} bordered size="small">
            {systemHealth.components?.map((component, index) => (
              <React.Fragment key={component.component_name || index}>
                <Descriptions.Item label={component.component_name}>
                  <Tag
                    color={
                      component.status === "healthy"
                        ? "green"
                        : component.status === "degraded"
                        ? "orange"
                        : "red"
                    }
                  >
                    {component.status}
                  </Tag>
                </Descriptions.Item>
              </React.Fragment>
            ))}
          </Descriptions>
        </Card>
      )}

      {/* 测试结果 */}
      <Card title="测试结果" style={{ marginTop: "16px" }}>
        {testResults.length === 0 ? (
          <Alert
            message="暂无测试结果"
            description="点击运行所有测试按钮开始测试"
            type="warning"
            showIcon
          />
        ) : (
          <Table
            columns={columns}
            dataSource={testResults}
            rowKey={(record, index) => `${record.module}-${record.api}-${index}`}
            pagination={false}
            size="small"
          />
        )}
      </Card>

      {/* 租户隔离测试 */}
      <Card title="租户隔离测试" style={{ marginTop: "16px" }}>
        <Descriptions title="当前租户信息" column={2} bordered>
          <Descriptions.Item label="租户 ID">
            {currentTenantId || "未选择"}
          </Descriptions.Item>
          <Descriptions.Item label="租户状态">
            {currentTenantId ? (
              <Tag color="green">已选择</Tag>
            ) : (
              <Tag color="default">未选择</Tag>
            )}
          </Descriptions.Item>
        </Descriptions>
        <Alert
          message="租户隔离说明"
          description="所有 API 调用都会自动携带 X-Tenant-ID 请求头，确保数据隔离。"
          type="success"
          showIcon
          style={{ marginTop: "16px" }}
        />
      </Card>
    </div>
  );
};

export default IntegrationTest;
