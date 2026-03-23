"""
最简单的API - 用于测试部署
"""
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="ALOA DECOR Simple API",
    description="Minimal API for deployment testing",
    version="1.0.0"
)

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "ALOA DECOR API is running!",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test")
async def test():
    """测试端点"""
    return {"status": "ok", "message": "API is working correctly"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
