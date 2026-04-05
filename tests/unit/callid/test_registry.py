"""
CallIdRegistry 单元测试

测试 callId 注册、绑定、查询、切换
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock

# 添加补丁目录到路径
patch_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(patch_src))

from copaw.app.callid.registry import (
    CallIdRegistry,
    CallIdBinding,
    BindingStatus,
)
from copaw.app.callid.schemas import (
    CallIdInfo,
    AgentInfo,
    TenantInfo,
)


class TestCallIdRegistryBasic:
    """CallIdRegistry 基础功能测试"""
    
    @pytest.fixture
    def registry(self):
        """创建注册表实例"""
        return CallIdRegistry()
    
    def test_bind_callid(self, registry):
        """测试绑定 callId"""
        result = registry.bind(
            call_id="400-001",
            agent_id="agent-default",
            tenant_id="tenant-abc",
            channel_id="dingtalk",
        )
        
        assert result.success is True
        assert result.call_id == "400-001"
        assert result.agent_id == "agent-default"
    
    def test_bind_callid_duplicate(self, registry):
        """测试重复绑定"""
        # 第一次绑定
        registry.bind(
            call_id="400-001",
            agent_id="agent-default",
            tenant_id="tenant-abc",
            channel_id="dingtalk",
        )
        
        # 第二次绑定（应该失败）
        result = registry.bind(
            call_id="400-001",
            agent_id="agent-other",
            tenant_id="tenant-abc",
            channel_id="dingtalk",
        )
        
        assert result.success is False
        assert "already bound" in result.error.lower()
    
    def test_query_binding(self, registry):
        """测试查询绑定"""
        # 先绑定
        registry.bind(
            call_id="400-001",
            agent_id="agent-default",
            tenant_id="tenant-abc",
            channel_id="dingtalk",
        )
        
        # 查询
        binding = registry.query("400-001")
        
        assert binding is not None
        assert binding.call_id == "400-001"
        assert binding.agent_id == "agent-default"
        assert binding.tenant_id == "tenant-abc"
    
    def test_query_nonexistent(self, registry):
        """测试查询不存在的 callId"""
        binding = registry.query("400-999")
        
        assert binding is None
    
    def test_unbind_callid(self, registry):
        """测试解绑 callId"""
        # 先绑定
        registry.bind(
            call_id="400-001",
            agent_id="agent-default",
            tenant_id="tenant-abc",
            channel_id="dingtalk",
        )
        
        # 解绑
        result = registry.unbind("400-001")
        
        assert result.success is True
        
        # 验证已解绑
        binding = registry.query("400-001")
        assert binding is None
    
    def test_list_bindings(self, registry):
        """测试列出所有绑定"""
        # 绑定多个
        registry.bind("400-001", "agent-1", "tenant-abc", "dingtalk")
        registry.bind("400-002", "agent-2", "tenant-abc", "dingtalk")
        registry.bind("400-003", "agent-3", "tenant-xyz", "feishu")
        
        # 列出所有
        bindings = registry.list_bindings()
        
        assert len(bindings) == 3
    
    def test_list_bindings_by_tenant(self, registry):
        """测试按租户列出绑定"""
        # 绑定多个
        registry.bind("400-001", "agent-1", "tenant-abc", "dingtalk")
        registry.bind("400-002", "agent-2", "tenant-abc", "dingtalk")
        registry.bind("400-003", "agent-3", "tenant-xyz", "feishu")
        
        # 按租户列出
        bindings = registry.list_bindings(tenant_id="tenant-abc")
        
        assert len(bindings) == 2
        assert all(b.tenant_id == "tenant-abc" for b in bindings)
    
    def test_list_bindings_by_agent(self, registry):
        """测试按 Agent 列出绑定"""
        # 绑定多个
        registry.bind("400-001", "agent-default", "tenant-abc", "dingtalk")
        registry.bind("400-002", "agent-default", "tenant-xyz", "dingtalk")
        registry.bind("400-003", "agent-other", "tenant-abc", "feishu")
        
        # 按 Agent 列出
        bindings = registry.list_bindings(agent_id="agent-default")
        
        assert len(bindings) == 2
        assert all(b.agent_id == "agent-default" for b in bindings)


class TestCallIdSwitch:
    """callId 切换测试（携号转网）"""
    
    @pytest.fixture
    def registry(self):
        """创建注册表实例"""
        return CallIdRegistry()
    
    def test_switch_agent(self, registry):
        """测试切换 Agent（携号转网）"""
        # 初始绑定
        registry.bind(
            call_id="400-001",
            agent_id="agent-old",
            tenant_id="tenant-abc",
            channel_id="dingtalk",
        )
        
        # 切换 Agent
        result = registry.switch_agent(
            call_id="400-001",
            new_agent_id="agent-new",
        )
        
        assert result.success is True
        
        # 验证切换后
        binding = registry.query("400-001")
        assert binding.agent_id == "agent-new"
    
    def test_switch_agent_preserves_session(self, registry):
        """测试切换 Agent 保留会话"""
        # 初始绑定（带 session_id）
        registry.bind(
            call_id="400-001",
            agent_id="agent-old",
            tenant_id="tenant-abc",
            channel_id="dingtalk",
            session_id="sess_001",
        )
        
        # 切换 Agent
        registry.switch_agent(
            call_id="400-001",
            new_agent_id="agent-new",
        )
        
        # 验证 session_id 保留
        binding = registry.query("400-001")
        assert binding.session_id == "sess_001"
    
    def test_switch_agent_nonexistent(self, registry):
        """测试切换不存在的 callId"""
        result = registry.switch_agent(
            call_id="400-999",
            new_agent_id="agent-new",
        )
        
        assert result.success is False
        assert "not found" in result.error.lower()


class TestCallIdBinding:
    """CallIdBinding 数据测试"""
    
    def test_binding_to_dict(self):
        """测试绑定转字典"""
        binding = CallIdBinding(
            call_id="400-001",
            agent_id="agent-default",
            tenant_id="tenant-abc",
            channel_id="dingtalk",
            session_id="sess_001",
            status=BindingStatus.ACTIVE,
        )
        
        data = binding.to_dict()
        
        assert data["call_id"] == "400-001"
        assert data["agent_id"] == "agent-default"
        assert data["status"] == "active"
    
    def test_binding_from_dict(self):
        """测试从字典创建绑定"""
        data = {
            "call_id": "400-001",
            "agent_id": "agent-default",
            "tenant_id": "tenant-abc",
            "channel_id": "dingtalk",
            "session_id": "sess_001",
            "status": "active",
        }
        
        binding = CallIdBinding.from_dict(data)
        
        assert binding.call_id == "400-001"
        assert binding.agent_id == "agent-default"
        assert binding.status == BindingStatus.ACTIVE
    
    def test_binding_str(self):
        """测试绑定字符串表示"""
        binding = CallIdBinding(
            call_id="400-001",
            agent_id="agent-default",
            tenant_id="tenant-abc",
            channel_id="dingtalk",
            status=BindingStatus.ACTIVE,
        )
        
        str_repr = str(binding)
        
        assert "400-001" in str_repr
        assert "agent-default" in str_repr


class TestBindingStatus:
    """绑定状态测试"""
    
    def test_status_values(self):
        """测试状态枚举值"""
        assert BindingStatus.ACTIVE.value == "active"
        assert BindingStatus.INACTIVE.value == "inactive"
        assert BindingStatus.SUSPENDED.value == "suspended"
        assert BindingStatus.DELETED.value == "deleted"
    
    def test_status_is_active(self):
        """测试判断是否活跃"""
        assert BindingStatus.ACTIVE.is_active() is True
        assert BindingStatus.INACTIVE.is_active() is False
        assert BindingStatus.SUSPENDED.is_active() is False


class TestCallIdInfo:
    """CallIdInfo 数据测试"""
    
    def test_callid_info_creation(self):
        """测试创建 callId 信息"""
        info = CallIdInfo(
            call_id="400-001",
            display_name="客服热线",
            description="客户服务热线",
            tenant_id="tenant-abc",
        )
        
        assert info.call_id == "400-001"
        assert info.display_name == "客服热线"
    
    def test_callid_info_with_agent(self):
        """测试带 Agent 信息的 callId"""
        agent_info = AgentInfo(
            agent_id="agent-default",
            agent_name="默认助手",
        )
        
        info = CallIdInfo(
            call_id="400-001",
            display_name="客服热线",
            tenant_id="tenant-abc",
            current_agent=agent_info,
        )
        
        assert info.current_agent.agent_name == "默认助手"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
