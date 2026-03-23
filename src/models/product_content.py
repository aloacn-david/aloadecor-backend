"""
产品内容管理数据模型
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from enum import Enum

# 内容类型枚举
class ContentType(str, Enum):
    ALL_US_JC = "全美国杰西"
    PRICE_LIST = "全计价表"
    PRODUCT_SHEET = "新品product sheet"
    RESEARCH = "新品调研"
    PRICE_VERIFY = "上传价核价"
    MAIN_IMAGE = "主图"
    WHITE_IMAGE = "白底图"
    DETAIL_IMAGE = "细节图"
    SIZE_IMAGE = "尺寸图"
    INSTALL_VIDEO = "安装视频"
    SCENE_VIDEO = "场景视频/网红视频"
    TEXT_CONTENT = "文字"
    LAUNCHED = "新品上架"

# 内容类型配置
class ContentTypeConfig(BaseModel):
    type: ContentType
    label: str
    icon: str
    color: str
    order: int

# 内容状态模型
class ProductContentStatus(BaseModel):
    product_id: str = Field(description="关联产品ID，与Shopify产品ID一致")
    sku: Optional[str] = Field(None, description="产品SKU")
    status: Dict[ContentType, bool] = Field(description="各内容类型状态")
    completed_count: int = Field(0, description="已完成数量")
    completion_rate: float = Field(0.0, description="完成率 0-100%")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: Optional[str] = Field(None, description="更新人")

    model_config = {
        "arbitrary_types_allowed": True
    }

# 更新请求
class ContentStatusUpdate(BaseModel):
    status_updates: Dict[ContentType, bool]
    updated_by: Optional[str] = None

# 批量更新请求
class BatchContentUpdate(BaseModel):
    updates: List[Dict]
    updated_by: Optional[str] = None

# 内容类型配置列表
CONTENT_TYPE_CONFIGS: List[ContentTypeConfig] = [
    ContentTypeConfig(type=ContentType.ALL_US_JC, label="全美国杰西", icon="🇺🇸", color="#4CAF50", order=1),
    ContentTypeConfig(type=ContentType.PRICE_LIST, label="全计价表", icon="📊", color="#2196F3", order=2),
    ContentTypeConfig(type=ContentType.PRODUCT_SHEET, label="新品product sheet", icon="📋", color="#FF9800", order=3),
    ContentTypeConfig(type=ContentType.RESEARCH, label="新品调研", icon="🔍", color="#9C27B0", order=4),
    ContentTypeConfig(type=ContentType.PRICE_VERIFY, label="上传价核价", icon="💰", color="#F44336", order=5),
    ContentTypeConfig(type=ContentType.MAIN_IMAGE, label="主图", icon="🖼️", color="#00BCD4", order=6),
    ContentTypeConfig(type=ContentType.WHITE_IMAGE, label="白底图", icon="⬜", color="#795548", order=7),
    ContentTypeConfig(type=ContentType.DETAIL_IMAGE, label="细节图", icon="🔍", color="#607D8B", order=8),
    ContentTypeConfig(type=ContentType.SIZE_IMAGE, label="尺寸图", icon="📏", color="#3F51B5", order=9),
    ContentTypeConfig(type=ContentType.INSTALL_VIDEO, label="安装视频", icon="🎬", color="#E91E63", order=10),
    ContentTypeConfig(type=ContentType.SCENE_VIDEO, label="场景视频/网红视频", icon="🎥", color="#FF5722", order=11),
    ContentTypeConfig(type=ContentType.TEXT_CONTENT, label="文字", icon="📝", color="#8BC34A", order=12),
    ContentTypeConfig(type=ContentType.LAUNCHED, label="新品上架", icon="✅", color="#4CAF50", order=13),
]

# 创建初始状态模板
def create_initial_status() -> Dict[ContentType, bool]:
    return {content_type.type: False for content_type in CONTENT_TYPE_CONFIGS}
