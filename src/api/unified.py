"""
统一API路由 - 整合所有功能
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime

from ..services.shopify_service import ShopifyService
from ..services.platform_links_service import PlatformLinksService
from ..services.content_service import ContentManagementService
from ..services.product_sync_service import ProductSyncService
from ..models.shopify import PlatformLinksUpdate, BulkPlatformLinksUpdate
from ..models.product_content import ContentStatusUpdate
from ..utils.monitoring import monitor_api, logger

router = APIRouter(prefix="/api", tags=["统一API"])

# Mock数据（当Shopify token未配置时使用）
MOCK_PRODUCTS = [
    {
        "id": 1,
        "title": "Modern Crystal Chandelier",
        "body_html": "Elegant crystal chandelier perfect for dining rooms",
        "vendor": "ALOA DECOR",
        "product_type": "Lighting",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "variants": [
            {
                "id": 101,
                "title": "Default",
                "price": "299.99",
                "sku": "CH-001",
                "position": 1,
                "inventory_quantity": 10,
                "weight": 5,
                "weight_unit": "lb"
            }
        ],
        "images": [
            {
                "id": 201,
                "src": "https://images.unsplash.com/photo-1565814329452-e1efa11c5b89?w=400",
                "position": 1,
                "alt": None
            }
        ],
        "tags": "chandelier,lighting,crystal"
    },
    {
        "id": 2,
        "title": "Vintage Table Lamp",
        "body_html": "Classic vintage style table lamp",
        "vendor": "ALOA DECOR",
        "product_type": "Lighting",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "variants": [
            {
                "id": 102,
                "title": "Default",
                "price": "89.99",
                "sku": "TL-002",
                "position": 1,
                "inventory_quantity": 25,
                "weight": 3,
                "weight_unit": "lb"
            }
        ],
        "images": [
            {
                "id": 202,
                "src": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400",
                "position": 1,
                "alt": None
            }
        ],
        "tags": "lamp,lighting,vintage"
    },
    {
        "id": 3,
        "title": "LED Floor Lamp",
        "body_html": "Modern LED floor lamp with adjustable brightness",
        "vendor": "ALOA DECOR",
        "product_type": "Lighting",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "variants": [
            {
                "id": 103,
                "title": "Default",
                "price": "149.99",
                "sku": "FL-003",
                "position": 1,
                "inventory_quantity": 15,
                "weight": 8,
                "weight_unit": "lb"
            }
        ],
        "images": [
            {
                "id": 203,
                "src": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=400",
                "position": 1,
                "alt": None
            }
        ],
        "tags": "lamp,lighting,led,floor"
    }
]

# 初始化服务
try:
    shopify_service = ShopifyService()
    logger.info("Shopify service initialized successfully")
except ValueError as e:
    logger.warning(f"Shopify service not initialized: {e}")
    shopify_service = None

platform_links_service = PlatformLinksService()
content_service = ContentManagementService()
product_sync_service = ProductSyncService()


@router.get("/shopify/products")
@monitor_api("shopify_products")
async def get_shopify_products():
    """获取Shopify产品列表"""
    try:
        if shopify_service:
            products = await shopify_service.fetch_products()
            platform_links = await platform_links_service.get_all_platform_links()
            
            # 创建平台链接字典以便快速查找
            links_dict = {str(link["product_id"]): link for link in platform_links}
            
            # 转换产品并添加平台链接
            result = []
            for product_data in products:
                transformed = shopify_service.transform_product(product_data)
                product_id = str(transformed["id"])
                
                if product_id in links_dict:
                    links = links_dict[product_id]
                    transformed["platformLinks"] = {
                        "amazon1": links.get("amazon1", ""),
                        "amazon2": links.get("amazon2", ""),
                        "wf1": links.get("wf1", ""),
                        "wf2": links.get("wf2", ""),
                        "os1": links.get("os1", ""),
                        "os2": links.get("os2", ""),
                        "hd1": links.get("hd1", ""),
                        "hd2": links.get("hd2", ""),
                        "lowes": links.get("lowes", ""),
                        "target": links.get("target", ""),
                        "walmart": links.get("walmart", ""),
                        "ebay": links.get("ebay", ""),
                        "kohls": links.get("kohls", "")
                    }
                
                result.append(transformed)
            
            logger.info(f"Fetched {len(result)} products from Shopify")
            return result
        else:
            logger.warning("Shopify service not available, returning mock data")
            # 使用mock数据
            result = []
            for product_data in MOCK_PRODUCTS:
                variants = []
                for v in product_data.get("variants", []):
                    variants.append({
                        "id": v.get("id"),
                        "title": v.get("title", ""),
                        "price": v.get("price", "0.00"),
                        "sku": v.get("sku", ""),
                        "position": v.get("position", 0),
                        "inventory_quantity": v.get("inventory_quantity", 0),
                        "weight": v.get("weight"),
                        "weight_unit": v.get("weight_unit")
                    })
                
                images = []
                for img in product_data.get("images", []):
                    images.append({
                        "id": img.get("id"),
                        "src": img.get("src", ""),
                        "position": img.get("position", 0),
                        "alt": img.get("alt")
                    })
                
                transformed = {
                    "id": product_data.get("id"),
                    "title": product_data.get("title", ""),
                    "body_html": product_data.get("body_html", ""),
                    "vendor": product_data.get("vendor", ""),
                    "product_type": product_data.get("product_type", ""),
                    "created_at": product_data.get("created_at"),
                    "updated_at": product_data.get("updated_at"),
                    "variants": variants,
                    "images": images,
                    "tags": product_data.get("tags", ""),
                    "platformLinks": {}
                }
                result.append(transformed)
            
            logger.info(f"Returning {len(result)} mock products")
            return result
        
    except Exception as e:
        logger.error(f"Error fetching Shopify products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shopify/products/{product_id}")
@monitor_api("shopify_product")
async def get_shopify_product(product_id: int):
    """获取单个Shopify产品"""
    if not shopify_service:
        raise HTTPException(status_code=503, detail="Shopify service not available")
    
    product = await shopify_service.fetch_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return shopify_service.transform_product(product)


@router.get("/platform-links")
@monitor_api("get_platform_links")
async def get_all_platform_links():
    """获取所有平台链接"""
    try:
        links = await platform_links_service.get_all_platform_links()
        return links
    except Exception as e:
        logger.error(f"Error getting platform links: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/platform-links/{product_id}")
@monitor_api("get_product_platform_links")
async def get_platform_links(product_id: str):
    """获取单个产品的平台链接"""
    try:
        links = await platform_links_service.get_platform_links(product_id)
        if not links:
            return {"product_id": product_id, "platformLinks": {}}
        return links
    except Exception as e:
        logger.error(f"Error getting platform links for {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/platform-links/{product_id}")
@monitor_api("update_platform_links")
async def update_platform_links(product_id: str, updates: PlatformLinksUpdate):
    """更新产品平台链接"""
    try:
        result = await platform_links_service.update_platform_links(product_id, updates)
        logger.info(f"Updated platform links for product {product_id}")
        return result
    except Exception as e:
        logger.error(f"Error updating platform links for {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/platform-links/bulk")
@monitor_api("batch_update_platform_links")
async def batch_update_platform_links(request: BulkPlatformLinksUpdate):
    """批量更新平台链接"""
    try:
        results = await platform_links_service.batch_update_platform_links(request.updates)
        logger.info(f"Batch updated {len(results)} products' platform links")
        return results
    except Exception as e:
        logger.error(f"Error batch updating platform links: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/platform-links/{product_id}")
@monitor_api("delete_platform_links")
async def delete_platform_links(product_id: str):
    """删除产品平台链接"""
    try:
        success = await platform_links_service.delete_platform_links(product_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error deleting platform links for {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/status")
@monitor_api("get_all_content_status")
async def get_all_content_status():
    """获取所有产品内容状态"""
    try:
        status = await content_service.get_all_content_status()
        return status
    except Exception as e:
        logger.error(f"Error getting content status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/status/{product_id}")
@monitor_api("get_product_content_status")
async def get_product_content_status(product_id: str):
    """获取单个产品内容状态"""
    try:
        status = await content_service.get_product_content_status(product_id)
        if not status:
            raise HTTPException(status_code=404, detail="Content status not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content status for {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content/status/{product_id}")
@monitor_api("update_content_status")
async def update_content_status(product_id: str, update: ContentStatusUpdate):
    """更新产品内容状态"""
    try:
        status = await content_service.create_or_update_content_status(
            product_id,
            update.status_updates,
            updated_by=update.updated_by
        )
        logger.info(f"Updated content status for product {product_id}")
        return status
    except Exception as e:
        logger.error(f"Error updating content status for {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/config/types")
@monitor_api("get_content_configs")
async def get_content_type_configs():
    """获取内容类型配置"""
    from ..models.product_content import CONTENT_TYPE_CONFIGS
    return CONTENT_TYPE_CONFIGS


@router.post("/content/batch")
@monitor_api("batch_update_content")
async def batch_update_content(updates: List[dict]):
    """批量更新内容状态"""
    try:
        results = []
        for item in updates:
            product_id = str(item.get("product_id"))
            status_updates = item.get("status_updates", {})
            updated_by = item.get("updated_by", "admin")
            
            result = await content_service.create_or_update_content_status(
                product_id, status_updates, updated_by=updated_by
            )
            results.append(result)
        
        logger.info(f"Batch updated {len(results)} products' content status")
        return results
    except Exception as e:
        logger.error(f"Error batch updating content status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/content/status/{product_id}")
@monitor_api("delete_content_status")
async def delete_content_status(product_id: str):
    """删除产品内容状态"""
    try:
        success = await content_service.delete_content_status(product_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error deleting content status for {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 统一产品API - 从数据库读取，不直接调用Shopify
# ============================================================================

@router.get("/products")
@monitor_api("get_products")
async def get_products():
    """获取所有产品（从数据库读取，包含基础数据+扩展数据）"""
    try:
        products = await product_sync_service.get_all_products()
        logger.info(f"Fetched {len(products)} products from database")
        return products
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}")
@monitor_api("get_product")
async def get_product(product_id: str):
    """获取单个产品（从数据库读取）"""
    try:
        product = await product_sync_service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products/sync")
@monitor_api("sync_products")
async def sync_products():
    """手动触发Shopify产品同步"""
    try:
        result = await product_sync_service.sync_products_from_shopify()
        return result
    except ValueError as e:
        logger.warning(f"Sync failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error syncing products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products/{product_id}/meta")
@monitor_api("update_product_meta")
async def update_product_meta(product_id: str, updates: Dict[str, Any]):
    """更新产品扩展数据"""
    try:
        meta = await product_sync_service.update_product_meta(product_id, updates)
        logger.info(f"Updated product meta for {product_id}")
        return meta
    except Exception as e:
        logger.error(f"Error updating product meta for {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))



