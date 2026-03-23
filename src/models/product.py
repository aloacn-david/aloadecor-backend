"""
产品数据模型 - 统一产品数据结构
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ProductVariant(BaseModel):
    """产品变体"""
    id: int
    title: str
    price: str
    sku: Optional[str] = None
    position: int
    inventory_quantity: int
    weight: Optional[float] = None
    weight_unit: Optional[str] = None
    
    model_config = {
        "arbitrary_types_allowed": True
    }


class ProductImage(BaseModel):
    """产品图片"""
    id: int
    src: str
    position: int
    alt: Optional[str] = None
    
    model_config = {
        "arbitrary_types_allowed": True
    }


class Product(BaseModel):
    """产品基础数据（来自Shopify）"""
    shopify_product_id: int = Field(..., description="Shopify产品ID")
    title: str
    handle: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[str] = None
    images: List[ProductImage] = []
    variants: List[ProductVariant] = []
    inventory: Optional[int] = None
    status: Optional[str] = None
    body_html: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    tags: Optional[str] = None
    shopify_created_at: Optional[datetime] = None
    shopify_updated_at: Optional[datetime] = None
    synced_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    model_config = {
        "arbitrary_types_allowed": True
    }


class ProductMeta(BaseModel):
    """产品扩展数据（后台维护）"""
    product_id: str = Field(..., description="关联产品ID（shopify_product_id的字符串形式）")
    
    # 平台链接
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
    
    # 产品内容
    content_description: Optional[str] = None
    content_copy: Optional[str] = None
    
    # 内部备注
    internal_notes: Optional[str] = None
    
    # 状态
    status: Optional[str] = Field(None, description="未完成/审核中/已上线")
    
    # 产品分类
    product_category: Optional[str] = Field(None, description="标品/半标品/非标品")
    
    # 标签
    tags: List[str] = []
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    model_config = {
        "arbitrary_types_allowed": True
    }


class ProductWithMeta(BaseModel):
    """产品数据（基础数据+扩展数据合并）"""
    # 基础数据
    shopify_product_id: int
    title: str
    handle: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[str] = None
    images: List[ProductImage] = []
    variants: List[ProductVariant] = []
    inventory: Optional[int] = None
    status: Optional[str] = None
    body_html: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    tags: Optional[str] = None
    
    # 平台链接
    platformLinks: Dict[str, Optional[str]] = {}
    
    # 扩展数据
    content_description: Optional[str] = None
    content_copy: Optional[str] = None
    internal_notes: Optional[str] = None
    meta_status: Optional[str] = None
    product_category: Optional[str] = None
    meta_tags: List[str] = []
    
    model_config = {
        "arbitrary_types_allowed": True
    }
