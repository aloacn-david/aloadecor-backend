# AloaDecor Backend

这是一个用于 AloaDecor 网站的 Shopify API 代理服务器。

## 功能

- 代理前端对 Shopify API 的请求
- 处理跨域问题 (CORS)
- 分页获取所有 Shopify 产品
- 产品数据处理和分类

## 环境变量

- `SHOPIFY_STORE`: Shopify 商店域名 (例如: your-store.myshopify.com)
- `SHOPIFY_TOKEN`: Shopify 访问令牌

## API 端点

- `GET /health`: 服务器健康检查
- `GET /api/shopify/products`: 获取所有产品
- `GET /api/shopify/categories`: 获取所有分类

## 部署到 Railway

1. 在 Railway 上创建新项目
2. 连接到 GitHub 存储库或直接上传代码
3. 设置环境变量
4. 部署应用

## 部署到其他平台

此应用也可以部署到 Heroku、Render 或任何支持 Node.js 的平台。