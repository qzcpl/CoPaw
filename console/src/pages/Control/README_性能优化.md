# 性能优化使用指南

**版本：** v1.0  
**日期：** 2026-04-01  
**文件位置：** `src/utils/performance.tsx`

---

## 功能概述

性能优化工具集提供常用的前端性能优化方案：

- ✅ 防抖（Debounce）
- ✅ 节流（Throttle）
- ✅ 懒加载（Lazy Load）
- ✅ 虚拟列表（Virtual List）
- ✅ 图片懒加载（Lazy Image）
- ✅ 记忆化组件（Memo）
- ✅ 分页优化（Pagination）
- ✅ 搜索优化（Optimized Search）

---

## API 文档

### 1. useDebounce（防抖）

**使用场景：** 搜索框输入、窗口 resize 等频繁触发场景

```typescript
import { useDebounce } from "@/utils/performance";

function SearchBox() {
  const [value, setValue] = useState("");
  
  // 500ms 防抖
  const debouncedSearch = useDebounce((keyword: string) => {
    // 执行搜索逻辑
    api.search(keyword);
  }, 500);
  
  return (
    <Input
      onChange={(e) => {
        setValue(e.target.value);
        debouncedSearch(e.target.value);
      }}
    />
  );
}
```

**参数：**
- `fn`: 要执行的函数
- `delay`: 延迟时间（毫秒）

**返回：** 防抖处理后的函数

---

### 2. useThrottle（节流）

**使用场景：** 滚动事件、鼠标移动等高频事件

```typescript
import { useThrottle } from "@/utils/performance";

function ScrollComponent() {
  // 100ms 节流
  const handleScroll = useThrottle((e: UIEvent) => {
    console.log("滚动位置:", e.currentTarget.scrollTop);
  }, 100);
  
  return (
    <div onScroll={handleScroll} style={{ height: 400, overflow: "auto" }}>
      {/* 内容 */}
    </div>
  );
}
```

**参数：**
- `fn`: 要执行的函数
- `interval`: 间隔时间（毫秒）

**返回：** 节流处理后的函数

---

### 3. useLazyLoad（懒加载）

**使用场景：** 图片懒加载、组件按需加载

```typescript
import { useLazyLoad } from "@/utils/performance";

function LazyComponent() {
  const { ref, isVisible } = useLazyLoad({ threshold: 0.1 });
  
  return (
    <div ref={ref}>
      {isVisible ? (
        <HeavyComponent />
      ) : (
        <div>加载中...</div>
      )}
    </div>
  );
}
```

**参数：**
- `options`: IntersectionObserver 选项（默认 `{ threshold: 0.1 }`）

**返回：**
- `ref`: 需要观察的元素引用
- `isVisible`: 元素是否进入视口

---

### 4. VirtualList（虚拟列表）

**使用场景：** 大数据量列表/表格（1000+ 项）

```typescript
import { VirtualList } from "@/utils/performance";

function LargeList() {
  const data = Array.from({ length: 10000 }, (_, i) => ({
    id: `item-${i}`,
    name: `项目 ${i}`,
  }));
  
  return (
    <VirtualList
      data={data}
      itemHeight={50}
      containerHeight={600}
      bufferSize={5}
      renderItem={(item, index) => (
        <div style={{ height: 50, padding: 10 }}>
          {item.name}
        </div>
      )}
    />
  );
}
```

**参数：**
- `data`: 数据源
- `itemHeight`: 每项高度（固定高度，必填）
- `containerHeight`: 容器高度
- `renderItem`: 渲染每项的函数
- `getItemKey`: 获取每项唯一键（可选）
- `bufferSize`: 额外缓冲项数（默认 5）

**性能对比：**
- 传统渲染：10,000 项 = 10,000 个 DOM 节点
- 虚拟列表：10,000 项 = 约 20-30 个 DOM 节点（可见区域 + 缓冲）

---

### 5. LazyImage（图片懒加载）

**使用场景：** 图片列表、相册等

```typescript
import { LazyImage } from "@/utils/performance";

function ImageGallery() {
  return (
    <div>
      <LazyImage
        src="https://example.com/image1.jpg"
        alt="图片 1"
        width={300}
        height={200}
        placeholder="/placeholder.jpg"
      />
    </div>
  );
}
```

**参数：**
- `src`: 图片 URL
- `alt`: 替代文本
- `placeholder`: 占位图（默认透明 GIF）
- `width`: 宽度
- `height`: 高度
- `onError`: 加载失败回调

---

### 6. Memo（记忆化组件）

**使用场景：** 避免子组件不必要的重渲染

```typescript
import { Memo } from "@/utils/performance";

function Parent() {
  const [count, setCount] = useState(0);
  const [data, setData] = useState([]);
  
  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>
        Count: {count}
      </button>
      
      <Memo deps={[data]}>
        <ExpensiveComponent data={data} />
      </Memo>
    </div>
  );
}
```

**参数：**
- `children`: 子组件
- `deps`: 依赖项数组
- `compare`: 自定义比较函数（可选）

---

### 7. usePagination（分页优化）

**使用场景：** 大数据集分页展示

```typescript
import { usePagination } from "@/utils/performance";

function PaginatedList() {
  const data = Array.from({ length: 1000 }, (_, i) => i);
  
  const {
    data: paginatedData,
    currentPage,
    totalPages,
    goToPage,
    nextPage,
    prevPage,
  } = usePagination(data, 20); // 每页 20 条
  
  return (
    <div>
      <List dataSource={paginatedData} renderItem={...} />
      
      <Pagination
        current={currentPage}
        total={totalPages * 20}
        onChange={goToPage}
      />
    </div>
  );
}
```

**参数：**
- `data`: 数据源
- `pageSize`: 每页大小（默认 20）

**返回：**
- `data`: 当前页数据
- `currentPage`: 当前页码
- `totalPages`: 总页数
- `total`: 总数据量
- `goToPage`: 跳转到指定页
- `nextPage`: 下一页
- `prevPage`: 上一页

---

### 8. useOptimizedSearch（优化搜索）

**使用场景：** 大数据集搜索（带防抖和缓存）

```typescript
import { useOptimizedSearch } from "@/utils/performance";

function SearchableList() {
  const data = Array.from({ length: 10000 }, (_, i) => ({
    id: `item-${i}`,
    name: `项目 ${i}`,
  }));
  
  const {
    keyword,
    setKeyword,
    results,
    clearSearch,
    total,
    filtered,
  } = useOptimizedSearch({
    data,
    searchFn: (item, keyword) =>
      item.name.toLowerCase().includes(keyword.toLowerCase()),
    debounceMs: 300,
    cacheSize: 20,
  });
  
  return (
    <div>
      <Input.Search
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
      />
      
      <div>
        搜索到 {filtered} / {total} 条结果
      </div>
      
      <List dataSource={results} renderItem={...} />
    </div>
  );
}
```

**参数：**
- `data`: 数据源
- `searchFn`: 搜索匹配函数
- `debounceMs`: 防抖延迟（默认 300ms）
- `cacheSize`: 缓存大小（默认 10 条）

**返回：**
- `keyword`: 当前搜索关键词
- `setKeyword`: 设置关键词
- `results`: 搜索结果
- `clearSearch`: 清空搜索
- `total`: 总数据量
- `filtered`: 过滤后数量

---

## 最佳实践

### 1. 大数据列表优化

**场景：** 展示 10,000+ 条数据

```typescript
// ❌ 不推荐：全量渲染
<List dataSource={largeData} renderItem={...} />

// ✅ 推荐：虚拟列表
<VirtualList
  data={largeData}
  itemHeight={50}
  containerHeight={600}
  renderItem={...}
/>
```

**性能提升：** 10-100 倍

---

### 2. 搜索框优化

**场景：** 实时搜索建议

```typescript
// ❌ 不推荐：每次输入都搜索
<Input onChange={(e) => search(e.target.value)} />

// ✅ 推荐：防抖搜索
const debouncedSearch = useDebounce(search, 500);
<Input onChange={(e) => debouncedSearch(e.target.value)} />

// ✅ 最佳：防抖 + 缓存
const { results, setKeyword } = useOptimizedSearch({
  data,
  searchFn: matchFn,
  debounceMs: 300,
  cacheSize: 20,
});
<Input value={keyword} onChange={(e) => setKeyword(e.target.value)} />
```

**性能提升：** 减少 80-90% 的搜索计算

---

### 3. 滚动事件优化

**场景：** 滚动加载、滚动位置监听

```typescript
// ❌ 不推荐：高频触发
<div onScroll={(e) => handleScroll(e)}>

// ✅ 推荐：节流
const handleScroll = useThrottle((e) => {
  // 处理逻辑
}, 100);
<div onScroll={handleScroll}>
```

**性能提升：** 减少 85% 的事件触发（60fps → 10fps）

---

### 4. 图片加载优化

**场景：** 图片墙、相册

```typescript
// ❌ 不推荐：立即加载所有图片
<img src={largeImageUrl} />

// ✅ 推荐：懒加载 + 占位图
<LazyImage
  src={largeImageUrl}
  placeholder={thumbnailUrl}
  width={300}
  height={200}
/>
```

**性能提升：** 首屏加载时间减少 50-70%

---

### 5. 组件重渲染优化

**场景：** 复杂组件、频繁更新场景

```typescript
// ❌ 不推荐：每次父组件更新都重渲染
<ExpensiveComponent data={data} />

// ✅ 推荐：记忆化
<Memo deps={[data]}>
  <ExpensiveComponent data={data} />
</Memo>

// ✅ 或：React.memo
const MemoizedComponent = React.memo(ExpensiveComponent);
```

**性能提升：** 减少 50-90% 的不必要渲染

---

## 性能对比表

| 优化技术 | 适用场景 | 性能提升 | 内存占用 |
|---------|---------|---------|---------|
| 虚拟列表 | 大数据列表 | 10-100 倍 | 降低 90% |
| 防抖 | 搜索框输入 | 减少 80% 计算 | 不变 |
| 节流 | 滚动/resize | 减少 85% 触发 | 不变 |
| 懒加载 | 图片/组件 | 首屏快 50% | 降低 60% |
| 缓存 | 重复搜索 | 减少 90% 计算 | 增加少量 |
| 分页 | 大数据集 | 渲染快 10 倍 | 降低 95% |

---

## 注意事项

1. **虚拟列表**：需要固定高度，不支持动态高度项
2. **防抖/节流**：根据场景选择合适的延迟时间
3. **懒加载**：SEO 不友好，重要内容不要懒加载
4. **缓存**：注意缓存大小，避免内存泄漏
5. **记忆化**：过度使用会增加内存开销

---

## 相关文件

- **工具集**：`src/utils/performance.tsx`
- **示例页面**：`src/pages/Control/PerformanceOptimization.tsx`
- **演示数据**：10,000 条模拟数据

---

**更新日期：** 2026-04-01  
**维护者：** CoPaw 前端团队
