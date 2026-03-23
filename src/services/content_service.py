"""
产品内容管理服务
"""
from datetime import datetime
from typing import List, Dict, Optional
from bson.objectid import ObjectId

from ..db.mongodb import get_collection
from ..models.product_content import (
    ProductContentStatus,
    ContentType,
    create_initial_status,
    CONTENT_TYPE_CONFIGS
)

class ContentManagementService:
    """内容管理服务类"""
    
    def __init__(self):
        self.collection = get_collection("product_content_status")
        self.total_content_types = len(CONTENT_TYPE_CONFIGS)
    
    async def get_all_content_status(self) -> List[ProductContentStatus]:
        """获取所有产品的内容状态"""
        if not self.collection:
            return []
        
        cursor = self.collection.find().sort("updated_at", -1)
        results = await cursor.to_list(length=None)
        
        return [ProductContentStatus(**result) for result in results]
    
    async def get_product_content_status(self, product_id: str) -> Optional[ProductContentStatus]:
        """获取单个产品的内容状态"""
        if not self.collection:
            return None
        
        result = await self.collection.find_one({"product_id": product_id})
        if result:
            return ProductContentStatus(**result)
        return None
    
    async def create_or_update_content_status(
        self, 
        product_id: str, 
        status_updates: Dict[ContentType, bool],
        sku: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> ProductContentStatus:
        """创建或更新产品内容状态"""
        if not self.collection:
            raise Exception("Database not connected")
        
        # 检查产品是否已存在
        existing = await self.get_product_content_status(product_id)
        
        if existing:
            # 更新现有状态
            updated_status = {**existing.status, **status_updates}
            
            # 计算完成数量和完成率
            completed_count = sum(1 for v in updated_status.values() if v)
            completion_rate = round((completed_count / self.total_content_types) * 100, 2)
            
            update_data = {
                "status": updated_status,
                "completed_count": completed_count,
                "completion_rate": completion_rate,
                "updated_at": datetime.now(),
            }
            
            if sku:
                update_data["sku"] = sku
            if updated_by:
                update_data["updated_by"] = updated_by
            
            await self.collection.update_one(
                {"product_id": product_id},
                {"$set": update_data}
            )
            
            # 返回更新后的对象
            return await self.get_product_content_status(product_id)
        else:
            # 创建新状态
            initial_status = create_initial_status()
            updated_status = {**initial_status, **status_updates}
            
            completed_count = sum(1 for v in updated_status.values() if v)
            completion_rate = round((completed_count / self.total_content_types) * 100, 2)
            
            status_obj = ProductContentStatus(
                product_id=product_id,
                sku=sku,
                status=updated_status,
                completed_count=completed_count,
                completion_rate=completion_rate,
                updated_by=updated_by
            )
            
            result = await self.collection.insert_one(status_obj.dict())
            status_obj.id = result.inserted_id
            
            return status_obj
    
    async def batch_update_content_status(
        self, 
        updates: List[Dict],
        updated_by: Optional[str] = None
    ) -> List[ProductContentStatus]:
        """批量更新内容状态"""
        results = []
        for update in updates:
            product_id = update.get("product_id")
            status_updates = update.get("status_updates", {})
            sku = update.get("sku")
            
            if product_id:
                result = await self.create_or_update_content_status(
                    product_id, 
                    status_updates, 
                    sku, 
                    updated_by
                )
                results.append(result)
        
        return results
    
    async def sync_product_from_shopify(self, product_data: Dict) -> ProductContentStatus:
        """从Shopify同步产品，创建初始状态"""
        product_id = str(product_data.get("id"))
        sku = product_data.get("variants", [{}])[0].get("sku")
        
        # 检查是否已存在
        existing = await self.get_product_content_status(product_id)
        if existing:
            # 更新SKU（如果有变化）
            if existing.sku != sku:
                await self.collection.update_one(
                    {"product_id": product_id},
                    {"$set": {"sku": sku, "updated_at": datetime.now()}}
                )
                return await self.get_product_content_status(product_id)
            return existing
        
        # 创建初始状态
        initial_status = create_initial_status()
        status_obj = ProductContentStatus(
            product_id=product_id,
            sku=sku,
            status=initial_status,
            completed_count=0,
            completion_rate=0.0
        )
        
        await self.collection.insert_one(status_obj.dict())
        return status_obj
    
    async def delete_content_status(self, product_id: str) -> bool:
        """删除产品内容状态"""
        if not self.collection:
            return False
        
        result = await self.collection.delete_one({"product_id": product_id})
        return result.deleted_count > 0
    
    async def get_content_type_configs(self):
        """获取内容类型配置"""
        return [config.dict() for config in CONTENT_TYPE_CONFIGS]

# 全局服务实例
content_service = ContentManagementService()
