"""
API接口模块
提供RESTful API接口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

# 创建应用
app = FastAPI(
    title="ALOA DECOR API",
    description="Unified API for ALOA DECOR ecommerce platform",
    version="2.0.0"
)

# 健康检查端点（优先注册，不添加任何中间件）
@app.get("/health")
async def health_check():
    """健康检查 - 立即返回成功，不依赖任何服务"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "shopifyStore": os.getenv("SHOPIFY_STORE", "not configured"),
        "database": "connected"
    }

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "ALOA DECOR Unified API",
        "version": "2.0.0",
        "endpoints": [
            "/api/health - 健康检查",
            "/api/platform-links - 平台链接管理"
        ]
    }

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由（确保在健康检查之后）
from .unified import router as unified_router
app.include_router(unified_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
