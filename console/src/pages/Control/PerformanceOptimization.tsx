/**
 * 性能优化演示页面
 * v4.0 新增 - 展示虚拟列表、防抖搜索、懒加载等优化效果
 */
import React, { useState, useEffect } from "react";
import {
  Card,
  Table,
  Space,
  Button,
  Alert,
  Descriptions,
  Divider,
  Tag,
  Typography,
  Input,
  List,
  Statistic,
  Row,
  Col,
} from "antd";
import {
  ThunderboltOutlined,
  DashboardOutlined,
  ExperimentOutlined,
} from "@ant-design/icons";
import {
  VirtualList,
  useDebounce,
  useThrottle,
  useLazyLoad,
  usePagination,
  useOptimizedSearch,
  LazyImage,
} from "@/utils/performance";

const { Title, Paragraph } = Typography;
const { Search } = Input;

/**
 * 性能优化演示页面
 */
export const PerformanceOptimization: React.FC = () => {
  // 生成大数据集
  const largeData = Array.from({ length: 10000 }, (_, i) => ({
    id: `item-${i}`,
    name: `项目 ${i + 1}`,
    description: `这是第 ${i + 1} 个项目的详细描述`,
    status: ["active", "inactive", "error"][Math.floor(Math.random() * 3)],
    value: Math.floor(Math.random() * 10000),
  }));

  // 虚拟列表示例
  const [virtualScrollCount, setVirtualScrollCount] = useState(0);

  // 防抖搜索示例
  const [debounceValue, setDebounceValue] = useState("");
  const [debounceInput, setDebounceInput] = useState("");
  
  const handleDebounceSearch = useDebounce((value: string) => {
    setDebounceValue(value);
  }, 500);

  // 节流示例
  const [throttleCount, setThrottleCount] = useState(0);
  const [scrollPosition, setScrollPosition] = useState(0);

  const handleScroll = useThrottle((e: React.UIEvent<HTMLDivElement>) => {
    setScrollPosition(e.currentTarget.scrollTop);
    setThrottleCount((prev) => prev + 1);
  }, 100);

  // 懒加载示例
  const { ref: lazyRef, isVisible: lazyVisible } = useLazyLoad();

  // 分页示例
  const {
    data: paginatedData,
    currentPage,
    totalPages,
    total,
    goToPage,
    nextPage,
    prevPage,
  } = usePagination(largeData, 20);

  // 优化搜索示例
  const {
    keyword: searchKeyword,
    setKeyword: setSearchKeyword,
    results: searchResults,
    clearSearch,
    total: searchTotal,
    filtered: searchFiltered,
  } = useOptimizedSearch({
    data: largeData,
    searchFn: (item, keyword) =>
      item.name.toLowerCase().includes(keyword.toLowerCase()) ||
      item.description.toLowerCase().includes(keyword.toLowerCase()),
    debounceMs: 300,
    cacheSize: 20,
  });

  // 状态标签
  const getStatusTag = (status: string) => {
    const config: Record<string, any> = {
      active: { color: "green", text: "活跃" },
      inactive: { color: "default", text: "未激活" },
      error: { color: "red", text: "错误" },
    };
    const { color, text } = config[status] || config.inactive;
    return <Tag color={color}>{text}</Tag>;
  };

  // 虚拟列表列定义
  const virtualColumns = [
    {
      title: "ID",
      dataIndex: "id",
      key: "id",
      width: 100,
    },
    {
      title: "名称",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      width: 100,
      render: getStatusTag,
    },
    {
      title: "数值",
      dataIndex: "value",
      key: "value",
      width: 100,
    },
  ];

  return (
    <div>
      <Alert
        message="性能优化演示"
        description="展示虚拟列表、防抖搜索、节流、懒加载等性能优化技术的实际效果"
        type="info"
        showIcon
        style={{ marginBottom: "16px" }}
        action={
          <Button
            type="primary"
            icon={<ThunderboltOutlined />}
            onClick={() => window.location.reload()}
          >
            重新测试
          </Button>
        }
      />

      {/* 性能指标概览 */}
      <Card style={{ marginBottom: "16px" }}>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="数据集大小"
              value={largeData.length}
              suffix="条"
              valueStyle={{ color: "#1890ff" }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="虚拟列表渲染项数"
              value={virtualScrollCount}
              suffix="项"
              valueStyle={{ color: "#52c41a" }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="节流触发次数"
              value={throttleCount}
              suffix="次"
              valueStyle={{ color: "#faad14" }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="懒加载状态"
              value={lazyVisible ? "已加载" : "未加载"}
              valueStyle={{ color: lazyVisible ? "#52c41a" : "#8c8c8c" }}
            />
          </Col>
        </Row>
      </Card>

      {/* 1. 虚拟列表示例 */}
      <Card
        title="1. 虚拟列表（Virtual List）"
        extra={<Tag color="blue">10,000 条数据</Tag>}
        style={{ marginBottom: "16px" }}
      >
        <Alert
          message="性能对比"
          description={
            <Space direction="vertical" style={{ width: "100%" }}>
              <span>❌ 传统渲染：渲染 10,000 个 DOM 节点，内存占用高，滚动卡顿</span>
              <span>✅ 虚拟列表：只渲染可见区域（约 20 项），内存占用低，滚动流畅</span>
            </Space>
          }
          type="success"
          showIcon
          style={{ marginBottom: "16px" }}
        />

        <div style={{ height: 400, border: "1px solid #d9d9d9" }}>
          <VirtualList
            data={largeData}
            itemHeight={54}
            containerHeight={400}
            bufferSize={5}
            renderItem={(item, index) => (
              <div
                style={{
                  padding: "12px 16px",
                  borderBottom: "1px solid #f0f0f0",
                  display: "flex",
                  alignItems: "center",
                  background: index % 2 === 0 ? "#fafafa" : "#fff",
                }}
              >
                <Space size="large" style={{ flex: 1 }}>
                  <span style={{ width: 100, color: "#8c8c8c" }}>{item.id}</span>
                  <span style={{ flex: 1 }}>{item.name}</span>
                  {getStatusTag(item.status)}
                  <span style={{ width: 100, textAlign: "right" }}>
                    {item.value}
                  </span>
                </Space>
              </div>
            )}
          />
        </div>

        <Paragraph style={{ marginTop: "16px" }}>
          <strong>使用说明：</strong>快速滚动列表，观察性能指标中的"虚拟列表渲染项数"，
          始终保持在约 20-30 项，而不是 10,000 项。
        </Paragraph>
      </Card>

      {/* 2. 防抖搜索示例 */}
      <Card
        title="2. 防抖搜索（Debounce Search）"
        extra={<Tag color="cyan">500ms 延迟</Tag>}
        style={{ marginBottom: "16px" }}
      >
        <Alert
          message="性能对比"
          description={
            <Space direction="vertical" style={{ width: "100%" }}>
              <span>❌ 实时搜索：每次输入都触发搜索，频繁计算，性能浪费</span>
              <span>✅ 防抖搜索：停止输入 500ms 后才触发搜索，减少不必要的计算</span>
            </Space>
          }
          type="success"
          showIcon
          style={{ marginBottom: "16px" }}
        />

        <Space direction="vertical" style={{ width: "100%" }}>
          <Search
            placeholder="输入项目名称搜索（防抖 500ms）"
            allowClear
            onSearch={handleDebounceSearch}
            onChange={(e) => {
              setDebounceInput(e.target.value);
              handleDebounceSearch(e.target.value);
            }}
            size="large"
          />

          <Descriptions bordered column={2}>
            <Descriptions.Item label="当前输入">
              {debounceInput || "（空）"}
            </Descriptions.Item>
            <Descriptions.Item label="搜索结果">
              {debounceValue || "（等待输入）"}
            </Descriptions.Item>
          </Descriptions>
        </Space>
      </Card>

      {/* 3. 节流示例 */}
      <Card
        title="3. 节流（Throttle）"
        extra={<Tag color="orange">100ms 间隔</Tag>}
        style={{ marginBottom: "16px" }}
      >
        <Alert
          message="性能对比"
          description={
            <Space direction="vertical" style={{ width: "100%" }}>
              <span>❌ 实时监听：scroll 事件每秒触发 60 次，性能开销大</span>
              <span>✅ 节流监听：每 100ms 最多触发一次，降低频率，提升性能</span>
            </Space>
          }
          type="success"
          showIcon
          style={{ marginBottom: "16px" }}
        />

        <div
          onScroll={handleScroll}
          style={{
            height: 200,
            overflow: "auto",
            border: "1px solid #d9d9d9",
            padding: "16px",
          }}
        >
          {Array.from({ length: 50 }, (_, i) => (
            <div key={i} style={{ padding: "8px 0", borderBottom: "1px solid #f0f0f0" }}>
              滚动内容行 {i + 1} - 滚动位置：{scrollPosition}px
            </div>
          ))}
        </div>

        <Descriptions bordered style={{ marginTop: "16px" }}>
          <Descriptions.Item label="节流触发次数">
            {throttleCount} 次
          </Descriptions.Item>
          <Descriptions.Item label="当前滚动位置">
            {scrollPosition}px
          </Descriptions.Item>
          <Descriptions.Item label="节流间隔">
            100ms
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* 4. 懒加载示例 */}
      <Card
        title="4. 懒加载（Lazy Load）"
        extra={<Tag color="purple">Intersection Observer</Tag>}
        style={{ marginBottom: "16px" }}
      >
        <Alert
          message="性能对比"
          description={
            <Space direction="vertical" style={{ width: "100%" }}>
              <span>❌ 立即加载：所有图片立即加载，浪费带宽和内存</span>
              <span>✅ 懒加载：只有进入视口才加载，节省资源</span>
            </Space>
          }
          type="success"
          showIcon
          style={{ marginBottom: "16px" }}
        />

        <div style={{ textAlign: "center" }}>
          <Paragraph>向下滚动到此区域触发加载：</Paragraph>
          <div style={{ height: 200 }} />
          
          <div ref={lazyRef} style={{ border: "2px dashed #1890ff", padding: "40px" }}>
            {lazyVisible ? (
              <LazyImage
                src="https://picsum.photos/400/200"
                alt="懒加载示例"
                width={400}
                height={200}
                placeholder="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
              />
            ) : (
              <div style={{ width: 400, height: 200, background: "#f5f5f5", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <span style={{ color: "#8c8c8c" }}>滚动到此区域加载图片...</span>
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* 5. 优化搜索示例 */}
      <Card
        title="5. 优化搜索（带缓存）"
        extra={<Tag color="green">缓存 20 条</Tag>}
        style={{ marginBottom: "16px" }}
      >
        <Alert
          message="性能对比"
          description={
            <Space direction="vertical" style={{ width: "100%" }}>
              <span>❌ 普通搜索：每次搜索都遍历全部数据，重复搜索浪费计算</span>
              <span>✅ 优化搜索：防抖 + 缓存，相同搜索词直接返回缓存结果</span>
            </Space>
          }
          type="success"
          showIcon
          style={{ marginBottom: "16px" }}
        />

        <Space direction="vertical" style={{ width: "100%" }}>
          <Search
            placeholder="搜索 10,000 条数据（带缓存）"
            allowClear
            onSearch={(value) => setSearchKeyword(value)}
            onChange={(e) => setSearchKeyword(e.target.value)}
            value={searchKeyword}
            size="large"
          />

          <Descriptions bordered column={3}>
            <Descriptions.Item label="总数据量">
              {searchTotal}
            </Descriptions.Item>
            <Descriptions.Item label="搜索结果">
              {searchFiltered}
            </Descriptions.Item>
            <Descriptions.Item label="缓存大小">
              最多 20 条
            </Descriptions.Item>
          </Descriptions>

          {searchKeyword && (
            <List
              dataSource={searchResults.slice(0, 10)}
              renderItem={(item) => (
                <List.Item>
                  <Space>
                    <Tag>{item.id}</Tag>
                    <span>{item.name}</span>
                    {getStatusTag(item.status)}
                  </Space>
                </List.Item>
              )}
              pagination={{
                pageSize: 10,
                showTotal: (total) => `共 ${total} 条结果`,
              }}
            />
          )}
        </Space>
      </Card>

      {/* 6. 分页示例 */}
      <Card
        title="6. 分页（Pagination）"
        extra={<Tag color="blue">每页 20 条</Tag>}
      >
        <Alert
          message="性能对比"
          description={
            <Space direction="vertical" style={{ width: "100%" }}>
              <span>❌ 全量加载：一次性加载 10,000 条数据，渲染慢，内存占用高</span>
              <span>✅ 分页加载：每次只加载 20 条，渲染快，内存占用低</span>
            </Space>
          }
          type="success"
          showIcon
          style={{ marginBottom: "16px" }}
        />

        <Table
          dataSource={paginatedData}
          columns={virtualColumns}
          rowKey="id"
          pagination={false}
          size="small"
        />

        <div style={{ marginTop: "16px", textAlign: "center" }}>
          <Space>
            <Button onClick={() => goToPage(1)} disabled={currentPage === 1}>
              首页
            </Button>
            <Button onClick={prevPage} disabled={currentPage === 1}>
              上一页
            </Button>
            <span>
              第 {currentPage} 页 / 共 {totalPages} 页（共 {total} 条）
            </span>
            <Button onClick={nextPage} disabled={currentPage === totalPages}>
              下一页
            </Button>
            <Button onClick={() => goToPage(totalPages)} disabled={currentPage === totalPages}>
              末页
            </Button>
          </Space>
        </div>
      </Card>

      {/* 总结 */}
      <Card
        title="性能优化总结"
        extra={<DashboardOutlined />}
        style={{ marginTop: "16px" }}
      >
        <Descriptions column={1} bordered>
          <Descriptions.Item label="虚拟列表">
            适用于大数据量列表/表格，只渲染可见区域，性能提升 10-100 倍
          </Descriptions.Item>
          <Descriptions.Item label="防抖">
            适用于搜索框、输入框等频繁触发场景，减少不必要的计算
          </Descriptions.Item>
          <Descriptions.Item label="节流">
            适用于 scroll、resize 等高频事件，控制触发频率
          </Descriptions.Item>
          <Descriptions.Item label="懒加载">
            适用于图片、长列表等，按需加载，节省带宽和内存
          </Descriptions.Item>
          <Descriptions.Item label="缓存">
            适用于重复搜索、重复计算场景，空间换时间
          </Descriptions.Item>
          <Descriptions.Item label="分页">
            适用于大数据集展示，分批加载，降低单次渲染压力
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};

export default PerformanceOptimization;
