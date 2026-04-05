-- ============================================================
-- CoPaw 频道架构重构 - 数据库迁移脚本
-- 版本：v2.0
-- 日期：2026-03-31
-- ============================================================

-- ============================================================
-- 1. 标识符注册表（CalledId 路由表）
-- ============================================================

CREATE TABLE IF NOT EXISTS identifier_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    called_id VARCHAR(64) UNIQUE NOT NULL,
    agent_id VARCHAR(64) NOT NULL,
    priority INTEGER DEFAULT 0,
    weight INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT 1,
    metadata JSON DEFAULT '{}',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 索引：加速 called_id 查询
CREATE INDEX IF NOT EXISTS idx_called_id_active ON identifier_registry(called_id, is_active);


-- ============================================================
-- 2. 会话记录表
-- ============================================================

CREATE TABLE IF NOT EXISTS session_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(128) UNIQUE NOT NULL,
    channel_id VARCHAR(64) NOT NULL,
    caller_logical_id VARCHAR(128) NOT NULL,
    caller_physical_id VARCHAR(128) NOT NULL,
    called_id VARCHAR(64) NOT NULL,
    channel_type VARCHAR(16) DEFAULT 'private',
    group_id VARCHAR(128),
    status VARCHAR(16) DEFAULT 'active',
    message_count INTEGER DEFAULT 0,
    metadata JSON DEFAULT '{}',
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    closed_at DATETIME
);

-- 索引：加速会话查询
CREATE INDEX IF NOT EXISTS idx_session_caller ON session_records(caller_logical_id, started_at);
CREATE INDEX IF NOT EXISTS idx_session_called ON session_records(called_id, started_at);
CREATE INDEX IF NOT EXISTS idx_session_status ON session_records(status, last_active_at);


-- ============================================================
-- 3. 消息日志表
-- ============================================================

CREATE TABLE IF NOT EXISTS message_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id VARCHAR(128) UNIQUE NOT NULL,
    session_id VARCHAR(128) NOT NULL,
    channel_id VARCHAR(64) NOT NULL,
    caller_logical_id VARCHAR(128) NOT NULL,
    caller_physical_id VARCHAR(128) NOT NULL,
    called_id VARCHAR(64) NOT NULL,
    content TEXT,
    content_type VARCHAR(32) DEFAULT 'text',
    direction VARCHAR(16) DEFAULT 'inbound',
    status VARCHAR(16) DEFAULT 'sent',
    metadata JSON DEFAULT '{}',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 索引：加速消息查询
CREATE INDEX IF NOT EXISTS idx_message_session ON message_logs(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_message_caller ON message_logs(caller_physical_id, created_at);
CREATE INDEX IF NOT EXISTS idx_message_status ON message_logs(status, created_at);


-- ============================================================
-- 4. 频道配置表
-- ============================================================

CREATE TABLE IF NOT EXISTS channel_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id VARCHAR(64) UNIQUE NOT NULL,
    channel_type VARCHAR(32) NOT NULL,
    config JSON DEFAULT '{}',
    is_enabled BOOLEAN DEFAULT 1,
    metadata JSON DEFAULT '{}',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 索引：加速频道查询
CREATE INDEX IF NOT EXISTS idx_channel_type ON channel_configs(channel_type, is_enabled);


-- ============================================================
-- 5. Agent 绑定表
-- ============================================================

CREATE TABLE IF NOT EXISTS agent_bindings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id VARCHAR(64) NOT NULL,
    channel_id VARCHAR(64) NOT NULL,
    called_id VARCHAR(64),
    tenant_id VARCHAR(64),
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    metadata JSON DEFAULT '{}',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_id, channel_id, called_id)
);

-- 索引：加速绑定查询
CREATE INDEX IF NOT EXISTS idx_agent_active ON agent_bindings(agent_id, is_active);
CREATE INDEX IF NOT EXISTS idx_channel_active ON agent_bindings(channel_id, is_active);
CREATE INDEX IF NOT EXISTS idx_tenant_active ON agent_bindings(tenant_id, is_active);


-- ============================================================
-- 初始化数据（示例）
-- ============================================================

-- 默认 Agent 绑定
INSERT OR IGNORE INTO agent_bindings (agent_id, channel_id, called_id, tenant_id, priority, is_active)
VALUES 
    ('default', 'console', NULL, 'default', 0, 1),
    ('default', 'dingtalk', NULL, 'default', 0, 1),
    ('default', 'feishu', NULL, 'default', 0, 1);

-- 默认 CalledId 路由
INSERT OR IGNORE INTO identifier_registry (called_id, agent_id, priority, weight, is_active)
VALUES 
    ('400-001', 'default', 0, 100, 1),
    ('400-002', 'default', 0, 100, 1);

-- 默认频道配置
INSERT OR IGNORE INTO channel_configs (channel_id, channel_type, config, is_enabled)
VALUES 
    ('console', 'console', '{}', 1),
    ('dingtalk', 'dingtalk', '{}', 1),
    ('feishu', 'feishu', '{}', 1);


-- ============================================================
-- 迁移完成
-- ============================================================
