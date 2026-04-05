# 批量操作功能使用指南

**版本：** v1.0  
**日期：** 2026-04-01  
**组件位置：** `src/components/BatchTable.tsx`

---

## 功能概述

批量操作功能提供通用的表格批量处理能力，支持：

- ✅ 批量选择（单选/全选/反选）
- ✅ 批量删除（带确认对话框）
- ✅ 批量启用/禁用
- ✅ 批量导出（CSV/Excel/JSON）
- ✅ 批量导入
- ✅ 自定义批量操作
- ✅ 最大选择数量限制
- ✅ 选择状态提示

---

## 快速开始

### 1. 基础用法

```tsx
import BatchTable from "@/components/BatchTable";

function MyPage() {
  const data = [
    { id: "1", name: "项目 1" },
    { id: "2", name: "项目 2" },
  ];

  return (
    <BatchTable
      dataSource={data}
      getRowKey={(record) => record.id}
      columns={[
        { title: "ID", dataIndex: "id" },
        { title: "名称", dataIndex: "name" },
      ]}
    />
  );
}
```

### 2. 添加批量操作

```tsx
import BatchTable, { createBatchActions } from "@/components/BatchTable";

function MyPage() {
  // 创建批量操作
  const batchActions = createBatchActions({
    onDelete: async (ids, rows) => {
      // 执行批量删除
      await api.batchDelete(ids);
      message.success("删除成功");
    },
    onEnable: async (ids, rows) => {
      // 执行批量启用
      await api.batchEnable(ids);
    },
    onDisable: async (ids, rows) => {
      // 执行批量禁用
      await api.batchDisable(ids);
    },
  });

  return (
    <BatchTable
      dataSource={data}
      getRowKey={(record) => record.id}
      batchActions={batchActions}
      columns={columns}
    />
  );
}
```

### 3. 自定义批量操作

```tsx
const batchActions: BatchAction[] = [
  {
    key: "custom-action",
    label: "自定义操作",
    icon: <CustomIcon />,
    type: "primary",
    needConfirm: true,
    confirmTitle: "确认操作",
    confirmContent: "确定要执行此操作吗？",
    onAction: async (ids, rows) => {
      // 自定义逻辑
    },
  },
];
```

---

## API 文档

### BatchTable 组件

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `dataSource` | `T[]` | - | 数据源（必填） |
| `getRowKey` | `(record: T) => string` | - | 获取行唯一键（必填） |
| `batchActions` | `BatchAction[]` | `[]` | 批量操作列表 |
| `showBatchActions` | `boolean` | `true` | 是否显示批量操作栏 |
| `customBatchActions` | `ReactNode` | - | 自定义批量操作栏 |
| `maxSelection` | `number` | `0` | 最大选择数量（0 为不限制） |
| `onSelectionChange` | `(keys, rows) => void` | - | 选择变更回调 |
| `columns` | `ColumnsType<T>` | - | 表格列定义 |
| 其他 Table 属性 | - | - | 支持所有 Ant Design Table 属性 |

### BatchAction 配置

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `key` | `string` | - | 操作唯一标识（必填） |
| `label` | `string` | - | 操作名称（必填） |
| `onAction` | `(ids, rows) => void` | - | 操作回调（必填） |
| `icon` | `ReactNode` | - | 操作图标 |
| `type` | `ButtonProps["type"]` | `"default"` | 按钮类型 |
| `needConfirm` | `boolean` | `false` | 是否需要确认 |
| `confirmTitle` | `string` | `"确认操作"` | 确认对话框标题 |
| `confirmContent` | `string` | - | 确认对话框内容 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `disabledReason` | `string` | - | 禁用提示 |

### createBatchActions 工具

```tsx
const actions = createBatchActions<MyDataType>({
  onDelete: handleDelete,      // 批量删除
  onEnable: handleEnable,      // 批量启用
  onDisable: handleDisable,    // 批量禁用
  onExport: handleExport,      // 批量导出
  onImport: handleImport,      // 批量导入
  deleteConfirmTitle: "确认删除",
  deleteConfirmContent: "确定要删除吗？",
});
```

---

## 使用示例

### 示例 1：频道管理批量操作

```tsx
import BatchTable, { createBatchActions } from "@/components/BatchTable";
import { channelApi } from "@/api/modules/channel";
import { exportData } from "@/utils/export";

function ChannelManagement() {
  const [channels, setChannels] = useState<ChannelConfig[]>([]);

  const batchActions = createBatchActions<ChannelConfig>({
    // 批量删除
    onDelete: async (ids, rows) => {
      await Promise.all(
        rows.map((channel) =>
          channelApi.deleteChannel(channel.channel_id)
        )
      );
      message.success(`删除 ${ids.length} 个频道`);
      loadChannels();
    },

    // 批量启用
    onEnable: async (ids, rows) => {
      await channelApi.batchEnable(ids as string[]);
      message.success(`启用 ${ids.length} 个频道`);
      loadChannels();
    },

    // 批量禁用
    onDisable: async (ids, rows) => {
      await channelApi.batchDisable(ids as string[]);
      message.success(`禁用 ${ids.length} 个频道`);
      loadChannels();
    },

    // 批量导出
    onExport: async (ids, rows) => {
      await exportData({
        filename: `channels_${Date.now()}`,
        format: "excel",
        data: rows,
        columns: [
          { title: "ID", dataIndex: "channel_id" },
          { title: "名称", dataIndex: "channel_name" },
          { title: "状态", dataIndex: "status" },
        ],
      });
    },
  });

  return (
    <BatchTable
      dataSource={channels}
      getRowKey={(r) => r.channel_id}
      batchActions={batchActions}
      maxSelection={100}
      columns={columns}
    />
  );
}
```

### 示例 2：自定义批量操作

```tsx
const batchActions: BatchAction[] = [
  {
    key: "batch-audit",
    label: "批量审核",
    icon: <CheckOutlined />,
    type: "primary",
    needConfirm: true,
    confirmTitle: "批量审核",
    confirmContent: "确定要通过选中的项目审核吗？",
    onAction: async (ids, rows) => {
      await api.batchAudit(ids as string[], { status: "approved" });
    },
  },
  {
    key: "batch-reject",
    label: "批量拒绝",
    icon: <CloseOutlined />,
    type: "danger",
    needConfirm: true,
    onAction: async (ids, rows) => {
      await api.batchAudit(ids as string[], { status: "rejected" });
    },
  },
];
```

### 示例 3：带选择限制

```tsx
<BatchTable
  dataSource={data}
  getRowKey={(r) => r.id}
  batchActions={batchActions}
  maxSelection={10}  // 最多选择 10 项
  onSelectionChange={(keys, rows) => {
    console.log("已选择:", keys.length, "项");
  }}
  columns={columns}
/>
```

---

## 最佳实践

### 1. 性能优化

- 大数据集使用分页
- 设置合理的 `maxSelection` 限制
- 批量操作使用 `Promise.allSettled` 处理部分失败

### 2. 用户体验

- 危险操作（删除）必须二次确认
- 操作后给出明确反馈（成功/失败数量）
- 提供"清空选择"按钮
- 显示当前选择数量

### 3. 错误处理

```tsx
const handleBatchDelete = async (ids, rows) => {
  const results = await Promise.allSettled(
    rows.map((item) => api.delete(item.id))
  );

  const success = results.filter((r) => r.status === "fulfilled").length;
  const failed = results.filter((r) => r.status === "rejected").length;

  if (failed === 0) {
    message.success(`成功删除 ${success} 项`);
  } else {
    message.warning(`删除完成：成功 ${success} 项，失败 ${failed} 项`);
  }

  // 刷新列表
  loadData();
};
```

### 4. 与搜索/筛选配合

```tsx
// 搜索后，批量操作只针对当前页或所有匹配结果
const [searchMode, setSearchMode] = useState<"current" | "all">("current");

const handleBatchDelete = async (ids, rows) => {
  if (searchMode === "all") {
    // 删除所有匹配结果
    await api.batchDeleteByFilter(searchFilters);
  } else {
    // 只删除当前选择的
    await api.batchDelete(ids);
  }
};
```

---

## 注意事项

1. **唯一键**：`getRowKey` 必须返回唯一标识符
2. **异步操作**：`onAction` 支持返回 Promise
3. **确认对话框**：危险操作务必设置 `needConfirm: true`
4. **选择清空**：操作成功后会自动清空选择状态
5. **禁用状态**：可通过 `disabled` 动态控制操作可用性

---

## 相关文件

- **组件**：`src/components/BatchTable.tsx`
- **导出工具**：`src/utils/export.ts`
- **示例页面**：`src/pages/Control/ChannelListWithBatch.tsx`

---

**更新日期：** 2026-04-01  
**维护者：** CoPaw 前端团队
