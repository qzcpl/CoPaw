/**
 * 搜索结果高亮组件
 * v4.0 新增 - 支持关键词高亮显示
 */
import React from "react";
import { Tag } from "antd";

/**
 * 高亮组件属性
 */
export interface HighlightProps {
  /** 原始文本 */
  children: string;
  /** 要高亮的关键词 */
  keyword: string;
  /** 是否区分大小写 */
  caseSensitive?: boolean;
  /** 高亮样式类名 */
  highlightClassName?: string;
  /** 高亮样式 */
  highlightStyle?: React.CSSProperties;
}

/**
 * 搜索结果高亮组件
 */
export const Highlight: React.FC<HighlightProps> = ({
  children,
  keyword,
  caseSensitive = false,
  highlightClassName = "",
  highlightStyle = {
    backgroundColor: "#ffec3d",
    padding: "2px 4px",
    borderRadius: "2px",
    fontWeight: "bold",
  },
}) => {
  if (!keyword || !children) {
    return <>{children}</>;
  }

  const text = String(children);
  const flags = caseSensitive ? "g" : "gi";
  
  // 转义特殊字符
  const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  
  try {
    const regex = new RegExp(`(${escapedKeyword})`, flags);
    const parts = text.split(regex);

    return (
      <>
        {parts.map((part, index) => {
          if (part.toLowerCase() === keyword.toLowerCase() && part !== "") {
            return (
              <mark
                key={index}
                className={highlightClassName}
                style={highlightStyle}
              >
                {part}
              </mark>
            );
          }
          return <React.Fragment key={index}>{part}</React.Fragment>;
        })}
      </>
    );
  } catch (e) {
    // 正则表达式无效时返回原文本
    console.warn("高亮正则表达式无效:", e);
    return <>{children}</>;
  }
};

/**
 * 多关键词高亮组件
 */
export interface MultiHighlightProps {
  /** 原始文本 */
  children: string;
  /** 要高亮的关键词数组 */
  keywords: string[];
  /** 是否区分大小写 */
  caseSensitive?: boolean;
  /** 高亮样式类名 */
  highlightClassName?: string;
  /** 高亮样式 */
  highlightStyle?: React.CSSProperties;
}

/**
 * 多关键词高亮组件
 */
export const MultiHighlight: React.FC<MultiHighlightProps> = ({
  children,
  keywords,
  caseSensitive = false,
  highlightClassName = "",
  highlightStyle = {
    backgroundColor: "#ffec3d",
    padding: "2px 4px",
    borderRadius: "2px",
    fontWeight: "bold",
  },
}) => {
  if (!keywords || keywords.length === 0 || !children) {
    return <>{children}</>;
  }

  const text = String(children);
  const flags = caseSensitive ? "g" : "gi";
  
  // 过滤空关键词并转义特殊字符
  const validKeywords = keywords
    .filter((k) => k && k.trim())
    .map((k) => k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));

  if (validKeywords.length === 0) {
    return <>{children}</>;
  }

  try {
    // 创建匹配任意关键词的正则
    const regex = new RegExp(`(${validKeywords.join("|")})`, flags);
    const parts = text.split(regex);

    return (
      <>
        {parts.map((part, index) => {
          const matchedKeyword = validKeywords.find(
            (k) =>
              caseSensitive
                ? part === k
                : part.toLowerCase() === k.toLowerCase()
          );

          if (matchedKeyword && part !== "") {
            return (
              <mark
                key={index}
                className={highlightClassName}
                style={highlightStyle}
              >
                {part}
              </mark>
            );
          }
          return <React.Fragment key={index}>{part}</React.Fragment>;
        })}
      </>
    );
  } catch (e) {
    // 正则表达式无效时返回原文本
    console.warn("高亮正则表达式无效:", e);
    return <>{children}</>;
  }
};

/**
 * 高亮表格单元格组件
 */
export interface HighlightCellProps {
  /** 单元格文本 */
  text: string;
  /** 搜索关键词 */
  keyword: string;
  /** 是否区分大小写 */
  caseSensitive?: boolean;
  /** 最大显示长度（超过显示省略号） */
  maxLength?: number;
}

/**
 * 高亮表格单元格组件
 */
export const HighlightCell: React.FC<HighlightCellProps> = ({
  text,
  keyword,
  caseSensitive = false,
  maxLength = 100,
}) => {
  const displayText = text.length > maxLength 
    ? text.substring(0, maxLength) + "..." 
    : text;

  return <Highlight keyword={keyword} caseSensitive={caseSensitive}>
    {displayText}
  </Highlight>;
};

export default Highlight;
