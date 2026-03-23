# ALOA DECOR 统一后端部署指南

## 概述

本统一后端整合了以下功能：
- Shopify产品同步
- 平台链接管理
- 产品内容状态管理
- AI分析功能
- Prometheus监控

## 技术栈

- **Web框架**: FastAPI
- **数据库**: MongoDB (MongoDB Atlas)
- **异步客户端**: Motor
- **HTTP客户端**: httpx
- **监控**: Prometheus
- **日志**: Python logging

## 本地开发

### 1. 环境配置

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入真实配置：

```env
# Shopify API配置
SHOPIFY_STORE=your-shop-name.myshopify.com
SHOPIFY_TOKEN=your-shopify-api-token

# MongoDB配置
MONGODB_URI=mongodb://localhost:27017/aloadecor

# API配置
API_TIMEOUT=30

# OpenAI API配置（可选）
OPENAI_API_KEY=your-openai-api-key
```

### 2. 安装依赖

```bash
cd ai-analyzer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 启动服务

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

访问 API 文档：http://localhost:8000/docs

## 部署到 Railway

### 1. 创建新项目

1. 访问 [Railway](https://railway.app)
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择您的仓库

### 2. 配置环境变量

在 Railway 项目设置中添加以下环境变量：

```
SHOPIFY_STORE=your-shop-name.myshopify.com
SHOPIFY_TOKEN=your-shopify-api-token
MONGODB_URI=mongodb+srv://...
API_TIMEOUT=30
OPENAI_API_KEY=your-openai-api-key (可选)
```

### 3. 配置 MongoDB

如果需要，可以使用 Railway 提供的 MongoDB：

1. 在项目中点击 "Add Service"
2. 选择 "MongoDB"
3. Railway 会自动配置 `MONGO_URL` 环境变量
4. 修改代码使用 `MONGO_URL` 或在 `MONGODB_URI` 中使用相同的值

### 4. 配置构建和启动命令

在 Railway 服务设置中配置：

- **Build Command**: (留空，使用默认)
- **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

### 5. 部署

Railway 会自动在每次推送到 main 分支时部署。

## API 端点

### 产品相关

- `GET /api/shopify/products` - 获取所有Shopify产品
- `GET /api/shopify/products/{product_id}` - 获取单个产品

### 平台链接

- `GET /api/platform-links` - 获取所有平台链接
- `GET /api/platform-links/{product_id}` - 获取单个产品的平台链接
- `POST /api/platform-links/{product_id}` - 更新产品平台链接
- `POST /api/platform-links/bulk` - 批量更新平台链接
- `DELETE /api/platform-links/{product_id}` - 删除产品平台链接

### 内容状态

- `GET /api/content/status` - 获取所有产品内容状态
- `GET /api/content/status/{product_id}` - 获取单个产品内容状态
- `POST /api/content/status/{product_id}` - 更新产品内容状态
- `GET /api/content/config/types` - 获取内容类型配置
- `POST /api/content/batch` - 批量更新内容状态
- `DELETE /api/content/status/{product_id}` - 删除产品内容状态

### 监控

- `GET /metrics` - Prometheus指标
- `GET /health` - 健康检查

## 监控

### Prometheus 指标

可用的指标：

- `api_requests_total` - 总请求数
- `api_request_duration_seconds` - 请求耗时分布
- `api_active_requests` - 当前活跃请求数
- `api_errors_total` - 错误总数

### 日志

所有API请求都会记录到标准输出，包含：
- 请求时间
- 端点
- 方法
- 状态码
- 耗时
- 错误信息

## 健康检查

访问 `/health` 端点检查服务状态：

```json
{
  "status": "healthy",
  "timestamp": "2026-03-17T10:30:00.000000",
  "services": {
    "shopify": "available",
    "platform_links": "available",
    "content_management": "available"
  }
}
```

## 故障排查

### Shopify API 失败

检查：
1. `SHOPIFY_STORE` 和 `SHOPIFY_TOKEN` 配置正确
2. Shopify API 密钥权限正确
3. 网络连接正常

### MongoDB 连接失败

检查：
1. `MONGODB_URI` 配置正确
2. MongoDB 服务运行正常
3. 防火墙允许连接

### API 请求超时

增加 `API_TIMEOUT` 环境变量的值（单位：秒）

## 更新记录

### v3.0.0 (2026-03-17)
- 统一后端架构
- 整合Shopify产品同步
- 整合平台链接管理
- 整合内容状态管理
- 添加Prometheus监控
- 添加结构化日志
