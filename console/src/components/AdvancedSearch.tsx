/**
 * 高级搜索组件
 * v4.0 新增 - 支持多条件筛选、搜索历史、结果高亮
 */
import React, { useState, useEffect, useRef } from "react";
import {
  Input,
  Select,
  Button,
  Space,
  Tag,
  Dropdown,
  Menu,
  Divider,
  Tooltip,
  Badge,
} from "antd";
import {
  SearchOutlined,
  HistoryOutlined,
  ClearOutlined,
  FilterOutlined,
  DownOutlined,
  CloseCircleOutlined,
} from "@ant-design/icons";

const { Option } = Select;
const { Search } = Input;

/**
 * 搜索条件接口
 */
export interface SearchCondition {
  field: string;
  operator: "contains" | "equals" | "startsWith" | "endsWith" | "gt" | "lt" | "between";
  value: string | number | [number, number];
}

/**
 * 搜索历史项
 */
export interface SearchHistoryItem {
  id: string;
  keyword: string;
  conditions: SearchCondition[];
  timestamp: number;
  resultCount?: number;
}

/**
 * 高级搜索组件属性
 */
export interface AdvancedSearchProps {
  /** 搜索占位符 */
  placeholder?: string;
  /** 是否显示搜索历史 */
  showHistory?: boolean;
  /** 是否显示高级筛选 */
  showFilter?: boolean;
  /** 搜索字段选项 */
  searchFields?: { label: string; value: string }[];
  /** 运算符选项 */
  operators?: { label: string; value: SearchCondition["operator"] }[];
  /** 初始搜索词 */
  initialKeyword?: string;
  /** 初始条件 */
  initialConditions?: SearchCondition[];
  /** 搜索历史最大数量 */
  maxHistory?: number;
  /** 搜索回调 */
  onSearch?: (keyword: string, conditions: SearchCondition[]) => void;
  /** 清空回调 */
  onClear?: () => void;
  /** 条件变更回调 */
  onConditionsChange?: (conditions: SearchCondition[]) => void;
}

/**
 * 高级搜索组件
 */
export const AdvancedSearch: React.FC<AdvancedSearchProps> = ({
  placeholder = "搜索...",
  showHistory = true,
  showFilter = true,
  searchFields = [
    { label: "名称", value: "name" },
    { label: "ID", value: "id" },
    { label: "描述", value: "description" },
  ],
  operators = [
    { label: "包含", value: "contains" },
    { label: "等于", value: "equals" },
    { label: "开始于", value: "startsWith" },
    { label: "结束于", value: "endsWith" },
  ],
  initialKeyword = "",
  initialConditions = [],
  maxHistory = 10,
  onSearch,
  onClear,
  onConditionsChange,
}) => {
  const [keyword, setKeyword] = useState(initialKeyword);
  const [conditions, setConditions] = useState<SearchCondition[]>(initialConditions);
  const [history, setHistory] = useState<SearchHistoryItem[]>([]);
  const [historyVisible, setHistoryVisible] = useState(false);
  const [filterVisible, setFilterVisible] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  // 加载搜索历史
  useEffect(() => {
    const savedHistory = localStorage.getItem("search_history");
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory));
      } catch (e) {
        console.error("加载搜索历史失败:", e);
      }
    }
  }, []);

  // 点击外部关闭历史下拉
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setHistoryVisible(false);
        setFilterVisible(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // 执行搜索
  const handleSearch = (value?: string) => {
    const searchKeyword = value ?? keyword;
    onSearch?.(searchKeyword, conditions);

    // 添加到搜索历史
    if (showHistory && searchKeyword.trim()) {
      addToHistory(searchKeyword, conditions);
    }
  };

  // 添加到搜索历史
  const addToHistory = (searchKeyword: string, searchConditions: SearchCondition[]) => {
    setHistory((prev) => {
      // 移除重复项
      const filtered = prev.filter(
        (item) => item.keyword !== searchKeyword
      );
      // 添加新项
      const newItem: SearchHistoryItem = {
        id: Date.now().toString(),
        keyword: searchKeyword,
        conditions: searchConditions,
        timestamp: Date.now(),
      };
      const updated = [newItem, ...filtered].slice(0, maxHistory);
      // 保存到 localStorage
      localStorage.setItem("search_history", JSON.stringify(updated));
      return updated;
    });
  };

  // 清空搜索
  const handleClear = () => {
    setKeyword("");
    setConditions([]);
    onClear?.();
    onSearch?.("", []);
  };

  // 使用历史搜索
  const useHistoryItem = (item: SearchHistoryItem) => {
    setKeyword(item.keyword);
    setConditions(item.conditions);
    setHistoryVisible(false);
    onSearch?.(item.keyword, item.conditions);
  };

  // 删除历史项
  const deleteHistoryItem = (id: string, event: React.MouseEvent) => {
    event.stopPropagation();
    setHistory((prev) => {
      const updated = prev.filter((item) => item.id !== id);
      localStorage.setItem("search_history", JSON.stringify(updated));
      return updated;
    });
  };

  // 清空历史
  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem("search_history");
  };

  // 添加搜索条件
  const addCondition = () => {
    const newCondition: SearchCondition = {
      field: searchFields[0]?.value || "name",
      operator: "contains",
      value: "",
    };
    const updated = [...conditions, newCondition];
    setConditions(updated);
    onConditionsChange?.(updated);
  };

  // 更新搜索条件
  const updateCondition = (
    index: number,
    updates: Partial<SearchCondition>
  ) => {
    const updated = conditions.map((cond, i) =>
      i === index ? { ...cond, ...updates } : cond
    );
    setConditions(updated);
    onConditionsChange?.(updated);
  };

  // 删除搜索条件
  const removeCondition = (index: number) => {
    const updated = conditions.filter((_, i) => i !== index);
    setConditions(updated);
    onConditionsChange?.(updated);
  };

  // 搜索历史菜单
  const historyMenuItems = history.length === 0
    ? [{ key: 'empty', label: '暂无搜索历史', disabled: true }]
    : history.map((item) => ({
        key: item.id,
        label: (
          <Space>
            <HistoryOutlined />
            <span>{item.keyword}</span>
            {item.conditions.length > 0 && (
              <Tag color="blue">{item.conditions.length}个条件</Tag>
            )}
          </Space>
        ),
        onClick: () => useHistoryItem(item),
        icon: (
          <CloseCircleOutlined
            onClick={(e) => deleteHistoryItem(item.id, e)}
            style={{
              color: "#8c8c8c",
              cursor: "pointer",
            }}
          />
        ),
      }));

  // 添加清空历史项
  const historyMenuItemsWithClear = [
    ...historyMenuItems,
    { type: 'divider' as const },
    {
      key: 'clear',
      label: (
        <Space>
          <ClearOutlined />
          <span>清空历史</span>
        </Space>
      ),
      onClick: clearHistory,
    },
  ];

  const historyMenu = {
    items: historyMenuItemsWithClear,
    style: { maxHeight: "400px", overflowY: "auto" as const },
  } as const;

  // 高级筛选菜单
  const filterMenu = {
    items: [{
      key: 'filter-content',
      label: (
        <div style={{ width: "500px", padding: "16px" }}>
          <div style={{ marginBottom: "12px" }}>
            <strong>搜索条件</strong>
          </div>
          {conditions.map((condition, index) => (
            <Space key={index} style={{ marginBottom: "8px", width: "100%" }}>
              <Select
                value={condition.field}
                onChange={(value) => updateCondition(index, { field: value })}
                style={{ width: "120px" }}
                size="small"
              >
                {searchFields.map((field) => (
                  <Option key={field.value} value={field.value}>
                    {field.label}
                  </Option>
                ))}
              </Select>
              <Select
                value={condition.operator}
                onChange={(value) => updateCondition(index, { operator: value })}
                style={{ width: "100px" }}
                size="small"
              >
                {operators.map((op) => (
                  <Option key={op.value} value={op.value}>
                    {op.label}
                  </Option>
                ))}
              </Select>
              <Input
                value={condition.value as string}
                onChange={(e) => updateCondition(index, { value: e.target.value })}
                placeholder="输入值"
                style={{ flex: 1 }}
                size="small"
              />
              <Button
                type="text"
                danger
                icon={<CloseCircleOutlined />}
                onClick={() => removeCondition(index)}
                size="small"
              />
            </Space>
          ))}
          <Divider style={{ margin: "8px 0" }} />
          <Space>
            <Button type="primary" size="small" onClick={addCondition}>
              添加条件
            </Button>
            <Button
              size="small"
              onClick={() => {
                setConditions([]);
                onConditionsChange?.([]);
              }}
            >
              清空条件
            </Button>
          </Space>
        </div>
      ),
    }],
  };

  return (
    <div ref={searchRef} style={{ display: "inline-block", width: "100%" }}>
      <Space.Compact style={{ width: "100%" }}>
        {/* 搜索历史下拉 */}
        {showHistory && (
          <Dropdown
            menu={historyMenu}
            trigger={["click"]}
            open={historyVisible}
            onOpenChange={setHistoryVisible}
          >
            <Button icon={<HistoryOutlined />} />
          </Dropdown>
        )}

        {/* 搜索输入框 */}
        <Search
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onSearch={handleSearch}
          placeholder={placeholder}
          allowClear
          style={{ flex: 1 }}
          onPressEnter={() => handleSearch()}
        />

        {/* 高级筛选下拉 */}
        {showFilter && (
          <Tooltip title="高级筛选">
            <Dropdown
              menu={filterMenu}
              trigger={["click"]}
              open={filterVisible}
              onOpenChange={setFilterVisible}
            >
              <Badge count={conditions.length} showZero>
                <Button icon={<FilterOutlined />} />
              </Badge>
            </Dropdown>
          </Tooltip>
        )}

        {/* 搜索按钮 */}
        <Button
          type="primary"
          icon={<SearchOutlined />}
          onClick={() => handleSearch()}
        >
          搜索
        </Button>

        {/* 清空按钮 */}
        {(keyword || conditions.length > 0) && (
          <Button
            icon={<ClearOutlined />}
            onClick={handleClear}
          >
            清空
          </Button>
        )}
      </Space.Compact>

      {/* 搜索条件标签 */}
      {conditions.length > 0 && (
        <div style={{ marginTop: "8px" }}>
          <Space size={4} wrap>
            {conditions.map((condition, index) => (
              <Tag
                key={index}
                closable
                onClose={() => removeCondition(index)}
                color="blue"
              >
                {searchFields.find((f) => f.value === condition.field)?.label}:{" "}
                {operators.find((o) => o.value === condition.operator)?.label}{" "}
                "{String(condition.value)}"
              </Tag>
            ))}
          </Space>
        </div>
      )}
    </div>
  );
};

export default AdvancedSearch;
