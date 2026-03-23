"""
API接口模块
提供RESTful API接口
"""
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from ..db.mongodb import connect_to_mongo, close_mongo_connection
from .unified import router as unified_router
from ..utils.monitoring import monitor_middleware, get_metrics

# 创建应用
app = FastAPI(
    title="ALOA DECOR API",
    description="Unified API for ALOA DECOR ecommerce platform",
    version="2.0.0"
)

# 添加监控中间件
app.middleware("http")(monitor_middleware)

# 注册路由
app.include_router(unified_router)

# 事件处理
@app.on_event("startup")
async def startup_event():
    """启动时连接MongoDB"""
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    """关闭时断开MongoDB连接"""
    await close_mongo_connection()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 简单的健康检查端点（不依赖MongoDB）
@app.get("/health")
async def health_check():
    """健康检查"""
    import os
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "shopifyStore": os.getenv("SHOPIFY_STORE", "not configured")
    }

@app.get("/metrics")
async def metrics():
    """Prometheus指标端点"""
    metrics_content, content_type = get_metrics()
    return Response(content=metrics_content, media_type=content_type)


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
