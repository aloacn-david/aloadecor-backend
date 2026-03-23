"""
产品同步服务 - 统一产品数据管理
Shopify只作为同步源，所有数据从本地数据库读取
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.product import Product, ProductMeta, ProductWithMeta, ProductVariant, ProductImage
from ..services.shopify_service import ShopifyService
from ..db.mongodb import get_collection
from ..utils.monitoring import logger


class ProductSyncService:
    """产品同步服务"""
    
    def __init__(self):
        self.shopify_service = None
        try:
            self.shopify_service = ShopifyService()
            logger.info("Shopify service initialized for product sync")
        except ValueError as e:
            logger.warning(f"Shopify service not initialized: {e}")
    
    async def sync_products_from_shopify(self) -> Dict[str, Any]:
        """
        从Shopify同步产品数据到本地数据库
        
        Returns:
            同步结果统计
        """
        if not self.shopify_service:
            raise ValueError("Shopify service not available")
        
        logger.info("Starting product sync from Shopify...")
        
        # 获取Shopify产品
        shopify_products = await self.shopify_service.fetch_products()
        
        products_collection = get_collection("products")
        if not products_collection:
            raise ValueError("Database not connected")
        
        synced_count = 0
        updated_count = 0
        created_count = 0
        
        for shopify_product in shopify_products:
            shopify_id = shopify_product.get("id")
            
            # 转换Shopify产品为本地格式
            product_data = self._transform_shopify_product(shopify_product)
            
            # 检查是否已存在
            existing = await products_collection.find_one({"shopify_product_id": shopify_id})
            
            if existing:
                # 更新现有产品
                product_data["updated_at"] = datetime.now()
                product_data["_id"] = existing["_id"]
                await products_collection.replace_one(
                    {"shopify_product_id": shopify_id},
                    product_data
                )
                updated_count += 1
            else:
                # 创建新产品
                await products_collection.insert_one(product_data)
                created_count += 1
            
            synced_count += 1
        
        result = {
            "synced_count": synced_count,
            "created_count": created_count,
            "updated_count": updated_count,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Product sync completed: {result}")
        return result
    
    def _transform_shopify_product(self, shopify_product: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换Shopify产品为本地产品格式
        
        Args:
            shopify_product: Shopify原始产品数据
            
        Returns:
            本地产品数据
        """
        # 转换变体
        variants = []
        for v in shopify_product.get("variants", []):
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
        
        # 转换图片
        images = []
        for img in shopify_product.get("images", []):
            images.append({
                "id": img.get("id"),
                "src": img.get("src", ""),
                "position": img.get("position", 0),
                "alt": img.get("alt")
            })
        
        # 获取第一个变体的SKU和价格
        first_variant = shopify_product.get("variants", [{}])[0]
        
        return {
            "shopify_product_id": shopify_product.get("id"),
            "title": shopify_product.get("title", ""),
            "handle": shopify_product.get("handle"),
            "sku": first_variant.get("sku"),
            "price": first_variant.get("price"),
            "images": images,
            "variants": variants,
            "inventory": first_variant.get("inventory_quantity"),
            "status": shopify_product.get("status"),
            "body_html": shopify_product.get("body_html"),
            "vendor": shopify_product.get("vendor"),
            "product_type": shopify_product.get("product_type"),
            "tags": shopify_product.get("tags"),
            "shopify_created_at": shopify_product.get("created_at"),
            "shopify_updated_at": shopify_product.get("updated_at"),
            "synced_at": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    
    async def get_all_products(self) -> List[Dict[str, Any]]:
        """
        获取所有产品（从数据库读取）
        
        Returns:
            产品列表（包含基础数据+扩展数据）
        """
        products_collection = get_collection("products")
        product_meta_collection = get_collection("product_meta")
        
        if not products_collection or not product_meta_collection:
            raise ValueError("Database not connected")
        
        # 获取所有产品
        products_cursor = products_collection.find({})
        products = await products_cursor.to_list(length=None)
        
        # 获取所有product_meta
        meta_cursor = product_meta_collection.find({})
        metas = await meta_cursor.to_list(length=None)
        
        # 创建meta字典
        meta_dict = {meta["product_id"]: meta for meta in metas}
        
        # 合并数据
        result = []
        for product in products:
            product_id = str(product["shopify_product_id"])
            meta = meta_dict.get(product_id, {})
            
            merged = self._merge_product_with_meta(product, meta)
            result.append(merged)
        
        return result
    
    async def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个产品（从数据库读取）
        
        Args:
            product_id: Shopify产品ID
            
        Returns:
            产品数据（包含基础数据+扩展数据）
        """
        products_collection = get_collection("products")
        product_meta_collection = get_collection("product_meta")
        
        if not products_collection or not product_meta_collection:
            raise ValueError("Database not connected")
        
        # 获取产品
        product = await products_collection.find_one({"shopify_product_id": int(product_id)})
        if not product:
            return None
        
        # 获取product_meta
        meta = await product_meta_collection.find_one({"product_id": product_id})
        
        # 合并数据
        merged = self._merge_product_with_meta(product, meta or {})
        return merged
    
    def _merge_product_with_meta(self, product: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并产品基础数据和扩展数据
        
        Args:
            product: 产品基础数据
            meta: 产品扩展数据
            
        Returns:
            合并后的产品数据
        """
        return {
            # 基础数据
            "id": product["shopify_product_id"],
            "shopify_product_id": product["shopify_product_id"],
            "title": product["title"],
            "handle": product.get("handle"),
            "sku": product.get("sku"),
            "price": product.get("price"),
            "images": product.get("images", []),
            "variants": product.get("variants", []),
            "inventory": product.get("inventory"),
            "status": product.get("status"),
            "body_html": product.get("body_html"),
            "vendor": product.get("vendor"),
            "product_type": product.get("product_type"),
            "tags": product.get("tags"),
            
            # 平台链接
            "platformLinks": {
                "amazon1": meta.get("amazon1"),
                "amazon2": meta.get("amazon2"),
                "wf1": meta.get("wf1"),
                "wf2": meta.get("wf2"),
                "os1": meta.get("os1"),
                "os2": meta.get("os2"),
                "hd1": meta.get("hd1"),
                "hd2": meta.get("hd2"),
                "lowes": meta.get("lowes"),
                "target": meta.get("target"),
                "walmart": meta.get("walmart"),
                "ebay": meta.get("ebay"),
                "kohls": meta.get("kohls")
            },
            
            # 扩展数据
            "content_description": meta.get("content_description"),
            "content_copy": meta.get("content_copy"),
            "internal_notes": meta.get("internal_notes"),
            "meta_status": meta.get("status"),
            "product_category": meta.get("product_category"),
            "meta_tags": meta.get("tags", [])
        }
    
    async def update_product_meta(self, product_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新产品扩展数据
        
        Args:
            product_id: 产品ID
            updates: 更新数据
            
        Returns:
            更新后的product_meta
        """
        product_meta_collection = get_collection("product_meta")
        if not product_meta_collection:
            raise ValueError("Database not connected")
        
        updates["updated_at"] = datetime.now()
        
        # 更新或创建
        result = await product_meta_collection.update_one(
            {"product_id": product_id},
            {"$set": updates},
            upsert=True
        )
        
        # 获取更新后的数据
        meta = await product_meta_collection.find_one({"product_id": product_id})
        return meta
