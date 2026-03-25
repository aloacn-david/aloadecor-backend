"""
平台链接服务
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..db.mongodb import get_collection
from ..models.shopify import PlatformLinks, PlatformLinksUpdate


class PlatformLinksService:
    """平台链接管理服务"""
    
    async def get_all_platform_links(self) -> List[Dict[str, Any]]:
        """获取所有产品的平台链接"""
        collection = get_collection("platform_links")
        cursor = collection.find().sort("updated_at", -1)
        results = await cursor.to_list(length=None)
        return results
    
    async def get_platform_links(self, product_id: str) -> Optional[Dict[str, Any]]:
        """获取单个产品的平台链接"""
        collection = get_collection("platform_links")
        result = await collection.find_one({"product_id": product_id})
        return result
    
    async def update_platform_links(
        self,
        product_id: str,
        updates: PlatformLinksUpdate
    ) -> Dict[str, Any]:
        """更新产品平台链接"""
        collection = get_collection("platform_links")
        existing = await self.get_platform_links(product_id)
        
        # 提取平台链接到顶层
        update_data = updates.platform_links.copy() if updates.platform_links else {}
        update_data["updated_at"] = datetime.now()
        if updates.updated_by:
            update_data["updated_by"] = updates.updated_by
        
        if existing:
            await collection.update_one(
                {"product_id": product_id},
                {"$set": update_data}
            )
        else:
            update_data["product_id"] = product_id
            update_data["created_at"] = datetime.now()
            await collection.insert_one(update_data)
        
        return await self.get_platform_links(product_id)
    
    async def batch_update_platform_links(
        self,
        updates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """批量更新平台链接"""
        results = []
        
        for item in updates:
            product_id = str(item.get("product_id"))
            if not product_id:
                continue
            
            update_data = {k: v for k, v in item.items() if k != "product_id"}
            update_obj = PlatformLinksUpdate(**update_data)
            
            result = await self.update_platform_links(product_id, update_obj)
            results.append(result)
        
        return results
    
    async def delete_platform_links(self, product_id: str) -> bool:
        """删除产品平台链接"""
        collection = get_collection("platform_links")
        result = await collection.delete_one({"product_id": product_id})
        return result.deleted_count > 0
