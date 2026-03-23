"""
Shopify产品数据模型
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ShopifyVariant(BaseModel):
    """Shopify产品变体"""
    id: int
    title: str
    price: str
    sku: Optional[str] = None
    position: int
    inventory_quantity: int
    weight: Optional[float] = None
    weight_unit: Optional[str] = None


class ShopifyImage(BaseModel):
    """Shopify产品图片"""
    id: int
    src: str
    position: int
    alt: Optional[str] = None


class ShopifyProduct(BaseModel):
    """Shopify产品"""
    id: int
    title: str
    body_html: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    variants: List[ShopifyVariant] = []
    images: List[ShopifyImage] = []
    tags: Optional[str] = None
    
    model_config = {
        "arbitrary_types_allowed": True
    }


class PlatformLinks(BaseModel):
    """平台链接模型"""
    product_id: str = Field(..., description="Shopify产品ID")
    amazon1: Optional[str] = None
    amazon2: Optional[str] = None
    wf1: Optional[str] = None
    wf2: Optional[str] = None
    os1: Optional[str] = None
    os2: Optional[str] = None
    hd1: Optional[str] = None
    hd2: Optional[str] = None
    lowes: Optional[str] = None
    target: Optional[str] = None
    walmart: Optional[str] = None
    ebay: Optional[str] = None
    kohls: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    model_config = {
        "arbitrary_types_allowed": True
    }


class PlatformLinksUpdate(BaseModel):
    """平台链接更新请求"""
    amazon1: Optional[str] = None
    amazon2: Optional[str] = None
    wf1: Optional[str] = None
    wf2: Optional[str] = None
    os1: Optional[str] = None
    os2: Optional[str] = None
    hd1: Optional[str] = None
    hd2: Optional[str] = None
    lowes: Optional[str] = None
    target: Optional[str] = None
    walmart: Optional[str] = None
    ebay: Optional[str] = None
    kohls: Optional[str] = None


class BulkPlatformLinksUpdate(BaseModel):
    """批量平台链接更新"""
    updates: List[Dict[str, Any]]
