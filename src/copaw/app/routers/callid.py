# -*- coding: utf-8 -*-
"""callId management API routes."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/callid", tags=["callid"])


class CallIdBindingResponse(BaseModel):
    """callId binding response."""

    call_id: str
    call_type: Literal["shared", "dedicated"]
    owner_agent_id: str
    owner_tenant_id: str
    channel_id: str
    channel_instance_id: str
    routing_strategy: Literal[
        "direct",
        "round_robin",
        "weighted",
        "skill_based",
    ]
    routing_config: Dict[str, Any]
    status: Literal["active", "suspended", "unbound"]
    bound_at: str
    suspended_at: Optional[str] = None
    suspended_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CallIdBindRequest(BaseModel):
    """callId bind request."""

    call_id: str
    agent_id: str
    tenant_id: str
    channel_id: str
    routing_strategy: Optional[
        Literal["direct", "round_robin", "weighted", "skill_based"]
    ] = "direct"
    routing_config: Optional[Dict[str, Any]] = None


class CallIdUnbindRequest(BaseModel):
    """callId unbind request."""

    call_id: str
    tenant_id: str


class CallIdSwitchRequest(BaseModel):
    """Agent switch request."""

    call_id: str
    new_agent_id: str
    tenant_id: str
    reason: Optional[str] = None


class CallIdSuspendRequest(BaseModel):
    """callId suspend request."""

    call_id: str
    tenant_id: str
    reason: str


class CallIdResumeRequest(BaseModel):
    """callId resume request."""

    call_id: str
    tenant_id: str


class CallIdChangeRecordResponse(BaseModel):
    """callId change record response."""

    call_id: str
    change_type: Literal["bind", "switch", "suspend", "resume", "unbind"]
    old_binding: Optional[Dict[str, Any]]
    new_binding: Optional[Dict[str, Any]]
    operator: str
    reason: str
    created_at: str


CALLID_DB: Dict[str, Dict[str, Any]] = {
    "400-001": {
        "call_id": "400-001",
        "call_type": "shared",
        "owner_agent_id": "agent_1",
        "owner_tenant_id": "default",
        "channel_id": "dingtalk",
        "channel_instance_id": "dingtalk_001",
        "routing_strategy": "direct",
        "routing_config": {},
        "status": "active",
        "bound_at": "2026-03-31T10:00:00Z",
        "suspended_at": None,
        "suspended_reason": None,
        "metadata": {},
    },
}

CALLID_HISTORY: List[Dict[str, Any]] = []


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


@router.get("/bindings", response_model=List[CallIdBindingResponse])
async def list_callid_bindings(
    request: Request,
    tenant_id: Optional[str] = Query(None, description="Tenant ID"),
) -> List[Dict[str, Any]]:
    """List callId bindings."""
    current_user = _get_current_user(request)
    effective_tenant_id = tenant_id or current_user["tenant_id"]
    bindings = [
        b
        for b in CALLID_DB.values()
        if b["owner_tenant_id"] == effective_tenant_id
    ]
    return bindings


@router.get("/bindings/{call_id}", response_model=CallIdBindingResponse)
async def get_callid_binding(
    request: Request,
    call_id: str,
    tenant_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get callId binding details."""
    _get_current_user(request)
    binding = CALLID_DB.get(call_id)
    if not binding:
        raise HTTPException(
            status_code=404,
            detail=f"callId not found: {call_id}",
        )
    return binding


@router.post("/bind", response_model=CallIdBindingResponse)
async def bind_callid(
    request: Request,
    data: CallIdBindRequest,
) -> Dict[str, Any]:
    """Bind a callId."""
    current_user = _get_current_user(request)
    if data.call_id in CALLID_DB:
        raise HTTPException(
            status_code=400,
            detail=f"callId already bound: {data.call_id}",
        )
    binding = {
        "call_id": data.call_id,
        "call_type": "shared",
        "owner_agent_id": data.agent_id,
        "owner_tenant_id": data.tenant_id,
        "channel_id": data.channel_id,
        "channel_instance_id": f"{data.channel_id}_{data.call_id}",
        "routing_strategy": data.routing_strategy or "direct",
        "routing_config": data.routing_config or {},
        "status": "active",
        "bound_at": datetime.utcnow().isoformat() + "Z",
        "suspended_at": None,
        "suspended_reason": None,
        "metadata": {},
    }
    CALLID_DB[data.call_id] = binding
    CALLID_HISTORY.append(
        {
            "call_id": data.call_id,
            "change_type": "bind",
            "old_binding": None,
            "new_binding": binding,
            "operator": current_user["user_id"],
            "reason": "Initial binding",
            "created_at": datetime.utcnow().isoformat() + "Z",
        },
    )
    return binding


@router.post("/unbind")
async def unbind_callid(
    request: Request,
    data: CallIdUnbindRequest,
) -> Dict[str, str]:
    """Unbind a callId."""
    current_user = _get_current_user(request)
    binding = CALLID_DB.get(data.call_id)
    if not binding:
        raise HTTPException(
            status_code=404,
            detail=f"callId not found: {data.call_id}",
        )
    old_binding = CALLID_DB.pop(data.call_id)
    CALLID_HISTORY.append(
        {
            "call_id": data.call_id,
            "change_type": "unbind",
            "old_binding": old_binding,
            "new_binding": None,
            "operator": current_user["user_id"],
            "reason": "Unbind callId",
            "created_at": datetime.utcnow().isoformat() + "Z",
        },
    )
    return {"message": "callId unbound successfully"}


@router.post("/switch")
async def switch_agent(
    request: Request,
    data: CallIdSwitchRequest,
) -> Dict[str, str]:
    """Switch agent for a callId."""
    current_user = _get_current_user(request)
    binding = CALLID_DB.get(data.call_id)
    if not binding:
        raise HTTPException(
            status_code=404,
            detail=f"callId not found: {data.call_id}",
        )
    old_binding = binding.copy()
    binding["owner_agent_id"] = data.new_agent_id
    binding["updated_at"] = datetime.utcnow().isoformat() + "Z"
    CALLID_HISTORY.append(
        {
            "call_id": data.call_id,
            "change_type": "switch",
            "old_binding": old_binding,
            "new_binding": binding,
            "operator": current_user["user_id"],
            "reason": data.reason or "Agent switch",
            "created_at": datetime.utcnow().isoformat() + "Z",
        },
    )
    return {"message": "Agent switched successfully"}


@router.post("/bindings/{call_id}/suspend")
async def suspend_callid(
    request: Request,
    call_id: str,
    data: CallIdSuspendRequest,
) -> Dict[str, str]:
    """Suspend a callId."""
    current_user = _get_current_user(request)
    binding = CALLID_DB.get(call_id)
    if not binding:
        raise HTTPException(
            status_code=404,
            detail=f"callId not found: {call_id}",
        )
    binding["status"] = "suspended"
    binding["suspended_at"] = datetime.utcnow().isoformat() + "Z"
    binding["suspended_reason"] = data.reason
    CALLID_HISTORY.append(
        {
            "call_id": call_id,
            "change_type": "suspend",
            "old_binding": binding.copy(),
            "new_binding": binding,
            "operator": current_user["user_id"],
            "reason": data.reason,
            "created_at": datetime.utcnow().isoformat() + "Z",
        },
    )
    return {"message": "callId suspended successfully"}


@router.post("/bindings/{call_id}/resume")
async def resume_callid(
    request: Request,
    call_id: str,
    data: CallIdResumeRequest,
) -> Dict[str, str]:
    """Resume a callId."""
    current_user = _get_current_user(request)
    binding = CALLID_DB.get(call_id)
    if not binding:
        raise HTTPException(
            status_code=404,
            detail=f"callId not found: {call_id}",
        )
    binding["status"] = "active"
    binding["suspended_at"] = None
    binding["suspended_reason"] = None
    CALLID_HISTORY.append(
        {
            "call_id": call_id,
            "change_type": "resume",
            "old_binding": binding.copy(),
            "new_binding": binding,
            "operator": current_user["user_id"],
            "reason": "Resume callId",
            "created_at": datetime.utcnow().isoformat() + "Z",
        },
    )
    return {"message": "callId resumed successfully"}


@router.get("/history", response_model=List[CallIdChangeRecordResponse])
async def get_callid_history(
    request: Request,
    call_id: str = Query(...),
    tenant_id: str = Query(...),
    limit: int = Query(50, ge=1, le=100),
) -> List[Dict[str, Any]]:
    """Get callId change history."""
    _get_current_user(request)
    history = [h for h in CALLID_HISTORY if h["call_id"] == call_id]
    history = sorted(history, key=lambda x: x["created_at"], reverse=True)[
        :limit
    ]
    return history
