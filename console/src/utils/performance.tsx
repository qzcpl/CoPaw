/**
 * 性能优化工具集
 * v4.0 新增 - 防抖、节流、懒加载、虚拟列表等性能优化组件
 */
import React, { useState, useEffect, useRef, useCallback, useMemo } from "react";

/**
 * 防抖 Hook
 * @param fn 要执行的函数
 * @param delay 延迟时间（毫秒）
 */
export function useDebounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): T {
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const debouncedFn = useCallback(
    (...args: Parameters<T>) => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
      timerRef.current = setTimeout(() => {
        fn(...args);
      }, delay);
    },
    [fn, delay]
  );

  // 组件卸载时清理定时器
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  return debouncedFn as T;
}

/**
 * 节流 Hook
 * @param fn 要执行的函数
 * @param interval 间隔时间（毫秒）
 */
export function useThrottle<T extends (...args: any[]) => any>(
  fn: T,
  interval: number
): T {
  const lastRunRef = useRef<number>(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const throttledFn = useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now();
      const timeSinceLastRun = now - lastRunRef.current;

      if (timeSinceLastRun >= interval) {
        lastRunRef.current = now;
        fn(...args);
      } else {
        if (timerRef.current) {
          clearTimeout(timerRef.current);
        }
        timerRef.current = setTimeout(() => {
          lastRunRef.current = Date.now();
          fn(...args);
        }, interval - timeSinceLastRun);
      }
    },
    [fn, interval]
  );

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  return throttledFn as T;
}

/**
 * 懒加载 Hook（Intersection Observer）
 * @param options IntersectionObserver 选项
 */
export function useLazyLoad(
  options: IntersectionObserverInit = { threshold: 0.1 }
): { ref: React.RefObject<HTMLDivElement>; isVisible: boolean } {
  const ref = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true);
        observer.unobserve(element);
      }
    }, options);

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [options]);

  return { ref, isVisible };
}

/**
 * 虚拟列表组件（大数据量优化）
 */
interface VirtualListProps<T> {
  /** 数据源 */
  data: T[];
  /** 每项高度（固定高度） */
  itemHeight: number;
  /** 容器高度 */
  containerHeight: number;
  /** 渲染每项的函数 */
  renderItem: (item: T, index: number) => React.ReactNode;
  /** 每项的 key */
  getItemKey?: (item: T, index: number) => string;
  /** 额外缓冲项数 */
  bufferSize?: number;
  /** 自定义类名 */
  className?: string;
  /** 自定义样式 */
  style?: React.CSSProperties;
}

export function VirtualList<T>({
  data,
  itemHeight,
  containerHeight,
  renderItem,
  getItemKey,
  bufferSize = 5,
  className,
  style,
}: VirtualListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  // 计算可见区域
  const visibleCount = Math.ceil(containerHeight / itemHeight);
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - bufferSize);
  const endIndex = Math.min(
    data.length,
    startIndex + visibleCount + bufferSize * 2
  );

  // 可见数据
  const visibleData = useMemo(
    () => data.slice(startIndex, endIndex),
    [data, startIndex, endIndex]
  );

  // 总高度
  const totalHeight = data.length * itemHeight;

  // 偏移量
  const offsetY = startIndex * itemHeight;

  // 滚动处理
  const handleScroll = useThrottle(
    (e: React.UIEvent<HTMLDivElement>) => {
      setScrollTop(e.currentTarget.scrollTop);
    },
    16 // 约 60fps
  );

  return (
    <div
      ref={containerRef}
      className={className}
      style={{
        height: containerHeight,
        overflow: "auto",
        position: "relative",
        ...style,
      }}
      onScroll={handleScroll}
    >
      {/* 占位元素，保持滚动条高度 */}
      <div style={{ height: totalHeight, position: "relative" }}>
        {/* 可见区域 */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            transform: `translateY(${offsetY}px)`,
          }}
        >
          {visibleData.map((item, index) => (
            <div
              key={getItemKey?.(item, startIndex + index) || String(startIndex + index)}
              style={{ height: itemHeight }}
            >
              {renderItem(item, startIndex + index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * 图片懒加载组件
 */
interface LazyImageProps {
  /** 图片 URL */
  src: string;
  /** 替代文本 */
  alt?: string;
  /** 占位图 */
  placeholder?: string;
  /** 宽度 */
  width?: number | string;
  /** 高度 */
  height?: number | string;
  /** 自定义类名 */
  className?: string;
  /** 自定义样式 */
  style?: React.CSSProperties;
  /** 加载失败时的图片 */
  onError?: () => void;
}

export const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt = "",
  placeholder = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
  width,
  height,
  className,
  style,
  onError,
}) => {
  const { ref, isVisible } = useLazyLoad();
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  const handleLoad = () => {
    setLoaded(true);
  };

  const handleError = () => {
    setError(true);
    onError?.();
  };

  return (
    <div
      ref={ref}
      style={{
        width,
        height,
        display: "inline-block",
        ...style,
      }}
      className={className}
    >
      {isVisible ? (
        <img
          src={error ? placeholder : src}
          alt={alt}
          onLoad={handleLoad}
          onError={handleError}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            opacity: loaded ? 1 : 0,
            transition: "opacity 0.3s",
          }}
        />
      ) : (
        <img
          src={placeholder}
          alt={alt}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      )}
    </div>
  );
};

/**
 * 记忆化组件（避免不必要的重渲染）
 */
interface MemoProps {
  children: React.ReactNode;
  /** 依赖项，用于判断是否需要重新渲染 */
  deps?: any[];
  /** 自定义比较函数 */
  compare?: (prevDeps: any[], nextDeps: any[]) => boolean;
}

export const Memo: React.FC<MemoProps> = React.memo(
  ({ children }) => <>{children}</>,
  (prevProps, nextProps) => {
    if (!prevProps.deps || !nextProps.deps) return false;
    if (prevProps.compare) {
      return prevProps.compare(prevProps.deps, nextProps.deps);
    }
    // 默认浅比较
    if (prevProps.deps.length !== nextProps.deps.length) return false;
    for (let i = 0; i < prevProps.deps.length; i++) {
      if (prevProps.deps[i] !== nextProps.deps[i]) return false;
    }
    return true;
  }
);

/**
 * 大数据表格优化 Hook
 * @param data 数据源
 * @param pageSize 每页大小
 */
export function usePagination<T>(data: T[], pageSize: number = 20) {
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(data.length / pageSize);

  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    return data.slice(start, end);
  }, [data, currentPage, pageSize]);

  const goToPage = useCallback((page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  }, [totalPages]);

  const nextPage = useCallback(() => {
    goToPage(currentPage + 1);
  }, [currentPage, goToPage]);

  const prevPage = useCallback(() => {
    goToPage(currentPage - 1);
  }, [currentPage, goToPage]);

  return {
    data: paginatedData,
    currentPage,
    totalPages,
    total: data.length,
    goToPage,
    nextPage,
    prevPage,
  };
}

/**
 * 搜索优化 Hook（带防抖和缓存）
 */
export function useOptimizedSearch<T>({
  data,
  searchFn,
  debounceMs = 300,
  cacheSize = 10,
}: {
  data: T[];
  searchFn: (item: T, keyword: string) => boolean;
  debounceMs?: number;
  cacheSize?: number;
}) {
  const [keyword, setKeyword] = useState("");
  const [results, setResults] = useState<T[]>(data);
  const cacheRef = useRef<Map<string, T[]>>(new Map());

  // 防抖搜索
  const debouncedSearch = useDebounce((searchKeyword: string) => {
    // 检查缓存
    if (cacheRef.current.has(searchKeyword)) {
      setResults(cacheRef.current.get(searchKeyword)!);
      return;
    }

    // 执行搜索
    const filtered = data.filter((item) => searchFn(item, searchKeyword));

    // 更新缓存
    if (cacheRef.current.size >= cacheSize) {
      // 删除最旧的缓存
      const firstKey = cacheRef.current.keys().next().value;
      if (firstKey) {
        cacheRef.current.delete(firstKey);
      }
    }
    cacheRef.current.set(searchKeyword, filtered);

    setResults(filtered);
  }, debounceMs);

  // 关键词变更
  useEffect(() => {
    debouncedSearch(keyword);
  }, [keyword, debouncedSearch]);

  // 清空搜索
  const clearSearch = useCallback(() => {
    setKeyword("");
    setResults(data);
  }, [data]);

  return {
    keyword,
    setKeyword,
    results,
    clearSearch,
    total: data.length,
    filtered: results.length,
  };
}

export default {
  useDebounce,
  useThrottle,
  useLazyLoad,
  VirtualList,
  LazyImage,
  Memo,
  usePagination,
  useOptimizedSearch,
};
