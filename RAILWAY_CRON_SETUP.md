# Railway云端定时任务配置指南

## 📋 概述

本文档说明如何在Railway平台上配置定时任务，用于在凌晨00:00到早上07:05之间读取2024年9月5日的数据。

## 🚀 部署文件

### 1. 核心脚本文件

- `railway_september_5_reader.py` - 主要的数据读取脚本
- `railway_cron.py` - Cron服务脚本
- `read_yesterday_data.py` - 底层数据读取逻辑

### 2. 配置文件

- `Procfile` - Railway服务定义
- `requirements.txt` - Python依赖包
- `railway.toml` - Railway部署配置

## ⚙️ Railway服务配置

### Procfile服务定义

```
# Web service - MongoDB API Server
web: python3 mongodb_api.py --port ${PORT:-3000}

# Worker service - Auto Scraper
worker: python3 auto_scraper.py

# Cron service - September 5 Data Reader
cron: python3 railway_cron.py
```

### 环境变量配置

在Railway项目中设置以下环境变量：

```bash
# MongoDB Atlas连接字符串
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/taiwan_pk10

# Railway环境标识
RAILWAY_ENVIRONMENT=production

# 时区设置（可选）
TZ=Asia/Taipei
```

## 🕐 定时任务逻辑

### 执行时间窗口

- **时间范围**: 凌晨00:00 - 早上07:05（台湾时间）
- **检查频率**: 每小时检查一次
- **特定时间点**: 01:00, 03:00, 05:00, 07:00

### 任务流程

1. **时间检查**: 验证当前时间是否在执行窗口内
2. **环境检查**: 验证MongoDB连接和环境变量
3. **数据读取**: 执行2024-09-05数据读取
4. **日志记录**: 记录执行状态和结果

## 📦 部署步骤

### 1. 准备代码

确保所有文件都已提交到Git仓库：

```bash
git add .
git commit -m "Add Railway cron job for September 5 data reading"
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
railway variables set RAILWAY_ENVIRONMENT="production"
railway variables set TZ="Asia/Taipei"
```

### 3. 部署应用

```bash
# 部署到Railway
railway up
```

### 4. 启动Cron服务

在Railway控制台中：

1. 进入项目设置
2. 找到"Services"部分
3. 确保`cron`服务已启用并运行

## 🔍 监控和调试

### 查看日志

```bash
# 查看cron服务日志
railway logs --service cron

# 实时监控日志
railway logs --service cron --follow
```

### 日志文件位置

- Railway环境: `/tmp/railway_cron.log`
- Railway环境: `/tmp/railway_september_5.log`
- Railway环境: `/tmp/read_yesterday_data.log`

### 常见问题排查

1. **服务未启动**
   ```bash
   railway ps
   railway restart --service cron
   ```

2. **环境变量问题**
   ```bash
   railway variables
   ```

3. **MongoDB连接问题**
   - 检查MongoDB Atlas白名单设置
   - 验证连接字符串格式
   - 确认数据库用户权限

## 📊 执行状态检查

### 手动触发测试

可以通过Railway控制台手动重启cron服务来测试：

```bash
railway restart --service cron
```

### 数据验证

检查MongoDB Atlas中是否有相应的数据读取记录，或查看导出的JSON文件。

## ⚠️ 注意事项

1. **时区设置**: 确保Railway环境使用正确的时区（Asia/Taipei）
2. **资源限制**: Railway有计算资源限制，注意监控使用情况
3. **日志管理**: 定期清理临时日志文件，避免占用过多存储空间
4. **网络连接**: 确保Railway能够访问MongoDB Atlas
5. **错误处理**: 脚本包含完整的异常处理和重试机制

## 🔧 维护和更新

### 更新代码

```bash
# 更新代码后重新部署
git add .
git commit -m "Update cron job configuration"
git push
railway up
```

### 停止定时任务

如需停止定时任务：

```bash
railway down --service cron
```

### 修改执行时间

修改`railway_cron.py`中的调度设置，然后重新部署。

## 📞 支持

如遇到问题，请检查：

1. Railway服务状态
2. 环境变量配置
3. MongoDB Atlas连接
4. 服务日志输出

通过Railway控制台或CLI工具可以获取详细的运行状态和错误信息。