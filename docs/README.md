# CoPaw 频道架构重构 - 阶段 1 代码补丁

> **版本：** v1.0  
> **日期：** 2026-03-31  
> **阶段：** 基础标识体系实现

---

## 📁 目录结构

```
patch/
├── src/copaw/
│   ├── identifier/                    # 标识符模块（新增）
│   │   ├── __init__.py
│   │   ├── schemas.py                 # 六层标识符数据结构
│   │   ├── generator.py               # 标识符生成器
│   │   └── validator.py               # 标识符验证器
│   │
│   └── app/
│       ├── channels/
│       │   └── schema.py              # 修改：+BusMessage v3, +SessionContext v2
│       │
│       └── database/                  # 数据库模块（新增）
│           ├── __init__.py
│           ├── connection.py          # 数据库连接管理
│           ├── models.py              # 数据库模型（5 张表）
│           └── migrations/
│               ├── 001_initial_schema.sql  # SQL 迁移脚本
│               └── runner.py               # 迁移执行器
│
└── tests/
    └── identifier/
        └── test_identifier.py         # 单元测试（21 个测试）
```

---

## 📋 文件清单

### **新增模块（2 个）**

| 文件 | 大小 | 说明 |
|------|------|------|
| `src/copaw/identifier/__init__.py` | 0.5KB | 模块导出 |
| `src/copaw/identifier/schemas.py` | 9.5KB | 六层标识符数据结构 |
| `src/copaw/identifier/generator.py` | 7.2KB | 标识符生成器 |
| `src/copaw/identifier/validator.py` | 9.0KB | 标识符验证器 |
| `src/copaw/app/database/__init__.py` | 0.4KB | 模块导出 |
| `src/copaw/app/database/connection.py` | 1.8KB | 数据库连接管理 |
| `src/copaw/app/database/models.py` | 10.3KB | 数据库模型（5 张表） |
| `src/copaw/app/database/migrations/001_initial_schema.sql` | 5.4KB | SQL 迁移脚本 |
| `src/copaw/app/database/migrations/runner.py` | 3.3KB | 迁移执行器 |

### **修改文件（1 个）**

| 文件 | 修改量 | 说明 |
|------|--------|------|
| `src/copaw/app/channels/schema.py` | +15KB | BusMessage v3 + SessionContext v2 |

### **测试文件（1 个）**

| 文件 | 大小 | 说明 |
|------|------|------|
| `tests/identifier/test_identifier.py` | 10KB | 单元测试（21 个测试） |

**总代码量：** 约 **70KB**

---

## 🚀 安装方法

### **方法 1：直接覆盖（推荐）**

```bash
# 在 CoPaw_channel_patch/patch 目录下
xcopy /E /Y src\copaw\*.* C:\path\to\CoPaw\src\copaw\
xcopy /E /Y tests\identifier\*.* C:\path\to\CoPaw\tests\identifier\
```

### **方法 2：手动复制**

1. 复制 `src/copaw/identifier/` 到 CoPaw 源码目录
2. 复制 `src/copaw/app/database/` 到 CoPaw 源码目录
3. 覆盖 `src/copaw/app/channels/schema.py`
4. 复制 `tests/identifier/` 到 CoPaw 测试目录

### **方法 3：使用脚本**

```bash
# Windows
robocopy src\copaw C:\path\to\CoPaw\src\copaw /E /IS /IT
robocopy tests\identifier C:\path\to\CoPaw\tests\identifier /E /IS /IT
```

---

## ✅ 验证安装

### **1. 导入测试**

```python
# 测试标识符模块
from copaw.identifier import (
    ChannelId,
    CallerLogicalId,
    CallerPhysicalId,
    CalledId,
    SessionId,
    MessageId,
    Identifiers,
    IdentifierGenerator,
    IdentifierValidator,
)

# 测试数据库模块
from copaw.app.database import (
    IdentifierRegistry,
    SessionRecord,
    MessageLog,
    ChannelConfig,
    AgentBinding,
    get_engine,
    get_session,
)

# 测试频道模块
from copaw.app.channels.schema import (
    BusMessage,
    SessionContext,
    UserProfile,
    GroupContext,
)

print("✅ 所有模块导入成功！")
```

### **2. 功能测试**

```python
from copaw.identifier import IdentifierGenerator

gen = IdentifierGenerator()

# 测试私聊标识符
identifiers = gen.generate_private_identifiers(
    channel_type="dingtalk",
    user_id="user_001",
    called_id="400-001",
)
print(f"私聊标识符：{identifiers}")

# 测试群聊标识符
identifiers = gen.generate_group_identifiers(
    channel_type="dingtalk",
    group_id="group_001",
    user_id="user_001",
    called_id="400-001",
)
print(f"群聊标识符：{identifiers}")

print("✅ 功能测试通过！")
```

### **3. 单元测试**

```bash
cd tests/identifier
python -m pytest test_identifier.py -v
```

**预期输出：**
```
======================= 21 passed, 2 warnings in 0.27s ========================
```

---

## 📊 核心功能

### **1. 六层标识体系**

| 层级 | 标识符 | 说明 | 示例 |
|------|--------|------|------|
| L1 | ChannelId | 传输层 | `dingtalk`, `feishu` |
| L2 | CallerLogicalId | 逻辑主叫 | `user_001`, `group_001` |
| L3 | CallerPhysicalId | 物理主叫 | `user_001` |
| L4 | CalledId | 被叫 | `400-001`, `800-123` |
| L5 | SessionId | 会话 | `session_abc123` |
| L6 | MessageId | 消息 | `msg_xyz789` |

### **2. BusMessage v3**

```python
message = BusMessage(
    message_id="msg_123",
    channel_id="dingtalk",
    caller_logical_id="group_001",
    caller_physical_id="user_001",
    called_id="400-001",
    session_id="session_abc",
    channel_type="group",
    content="Hello, group!",
    group_name="测试群",
    sender_name="张三",
)
```

### **3. SessionContext v2（会话穿透）**

```python
context = SessionContext(
    channel="dingtalk",
    caller_logical_id="group_001",
    caller_physical_id="user_001",
    called_id="400-001",
    session_id="session_abc",
    group_context=GroupContext(
        group_id="group_001",
        group_name="测试群",
        member_count=50,
    ),
)
```

### **4. 数据库表（5 张）**

1. **identifier_registry** - CalledId 路由（携号转网）
2. **session_records** - 会话记录
3. **message_logs** - 消息日志
4. **channel_configs** - 频道配置
5. **agent_bindings** - Agent 绑定

---

## 🧪 测试结果

```
============================= test session starts =============================
platform win32 -- Python 3.13.12, pytest-9.0.2, pluggy-1.5.0
collected 21 items

test_identifier.py::TestChannelId::test_valid_channel_id PASSED
test_identifier.py::TestChannelId::test_invalid_channel_id PASSED
test_identifier.py::TestCallerLogicalId::test_valid_user_caller PASSED
test_identifier.py::TestCallerLogicalId::test_valid_group_caller PASSED
test_identifier.py::TestCallerLogicalId::test_invalid_caller PASSED
test_identifier.py::TestCalledId::test_valid_phone_format PASSED
test_identifier.py::TestCalledId::test_valid_uuid_format PASSED
test_identifier.py::TestCalledId::test_invalid_called_id PASSED
test_identifier.py::TestIdentifiers::test_private_identifiers PASSED
test_identifier.py::TestIdentifiers::test_group_identifiers PASSED
test_identifier.py::TestIdentifiers::test_invalid_private_identifiers PASSED
test_identifier.py::TestIdentifiers::test_to_dict PASSED
test_identifier.py::TestIdentifiers::test_from_dict PASSED
test_identifier.py::TestIdentifierGenerator::test_generate_private_identifiers PASSED
test_identifier.py::TestIdentifierGenerator::test_generate_group_identifiers PASSED
test_identifier.py::TestIdentifierValidator::test_valid_identifiers PASSED
test_identifier.py::TestIdentifierValidator::test_invalid_identifiers PASSED
test_identifier.py::TestIdentifierValidator::test_assert_valid PASSED
test_identifier.py::TestIdentifierValidator::test_assert_valid_raises PASSED
test_identifier.py::TestHelperFunctions::test_create_private_identifiers PASSED
test_identifier.py::TestHelperFunctions::test_create_group_identifiers PASSED

======================= 21 passed, 2 warnings in 0.27s ========================
```

**通过率：** 100% (21/21) ✅

---

## 📝 使用说明

### **创建私聊标识符**

```python
from copaw.identifier import IdentifierGenerator

gen = IdentifierGenerator()

identifiers = gen.generate_private_identifiers(
    channel_type="dingtalk",
    user_id="user_001",
    called_id="400-001",
)

print(identifiers.channel_id)           # dingtalk
print(identifiers.caller_logical_id)    # user_001
print(identifiers.caller_physical_id)   # user_001
print(identifiers.called_id)            # 400-001
```

### **创建群聊标识符**

```python
identifiers = gen.generate_group_identifiers(
    channel_type="dingtalk",
    group_id="group_001",
    user_id="user_001",
    called_id="400-001",
)

print(identifiers.caller_logical_id)    # group_001（群 ID）
print(identifiers.caller_physical_id)   # user_001（实际发送者）
```

### **验证标识符**

```python
from copaw.identifier import IdentifierValidator

valid, error = IdentifierValidator.validate_identifiers(identifiers)
if not valid:
    raise ValueError(f"Invalid identifiers: {error}")
```

### **初始化数据库**

```python
from copaw.app.database import init_database, create_tables

# 初始化数据库连接
init_database("sqlite:///copaw.db", echo=False)

# 创建表
create_tables()

# 或运行迁移脚本
from copaw.app.database.migrations.runner import run_migrations
run_migrations()
```

---

## 🔗 相关文档

- **阶段 1 完成报告：** `../STAGE_1_COMPLETION_REPORT.md`
- **实施日志：** `../implementation_log.md`
- **详细设计文档：** `../01_identifier_design.md`
- **主方案文档：** `C:\Users\qzcpl\Desktop\CoPaw 频道架构重构方案.md`

---

## ⚠️ 注意事项

1. **备份原文件** - 覆盖前请备份原有代码
2. **测试环境验证** - 建议先在测试环境验证
3. **数据库迁移** - 首次使用需运行迁移脚本
4. **依赖检查** - 确保 SQLAlchemy 已安装

---

## 📦 依赖

```txt
sqlalchemy>=2.0.0
pytest>=7.0.0
```

---

## 🎉 总结

✅ **代码量：** 70KB（11 个文件）  
✅ **测试：** 21/21 通过（100%）  
✅ **六层标识体系：** 完整实现  
✅ **群聊支持：** 完整实现  
✅ **会话穿透：** 数据结构完成  
✅ **数据库：** 5 张表 + 迁移脚本  

---

**补丁版本：** v1.0  
**生成日期：** 2026-03-31  
**负责人：** 贾维斯 2 号
