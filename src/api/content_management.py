"""
内容管理API接口
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from ..models.product_content import (
    ProductContentStatus,
    ContentStatusUpdate,
    BatchContentUpdate
)
from ..services.content_service import content_service

router = APIRouter(prefix="/api/content", tags=["content-management"])

@router.get("/status", response_model=List[ProductContentStatus])
async def get_all_content_status():
    """获取所有产品的内容状态"""
    try:
        return await content_service.get_all_content_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{product_id}", response_model=ProductContentStatus)
async def get_product_content_status(product_id: str):
    """获取单个产品的内容状态"""
    try:
        status = await content_service.get_product_content_status(product_id)
        if not status:
            raise HTTPException(status_code=404, detail="Product content status not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/status/{product_id}", response_model=ProductContentStatus)
async def update_product_content_status(
    product_id: str, 
    request: ContentStatusUpdate
):
    """更新产品的内容状态"""
    try:
        return await content_service.create_or_update_content_status(
            product_id,
            request.status_updates,
            updated_by=request.updated_by
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=List[ProductContentStatus])
async def batch_update_content_status(request: BatchContentUpdate):
    """批量更新内容状态"""
    try:
        return await content_service.batch_update_content_status(
            request.updates,
            updated_by=request.updated_by
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config/types", response_model=List[Dict[str, Any]])
async def get_content_type_configs():
    """获取内容类型配置"""
    try:
        return await content_service.get_content_type_configs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/status/{product_id}", response_model=Dict[str, bool])
async def delete_content_status(product_id: str):
    """删除产品内容状态"""
    try:
        success = await content_service.delete_content_status(product_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync/shopify", response_model=ProductContentStatus)
async def sync_single_product(product_data: Dict):
    """同步单个Shopify产品"""
    try:
        return await content_service.sync_product_from_shopify(product_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
