/**
 * 批量操作组件
 * v4.0 新增 - 支持批量选择、批量删除、批量启用/禁用等
 */
import React, { useState, useMemo } from "react";
import {
  Table,
  Button,
  Space,
  Modal,
  message,
  Checkbox,
  Tooltip,
  Badge,
  Alert,
  type TableProps,
} from "antd";
import {
  DeleteOutlined,
  CheckSquareOutlined,
  UpSquareOutlined,
  ExportOutlined,
  ImportOutlined,
  ReloadOutlined,
} from "@ant-design/icons";

/**
 * 批量操作配置
 */
export interface BatchAction {
  /** 操作 ID */
  key: string;
  /** 操作名称 */
  label: string;
  /** 操作图标 */
  icon?: React.ReactNode;
  /** 操作类型 */
  type?: "primary" | "default" | "dashed" | "text" | "link";
  /** 是否是危险操作（用于显示红色） */
  danger?: boolean;
  /** 是否需要确认 */
  needConfirm?: boolean;
  /** 确认提示 */
  confirmTitle?: string;
  /** 确认内容 */
  confirmContent?: string;
  /** 操作回调 */
  onAction: (selectedRowKeys: React.Key[], selectedRows: any[]) => void | Promise<void>;
  /** 是否禁用 */
  disabled?: boolean;
  /** 禁用提示 */
  disabledReason?: string;
}

/**
 * 批量操作表格属性
 */
export interface BatchTableProps<T> extends Omit<TableProps<T>, "rowSelection"> {
  /** 批量操作列表 */
  batchActions?: BatchAction[];
  /** 是否显示批量操作栏 */
  showBatchActions?: boolean;
  /** 自定义批量操作栏 */
  customBatchActions?: React.ReactNode;
  /** 最大选择数量（0 为不限制） */
  maxSelection?: number;
  /** 选择变更回调 */
  onSelectionChange?: (selectedRowKeys: React.Key[], selectedRows: T[]) => void;
  /** 获取行唯一键 */
  getRowKey: (record: T) => string;
  /** 数据源 */
  dataSource: T[];
}

/**
 * 批量操作表格组件
 */
export function BatchTable<T extends Record<string, any>>({
  batchActions = [],
  showBatchActions = true,
  customBatchActions,
  maxSelection = 0,
  onSelectionChange,
  getRowKey,
  dataSource,
  ...tableProps
}: BatchTableProps<T>) {
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [selectedRows, setSelectedRows] = useState<T[]>([]);
  const [loading, setLoading] = useState(false);

  // 计算选中状态
  const selectionState = useMemo(() => {
    const total = dataSource.length;
    const selected = selectedRowKeys.length;
    const allSelected = selected > 0 && selected === total;
    const indeterminate = selected > 0 && selected < total;
    return { total, selected, allSelected, indeterminate };
  }, [dataSource.length, selectedRowKeys.length]);

  // 全选/取消全选
  const handleSelectAll = (checked: boolean) => {
    if (!checked) {
      // 取消全选
      setSelectedRowKeys([]);
      setSelectedRows([]);
      onSelectionChange?.([], []);
    } else {
      // 全选
      const keys = dataSource.map((record) => getRowKey(record));
      const rows = [...dataSource];
      
      if (maxSelection > 0 && keys.length > maxSelection) {
        message.warning(`最多只能选择 ${maxSelection} 项`);
        return;
      }
      
      setSelectedRowKeys(keys);
      setSelectedRows(rows);
      onSelectionChange?.(keys, rows);
    }
  };

  // 行选择变更
  const handleRowSelectionChange = (keys: React.Key[], rows: T[]) => {
    if (maxSelection > 0 && keys.length > maxSelection) {
      message.warning(`最多只能选择 ${maxSelection} 项`);
      return;
    }
    
    setSelectedRowKeys(keys);
    setSelectedRows(rows);
    onSelectionChange?.(keys, rows);
  };

  // 执行批量操作
  const handleBatchAction = async (action: BatchAction) => {
    if (selectedRowKeys.length === 0) {
      message.warning("请先选择要操作的项目");
      return;
    }

    // 确认对话框
    if (action.needConfirm) {
      const confirmed = await new Promise<boolean>((resolve) => {
        Modal.confirm({
          title: action.confirmTitle || "确认操作",
          content: action.confirmContent || `确定要对选中的 ${selectedRowKeys.length} 项执行"${action.label}"操作吗？`,
          okText: "确认",
          cancelText: "取消",
          okType: action.danger ? "danger" as const : "primary",
          onOk: () => resolve(true),
          onCancel: () => resolve(false),
        });
      });

      if (!confirmed) return;
    }

    // 执行操作
    setLoading(true);
    try {
      await action.onAction(selectedRowKeys, selectedRows);
      // 操作成功后清空选择
      setSelectedRowKeys([]);
      setSelectedRows([]);
      onSelectionChange?.([], []);
    } catch (error: any) {
      console.error("批量操作失败:", error);
      // 不清空选择，允许用户重试
    } finally {
      setLoading(false);
    }
  };

  // 行选择配置
  const rowSelection: TableProps<T>["rowSelection"] = {
    selectedRowKeys,
    onChange: handleRowSelectionChange,
    onSelectAll: (selected) => {
      handleSelectAll(selected);
    },
  };

  // 可用的批量操作
  const availableActions = batchActions.filter(
    (action) => !action.disabled || selectedRowKeys.length > 0
  );

  return (
    <div>
      {/* 批量操作栏 */}
      {showBatchActions && (selectedRowKeys.length > 0 || customBatchActions) && (
        <Alert
          message={
            <Space>
              <span>已选择 {selectionState.selected} 项</span>
              {maxSelection > 0 && (
                <span style={{ color: "#8c8c8c" }}>
                  （最多 {maxSelection} 项）
                </span>
              )}
            </Space>
          }
          type="info"
          showIcon
          style={{ marginBottom: "16px" }}
          action={
            <Space size={4}>
              {/* 自定义操作 */}
              {customBatchActions}

              {/* 批量操作按钮 */}
              {availableActions.map((action) => (
                <Tooltip key={action.key} title={action.disabledReason}>
                  <Button
                    type={action.type}
                    danger={!!action.danger}
                    icon={action.icon}
                    onClick={() => handleBatchAction(action)}
                    disabled={action.disabled || selectedRowKeys.length === 0}
                    loading={loading}
                    size="small"
                  >
                    {action.label}
                  </Button>
                </Tooltip>
              ))}

              {/* 清空选择 */}
              <Button
                icon={<ReloadOutlined />}
                onClick={() => {
                  setSelectedRowKeys([]);
                  setSelectedRows([]);
                  onSelectionChange?.([], []);
                }}
                size="small"
              >
                清空选择
              </Button>
            </Space>
          }
        />
      )}

      {/* 表格 */}
      <Table
        {...tableProps}
        dataSource={dataSource}
        rowSelection={rowSelection}
        rowKey={getRowKey}
        loading={loading || tableProps.loading}
      />
    </div>
  );
}

/**
 * 创建常用批量操作
 */
export const createBatchActions = <T extends Record<string, any>>(config: {
  /** 批量删除 */
  onDelete?: (ids: React.Key[], rows: T[]) => void | Promise<void>;
  /** 批量启用 */
  onEnable?: (ids: React.Key[], rows: T[]) => void | Promise<void>;
  /** 批量禁用 */
  onDisable?: (ids: React.Key[], rows: T[]) => void | Promise<void>;
  /** 批量导出 */
  onExport?: (ids: React.Key[], rows: T[]) => void | Promise<void>;
  /** 批量导入 */
  onImport?: () => void | Promise<void>;
  /** 删除确认标题 */
  deleteConfirmTitle?: string;
  /** 删除确认内容 */
  deleteConfirmContent?: string;
}): BatchAction[] => {
  const actions: BatchAction[] = [];

  // 批量删除
  if (config.onDelete) {
    actions.push({
      key: "batch-delete",
      label: "批量删除",
      icon: <DeleteOutlined />,
      danger: true,
      needConfirm: true,
      confirmTitle: config.deleteConfirmTitle || "确认删除",
      confirmContent:
        config.deleteConfirmContent || "删除后无法恢复，确定要删除选中的项目吗？",
      onAction: config.onDelete,
    });
  }

  // 批量启用
  if (config.onEnable) {
    actions.push({
      key: "batch-enable",
      label: "批量启用",
      icon: <CheckSquareOutlined />,
      type: "primary",
      onAction: config.onEnable,
    });
  }

  // 批量禁用
  if (config.onDisable) {
    actions.push({
      key: "batch-disable",
      label: "批量禁用",
      icon: <UpSquareOutlined />,
      type: "default",
      onAction: config.onDisable,
    });
  }

  // 批量导出
  if (config.onExport) {
    actions.push({
      key: "batch-export",
      label: "批量导出",
      icon: <ExportOutlined />,
      type: "default",
      onAction: config.onExport,
    });
  }

  // 批量导入
  if (config.onImport) {
    actions.push({
      key: "batch-import",
      label: "批量导入",
      icon: <ImportOutlined />,
      type: "default",
      onAction: () => config.onImport!(),
      needConfirm: false,
    });
  }

  return actions;
};

export default BatchTable;
