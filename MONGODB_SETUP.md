# MongoDB Atlas 设置指南

## 1. 创建 MongoDB Atlas 账户

1. 访问 https://www.mongodb.com/cloud/atlas
2. 点击 "Try Free" 注册账户（可以使用 Google 账户）
3. 选择 "Shared Cluster"（免费套餐）

## 2. 创建数据库集群

1. 选择云服务提供商（推荐 AWS）
2. 选择区域（推荐离你最近的区域，如亚太地区选 Singapore）
3. 点击 "Create Cluster"
4. 等待集群创建完成（约 1-2 分钟）

## 3. 配置数据库访问

### 创建数据库用户
1. 在左侧菜单点击 "Database Access"
2. 点击 "Add New Database User"
3. 选择 "Password" 认证方式
4. 输入用户名（如：aloadecor_admin）
5. 输入密码（请保存好，后面需要用到）
6. 权限选择 "Read and write to any database"
7. 点击 "Add User"

### 配置网络访问
1. 在左侧菜单点击 "Network Access"
2. 点击 "Add IP Address"
3. 选择 "Allow Access from Anywhere"（0.0.0.0/0）
   - 或者添加 Railway 的 IP 地址
4. 点击 "Confirm"

## 4. 获取连接字符串

1. 回到 "Database" 页面
2. 点击 "Connect" 按钮
3. 选择 "Connect your application"
4. 选择驱动：Node.js
5. 版本：4.1 or later
6. 复制连接字符串，格式如下：
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/aloadecor?retryWrites=true&w=majority
   ```
7. 将 `<username>` 和 `<password>` 替换为你的数据库用户名和密码

## 5. 在 Railway 配置环境变量

1. 登录 Railway 控制台
2. 选择你的项目
3. 点击 "Variables" 标签
4. 添加以下环境变量：
   - 名称：`MONGODB_URI`
   - 值：你的 MongoDB Atlas 连接字符串

## 6. 本地开发配置（可选）

如果在本地开发，可以：

### 选项 A：使用本地 MongoDB
1. 安装 MongoDB Community Edition
2. 启动 MongoDB 服务
3. 使用默认连接字符串：`mongodb://localhost:27017/aloadecor`

### 选项 B：使用 MongoDB Atlas（推荐）
在本地 `.env` 文件中添加：
```
MONGODB_URI=mongodb+srv://your_username:your_password@cluster0.xxxxx.mongodb.net/aloadecor?retryWrites=true&w=majority
```

## 7. 验证连接

部署后，访问健康检查端点：
```
https://your-railway-domain.railway.app/health
```

应该返回：
```json
{
  "status": "ok",
  "database": "connected"
}
```

## 8. 数据备份

MongoDB Atlas 自动提供：
- 每日备份（免费版保留 7 天）
- 连续备份（付费版）

你也可以手动导出数据：
```bash
mongodump --uri="your_connection_string" --out=backup/
```

## 故障排除

### 连接失败
1. 检查网络访问配置是否正确
2. 确认用户名和密码正确
3. 检查连接字符串格式

### 权限问题
1. 确认数据库用户有读写权限
2. 检查数据库名称是否正确（aloadecor）

### 数据未保存
1. 查看 Railway 日志
2. 检查 MongoDB Atlas 监控面板
3. 确认环境变量已正确设置
