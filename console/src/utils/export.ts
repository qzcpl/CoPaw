/**
 * 数据导出工具
 * v4.0 新增 - 支持 CSV/Excel/JSON 格式导出
 */
import { message } from "antd";

/**
 * 导出数据选项
 */
export interface ExportOptions {
  /** 文件名（不含扩展名） */
  filename: string;
  /** 导出格式 */
  format: "csv" | "excel" | "json";
  /** 数据 */
  data: any[];
  /** 列定义 */
  columns: { title: string; dataIndex: string; render?: (value: any, record: any) => string }[];
  /** 编码（仅 CSV） */
  encoding?: string;
}

/**
 * 导出为 CSV 文件
 */
export const exportToCSV = (options: ExportOptions) => {
  const { filename, data, columns, encoding = "utf-8" } = options;

  try {
    // 生成表头
    const headers = columns.map((col) => col.title).join(",");

    // 生成数据行
    const rows = data.map((record) => {
      return columns
        .map((col) => {
          let value = record[col.dataIndex];
          // 处理 render 函数
          if (col.render) {
            value = col.render(value, record);
          }
          // 处理特殊字符
          if (typeof value === "string") {
            value = value.replace(/"/g, '""');
            if (value.includes(",") || value.includes("\n") || value.includes('"')) {
              value = `"${value}"`;
            }
          }
          return value;
        })
        .join(",");
    });

    // 组合 CSV 内容
    const csvContent = [headers, ...rows].join("\n");

    // 添加 BOM（防止中文乱码）
    const BOM = "\uFEFF";
    const blob = new Blob([BOM + csvContent], { type: `text/csv;charset=${encoding};` });

    // 下载文件
    downloadBlob(blob, `${filename}.csv`);

    message.success(`导出成功：${filename}.csv`);
  } catch (error) {
    console.error("CSV 导出失败:", error);
    message.error("导出失败");
  }
};

/**
 * 导出为 Excel 文件（使用 XLSX 库）
 */
export const exportToExcel = async (options: ExportOptions) => {
  const { filename, data, columns } = options;

  try {
    // 动态导入 xlsx 库
    const XLSX = await import("xlsx");

    // 准备数据
    const exportData = data.map((record) => {
      const row: Record<string, any> = {};
      columns.forEach((col) => {
        let value = record[col.dataIndex];
        if (col.render) {
          value = col.render(value, record);
        }
        row[col.title] = value;
      });
      return row;
    });

    // 创建工作表
    const worksheet = XLSX.utils.json_to_sheet(exportData);

    // 设置列宽
    const colWidths = columns.map((col) => ({
      wch: Math.max(col.title.length, 20),
    }));
    worksheet["!cols"] = colWidths;

    // 创建工作簿
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Sheet1");

    // 下载文件
    XLSX.writeFile(workbook, `${filename}.xlsx`);

    message.success(`导出成功：${filename}.xlsx`);
  } catch (error) {
    console.error("Excel 导出失败:", error);
    if (error instanceof Error && error.message.includes("Cannot find module")) {
      message.error("请先安装 xlsx 库：npm install xlsx");
    } else {
      message.error("导出失败");
    }
  }
};

/**
 * 导出为 JSON 文件
 */
export const exportToJSON = (options: ExportOptions) => {
  const { filename, data } = options;

  try {
    // 生成 JSON 内容
    const jsonContent = JSON.stringify(data, null, 2);

    // 创建 Blob
    const blob = new Blob([jsonContent], { type: "application/json" });

    // 下载文件
    downloadBlob(blob, `${filename}.json`);

    message.success(`导出成功：${filename}.json`);
  } catch (error) {
    console.error("JSON 导出失败:", error);
    message.error("导出失败");
  }
};

/**
 * 通用导出函数
 */
export const exportData = async (options: ExportOptions) => {
  const { format } = options;

  switch (format) {
    case "csv":
      return exportToCSV(options);
    case "excel":
      return exportToExcel(options);
    case "json":
      return exportToJSON(options);
    default:
      message.error(`不支持的导出格式：${format}`);
  }
};

/**
 * 下载 Blob 文件
 */
const downloadBlob = (blob: Blob, filename: string) => {
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);

  link.href = url;
  link.download = filename;
  link.style.display = "none";

  document.body.appendChild(link);
  link.click();

  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * 导出按钮组件属性
 */
export interface ExportButtonProps {
  /** 文件名 */
  filename: string;
  /** 导出格式 */
  format?: "csv" | "excel" | "json";
  /** 数据 */
  data: any[];
  /** 列定义 */
  columns: { title: string; dataIndex: string; render?: (value: any, record: any) => string }[];
  /** 按钮文本 */
  buttonText?: string;
  /** 按钮类型 */
  buttonType?: "primary" | "default" | "dashed" | "text" | "link";
  /** 导出前回调 */
  beforeExport?: () => Promise<boolean> | boolean;
  /** 导出后回调 */
  afterExport?: () => void;
}

/**
 * 创建导出按钮（需要在 React 组件中使用）
 */
export const createExportHandler = (props: ExportButtonProps) => {
  const {
    filename,
    format = "csv",
    data,
    columns,
    beforeExport,
    afterExport,
  } = props;

  return async () => {
    // 导出前检查
    if (beforeExport) {
      const shouldContinue = await beforeExport();
      if (!shouldContinue) {
        return;
      }
    }

    // 检查数据
    if (!data || data.length === 0) {
      message.warning("没有数据可导出");
      return;
    }

    // 执行导出
    await exportData({
      filename,
      format,
      data,
      columns,
    });

    // 导出后回调
    if (afterExport) {
      afterExport();
    }
  };
};

export default {
  exportToCSV,
  exportToExcel,
  exportToJSON,
  exportData,
  createExportHandler,
};
