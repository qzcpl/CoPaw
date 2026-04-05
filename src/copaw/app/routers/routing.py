# -*- coding: utf-8 -*-
"""Routing configuration API routes."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/routing", tags=["routing"])


ROUTING_STRATEGIES_DB: Dict[str, Dict[str, Any]] = {}
ROUTING_CONFIGS_DB: Dict[str, Dict[str, Any]] = {}
ROUTING_DECISIONS: List[Dict[str, Any]] = []


class RoutingStrategyResponse(BaseModel):
    """Routing strategy response."""

    strategy_id: str
    strategy_name: str
    strategy_type: Literal["direct", "round_robin", "weighted", "skill_based"]
    tenant_id: str
    config: Dict[str, Any]
    status: Literal["active", "inactive"] = "active"
    created_at: str
    updated_at: str


class RoutingStrategyCreateRequest(BaseModel):
    """Routing strategy create request."""

    strategy_name: str
    strategy_type: Literal["direct", "round_robin", "weighted", "skill_based"]
    tenant_id: str
    config: Optional[Dict[str, Any]] = None


class RoutingStrategyUpdateRequest(BaseModel):
    """Routing strategy update request."""

    strategy_name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[Literal["active", "inactive"]] = None


class RoutingConfigResponse(BaseModel):
    """Routing config response."""

    config_id: str
    call_id: str
    strategy_id: str
    strategy_type: str
    config: Dict[str, Any]
    targets: List[str]
    status: str


class RoutingConfigCreateRequest(BaseModel):
    """Routing config create request."""

    call_id: str
    strategy_id: str
    tenant_id: str
    config: Optional[Dict[str, Any]] = None
    targets: Optional[List[str]] = None


class RoutingConfigUpdateRequest(BaseModel):
    """Routing config update request."""

    strategy_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    targets: Optional[List[str]] = None


class RoutingDecision(BaseModel):
    """Routing decision response."""

    decision_id: str
    call_id: str
    session_id: str
    strategy_id: str
    selected_agent_id: str
    reason: str
    created_at: str


class RoutingTestResult(BaseModel):
    """Routing test result."""

    selected_agent_id: str
    reason: str
    score: float


class AgentRoutingStatus(BaseModel):
    """Agent routing status."""

    agent_id: str
    tenant_id: str
    active_sessions: int
    total_routed: int
    last_routed_at: Optional[str]


class RoutingStatsResponse(BaseModel):
    """Routing stats response."""

    tenant_id: str
    total_decisions: int
    by_strategy: Dict[str, int]
    by_agent: Dict[str, int]


def _get_current_user(request: Request) -> Dict[str, str]:
    """Get current user from request state."""
    user = getattr(request.state, "user", None)
    if not user:
        return {
            "user_id": "default",
            "tenant_id": "default",
            "role": "tenant_admin",
        }
    return {
        "user_id": user,
        "tenant_id": "default",
        "role": "tenant_admin",
    }


@router.get("/strategies", response_model=List[RoutingStrategyResponse])
async def list_routing_strategies(
    request: Request,
    tenant_id: Optional[str] = Query(None),
    strategy_type: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """List routing strategies."""
    _get_current_user(request)
    strategies = list(ROUTING_STRATEGIES_DB.values())
    if tenant_id:
        strategies = [s for s in strategies if s.get("tenant_id") == tenant_id]
    if strategy_type:
        strategies = [
            s for s in strategies if s.get("strategy_type") == strategy_type
        ]
    return strategies


@router.get(
    "/strategies/{strategy_id}",
    response_model=RoutingStrategyResponse,
)
async def get_routing_strategy(
    request: Request,
    strategy_id: str,
) -> Dict[str, Any]:
    """Get routing strategy details."""
    _get_current_user(request)
    strategy = ROUTING_STRATEGIES_DB.get(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=404,
            detail=f"Routing strategy not found: {strategy_id}",
        )
    return strategy


@router.post("/strategies", response_model=RoutingStrategyResponse)
async def create_routing_strategy(
    request: Request,
    data: RoutingStrategyCreateRequest,
) -> Dict[str, Any]:
    """Create routing strategy."""
    _get_current_user(request)
    strategy_id = (
        f"strategy_{data.strategy_name}_{int(datetime.utcnow().timestamp())}"
    )
    strategy = {
        "strategy_id": strategy_id,
        "strategy_name": data.strategy_name,
        "strategy_type": data.strategy_type,
        "tenant_id": data.tenant_id,
        "config": data.config or {},
        "status": "active",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    ROUTING_STRATEGIES_DB[strategy_id] = strategy
    return strategy


@router.put(
    "/strategies/{strategy_id}",
    response_model=RoutingStrategyResponse,
)
async def update_routing_strategy(
    request: Request,
    strategy_id: str,
    data: RoutingStrategyUpdateRequest,
) -> Dict[str, Any]:
    """Update routing strategy."""
    _get_current_user(request)
    strategy = ROUTING_STRATEGIES_DB.get(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=404,
            detail=f"Routing strategy not found: {strategy_id}",
        )
    if data.strategy_name:
        strategy["strategy_name"] = data.strategy_name
    if data.config:
        strategy["config"] = data.config
    if data.status:
        strategy["status"] = data.status
    strategy["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return strategy


@router.delete("/strategies/{strategy_id}")
async def delete_routing_strategy(
    request: Request,
    strategy_id: str,
) -> Dict[str, str]:
    """Delete routing strategy."""
    _get_current_user(request)
    if strategy_id not in ROUTING_STRATEGIES_DB:
        raise HTTPException(
            status_code=404,
            detail=f"Routing strategy not found: {strategy_id}",
        )
    del ROUTING_STRATEGIES_DB[strategy_id]
    return {"message": "Routing strategy deleted successfully"}


@router.get("/configs", response_model=List[RoutingConfigResponse])
async def list_routing_configs(
    request: Request,
    tenant_id: Optional[str] = Query(None),
    call_id: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """List routing configs."""
    _get_current_user(request)
    configs = list(ROUTING_CONFIGS_DB.values())
    if call_id:
        configs = [c for c in configs if c.get("call_id") == call_id]
    return configs


@router.get("/configs/{config_id}", response_model=RoutingConfigResponse)
async def get_routing_config(
    request: Request,
    config_id: str,
) -> Dict[str, Any]:
    """Get routing config details."""
    _get_current_user(request)
    config = ROUTING_CONFIGS_DB.get(config_id)
    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"Routing config not found: {config_id}",
        )
    return config


@router.post("/configs", response_model=RoutingConfigResponse)
async def create_routing_config(
    request: Request,
    data: RoutingConfigCreateRequest,
) -> Dict[str, Any]:
    """Create routing config."""
    _get_current_user(request)
    config_id = f"config_{data.call_id}"
    config = {
        "config_id": config_id,
        "call_id": data.call_id,
        "strategy_id": data.strategy_id,
        "strategy_type": "direct",
        "config": data.config or {},
        "targets": data.targets or [],
        "status": "active",
    }
    ROUTING_CONFIGS_DB[config_id] = config
    return config


@router.put("/configs/{config_id}", response_model=RoutingConfigResponse)
async def update_routing_config(
    request: Request,
    config_id: str,
    data: RoutingConfigUpdateRequest,
) -> Dict[str, Any]:
    """Update routing config."""
    _get_current_user(request)
    config = ROUTING_CONFIGS_DB.get(config_id)
    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"Routing config not found: {config_id}",
        )
    if data.strategy_id:
        config["strategy_id"] = data.strategy_id
    if data.config:
        config["config"] = data.config
    if data.targets:
        config["targets"] = data.targets
    return config


@router.delete("/configs/{config_id}")
async def delete_routing_config(
    request: Request,
    config_id: str,
) -> Dict[str, str]:
    """Delete routing config."""
    _get_current_user(request)
    if config_id not in ROUTING_CONFIGS_DB:
        raise HTTPException(
            status_code=404,
            detail=f"Routing config not found: {config_id}",
        )
    del ROUTING_CONFIGS_DB[config_id]
    return {"message": "Routing config deleted successfully"}


@router.get("/decisions", response_model=List[RoutingDecision])
async def get_routing_decisions(
    request: Request,
    call_id: str = Query(...),
    session_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
) -> List[Dict[str, Any]]:
    """Get routing decisions."""
    _get_current_user(request)
    decisions = [d for d in ROUTING_DECISIONS if d.get("call_id") == call_id]
    if session_id:
        decisions = [d for d in decisions if d.get("session_id") == session_id]
    return decisions[:limit]


@router.post(
    "/strategies/{strategy_id}/test",
    response_model=RoutingTestResult,
)
async def test_routing_strategy(
    request: Request,
    strategy_id: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """Test routing strategy."""
    _get_current_user(request)
    if strategy_id not in ROUTING_STRATEGIES_DB:
        raise HTTPException(
            status_code=404,
            detail=f"Routing strategy not found: {strategy_id}",
        )
    return {
        "selected_agent_id": "agent_default",
        "reason": "Test routing result",
        "score": 1.0,
    }


@router.get("/agents/status", response_model=List[AgentRoutingStatus])
async def get_agent_routing_status(
    request: Request,
    tenant_id: str = Query(...),
) -> List[Dict[str, Any]]:
    """Get agent routing status."""
    _get_current_user(request)
    return [
        {
            "agent_id": "agent_default",
            "tenant_id": tenant_id,
            "active_sessions": 0,
            "total_routed": 0,
            "last_routed_at": None,
        },
    ]


@router.get("/stats", response_model=RoutingStatsResponse)
async def get_routing_stats(
    request: Request,
    tenant_id: str = Query(...),
    start_time: str = Query(...),
    end_time: str = Query(...),
) -> Dict[str, Any]:
    """Get routing stats."""
    _get_current_user(request)
    return {
        "tenant_id": tenant_id,
        "total_decisions": len(ROUTING_DECISIONS),
        "by_strategy": {},
        "by_agent": {},
    }
