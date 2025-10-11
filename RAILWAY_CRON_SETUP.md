# Railway MongoDB API 部署指南

## 📋 概述

本文档说明如何在Railway平台上部署Taiwan PK10 MongoDB API系统。

## 🚀 部署文件

### 1. 核心文件

- `api_server_mongodb.js` - MongoDB API 服务器
- `simple_server.py` - 静态文件服务器

### 2. 配置文件

- `Procfile` - Railway服务定义
- `package.json` - Node.js依赖包
- `requirements.txt` - Python依赖包
- `railway.toml` - Railway部署配置

## ⚙️ Railway服务配置

### Procfile服务定义

```
# Web service - Simple Static File Server
web: python3 simple_server.py

# MongoDB API Server
api: node api_server_mongodb.js
```

### 环境变量配置

在Railway项目中设置以下环境变量：

```bash
# MongoDB Atlas连接字符串
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/taiwan_pk10

# API服务端口
PORT=3000

# Railway环境标识
RAILWAY_ENVIRONMENT=production

# 时区设置（可选）
TZ=Asia/Taipei
```

## 📦 部署步骤

### 1. 准备代码

确保所有文件都已提交到Git仓库：

```bash
git add .
git commit -m "Deploy MongoDB API system to Railway"
git push
```

### 2. Railway项目配置

```bash
# 登录Railway
railway login

# 连接到现有项目或创建新项目
railway link

# 设置环境变量
railway variables set MONGODB_URI="your_mongodb_atlas_uri"
railway variables set PORT="3000"
railway variables set RAILWAY_ENVIRONMENT="production"
```

### 3. 部署应用

```bash
# 部署到Railway
railway up
```

## 🔍 监控和调试

### 查看日志

```bash
# 查看web服务日志
railway logs --service web

# 查看API服务日志
railway logs --service api

# 实时监控日志
railway logs --follow
```

### 常见问题排查

1. **服务未启动**
   ```bash
   railway ps
   railway restart
   ```

2. **环境变量问题**
   ```bash
   railway variables
   ```

3. **MongoDB连接问题**
   - 检查MongoDB Atlas白名单设置
   - 验证连接字符串格式
   - 确认数据库用户权限

## 📊 API测试

### 健康检查

```bash
curl https://your-app.railway.app/api/health
```

### 获取统计信息

```bash
curl https://your-app.railway.app/api/stats
```

## ⚠️ 注意事项

1. **资源限制**: Railway有计算资源限制，注意监控使用情况
2. **网络连接**: 确保Railway能够访问MongoDB Atlas
3. **环境变量**: 确保所有必需的环境变量都已正确设置

## 🔧 维护和更新

### 更新代码

```bash
# 更新代码后重新部署
git add .
git commit -m "Update API system"
git push
railway up
```

## 📞 支持

如遇到问题，请检查：

1. Railway服务状态
2. 环境变量配置
3. MongoDB Atlas连接
4. 服务日志输出

通过Railway控制台或CLI工具可以获取详细的运行状态和错误信息。