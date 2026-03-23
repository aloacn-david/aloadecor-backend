"""
Shopify API服务类
"""
import os
import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.shopify import ShopifyProduct, ShopifyVariant, ShopifyImage


class ShopifyService:
    """Shopify API服务"""
    
    def __init__(self):
        self.store_url = os.getenv("SHOPIFY_STORE")
        self.api_token = os.getenv("SHOPIFY_TOKEN")
        self.timeout = int(os.getenv("API_TIMEOUT", 30))
        
        if not self.store_url or not self.api_token:
            raise ValueError("SHOPIFY_STORE and SHOPIFY_TOKEN environment variables are required")
        
        self.base_url = f"https://{self.store_url}/admin/api/2024-01"
        self.headers = {
            "X-Shopify-Access-Token": self.api_token,
            "Content-Type": "application/json"
        }
    
    async def fetch_products(self, limit: int = 250) -> List[Dict[str, Any]]:
        """
        获取Shopify产品列表
        
        Args:
            limit: 每页产品数量
            
        Returns:
            产品列表
        """
        products = []
        url = f"{self.base_url}/products.json"
        params = {"limit": limit}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while url:
                try:
                    response = await client.get(
                        url,
                        headers=self.headers,
                        params=params if not products else {}
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    products.extend(data.get("products", []))
                    
                    # 获取下一页链接
                    link_header = response.headers.get("Link", "")
                    if 'rel="next"' in link_header:
                        next_link = link_header.split('; rel="next"')[0].strip('<>')
                        url = next_link
                        params = {}
                    else:
                        url = None
                        
                except httpx.HTTPError as e:
                    print(f"Error fetching Shopify products: {e}")
                    break
        
        return products
    
    async def fetch_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        获取单个产品
        
        Args:
            product_id: Shopify产品ID
            
        Returns:
            产品数据
        """
        url = f"{self.base_url}/products/{product_id}.json"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                return data.get("product")
        except httpx.HTTPError as e:
            print(f"Error fetching product {product_id}: {e}")
            return None
    
    def transform_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换Shopify产品数据为前端可用格式
        
        Args:
            product_data: Shopify原始产品数据
            
        Returns:
            转换后的产品数据
        """
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
        
        return {
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
