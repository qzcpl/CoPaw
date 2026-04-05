"""
灰度发布 API
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime

from ..schemas.gray_release import (
    GrayReleaseConfigResponse,
    GrayReleaseCreateRequest,
    GrayReleaseUpdateRequest,
    GrayReleaseMetricsResponse,
)
from ..core.exceptions import ApiError, ApiErrorCode
from ..dependencies import get_current_user

router = APIRouter()

# 模拟灰度发布数据库
GRAY_RELEASES_DB = {}


@router.get("", response_model=List[GrayReleaseConfigResponse])
async def list_gray_releases(
    call_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    列出灰度发布
    
    Args:
        call_id: callId
        status: 状态
        current_user: 当前用户
    
    Returns:
        灰度发布列表
    """
    releases = list(GRAY_RELEASES_DB.values())
    
    # 过滤
    if call_id:
        releases = [r for r in releases if r["call_id"] == call_id]
    if status:
        releases = [r for r in releases if r["status"] == status]
    
    return releases


@router.get("/{release_id}", response_model=GrayReleaseConfigResponse)
async def get_gray_release(
    release_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    查询灰度发布详情
    
    Args:
        release_id: 发布 ID
        current_user: 当前用户
    
    Returns:
        灰度发布详情
    """
    release = GRAY_RELEASES_DB.get(release_id)
    
    if not release:
        raise ApiError(
            code=ApiErrorCode.NOT_FOUND,
            message=f"Gray release not found: {release_id}",
            status_code=404,
        )
    
    return release


@router.post("", response_model=GrayReleaseConfigResponse)
async def create_gray_release(
    request: GrayReleaseCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    创建灰度发布
    
    Args:
        request: 创建请求
        current_user: 当前用户
    
    Returns:
        创建的灰度发布
    """
    # 权限检查
    if current_user["role"] not in ["tenant_admin", "system_admin"]:
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only tenant admin can create gray release",
            status_code=403,
        )
    
    release_id = f"release_{request.release_name}_{int(datetime.utcnow().timestamp())}"
    
    release = {
        "release_id": release_id,
        "release_name": request.release_name,
        "call_id": request.call_id,
        "target_agent_id": request.target_agent_id,
        "traffic_percentage": request.traffic_percentage,
        "status": "active",
        "started_at": datetime.utcnow().isoformat() + "Z",
        "completed_at": None,
        "config": request.config or {},
    }
    
    GRAY_RELEASES_DB[release_id] = release
    
    return release


@router.put("/{release_id}", response_model=GrayReleaseConfigResponse)
async def update_gray_release(
    release_id: str,
    request: GrayReleaseUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    更新灰度发布
    
    Args:
        release_id: 发布 ID
        request: 更新请求
        current_user: 当前用户
    
    Returns:
        更新后的灰度发布
    """
    release = GRAY_RELEASES_DB.get(release_id)
    
    if not release:
        raise ApiError(
            code=ApiErrorCode.NOT_FOUND,
            message=f"Gray release not found: {release_id}",
            status_code=404,
        )
    
    # 更新字段
    if request.traffic_percentage is not None:
        release["traffic_percentage"] = request.traffic_percentage
    if request.status:
        release["status"] = request.status
        if request.status in ["completed", "rolled_back"]:
            release["completed_at"] = datetime.utcnow().isoformat() + "Z"
    
    release["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    return release


@router.delete("/{release_id}")
async def delete_gray_release(
    release_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    删除灰度发布
    
    Args:
        release_id: 发布 ID
        current_user: 当前用户
    """
    release = GRAY_RELEASES_DB.get(release_id)
    
    if not release:
        raise ApiError(
            code=ApiErrorCode.NOT_FOUND,
            message=f"Gray release not found: {release_id}",
            status_code=404,
        )
    
    # 权限检查
    if current_user["role"] not in ["tenant_admin", "system_admin"]:
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only tenant admin can delete gray release",
            status_code=403,
        )
    
    del GRAY_RELEASES_DB[release_id]
    
    return {"message": "Gray release deleted successfully"}


@router.get("/{release_id}/metrics", response_model=GrayReleaseMetricsResponse)
async def get_gray_release_metrics(
    release_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    查询灰度发布指标
    
    Args:
        release_id: 发布 ID
        current_user: 当前用户
    
    Returns:
        灰度发布指标
    """
    release = GRAY_RELEASES_DB.get(release_id)
    
    if not release:
        raise ApiError(
            code=ApiErrorCode.NOT_FOUND,
            message=f"Gray release not found: {release_id}",
            status_code=404,
        )
    
    # TODO: 实现真实指标查询
    return GrayReleaseMetricsResponse(
        release_id=release_id,
        total_requests=0,
        target_agent_requests=0,
        original_agent_requests=0,
        error_rate=0.0,
        avg_latency_ms=0.0,
        rollback_count=0,
    )
