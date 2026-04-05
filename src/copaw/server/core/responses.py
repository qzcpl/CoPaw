"""
统一响应格式
"""
from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""
    
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    code: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int = 1,
        page_size: int = 20,
    ) -> "PaginatedResponse[T]":
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
