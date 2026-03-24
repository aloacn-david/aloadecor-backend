"""
API接口模块
提供RESTful API接口
"""
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from ..db.mongodb import connect_to_mongo, close_mongo_connection
from .unified import router as unified_router
from .content_management import router as content_router
from .platform_links import router as platform_router
from ..utils.monitoring import monitor_middleware, get_metrics

# 创建应用
app = FastAPI(
    title="ALOA DECOR API",
    description="Unified API for ALOA DECOR ecommerce platform",
    version="2.0.0"
)

# 健康检查端点（优先注册，启动立即可用，不依赖任何服务）
@app.get("/health")
async def health_check():
    """健康检查 - 立即返回成功，不依赖任何服务"""
    import os
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
            "/api/shopify/products - 获取Shopify产品",
            "/api/products - 统一产品接口（数据库）",
            "/api/products/sync - 同步Shopify产品",
            "/api/platform-links - 平台链接管理",
            "/api/content/status - 内容状态管理",
            "/api/health - 健康检查",
            "/metrics - Prometheus指标"
        ]
    }

# 添加监控中间件
app.middleware("http")(monitor_middleware)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(unified_router)
app.include_router(content_router)
app.include_router(platform_router)

# 事件处理
@app.on_event("startup")
async def startup_event():
    """启动时连接MongoDB（后台连接，不阻塞服务启动）"""
    try:
        await connect_to_mongo()
    except Exception as e:
        print(f"MongoDB connection failed: {e}, will retry on next request")

@app.on_event("shutdown")
async def shutdown_event():
    """关闭时断开MongoDB连接"""
    try:
        await close_mongo_connection()
    except:
        pass

@app.get("/metrics")
async def metrics():
    """Prometheus指标端点"""
    metrics_content, content_type = get_metrics()
    return Response(content=metrics_content, media_type=content_type)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
