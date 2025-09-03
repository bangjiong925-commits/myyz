# Railway部署指南 - Taiwan PK10 自动爬虫系统

## 概述

本指南将帮助您将Taiwan PK10自动爬虫系统部署到Railway平台。Railway是一个现代化的云平台，支持Python应用、定时任务和数据库服务。

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端页面      │    │  MongoDB API    │    │   自动爬虫      │
│  (Vercel/本地)  │───▶│   (Railway)     │◀───│  (Railway)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  MongoDB Atlas  │    │   定时任务      │
                       │   (云数据库)    │    │  (每5分钟)      │
                       └─────────────────┘    └─────────────────┘
```

## 前置准备

### 1. 注册账号
- [Railway账号](https://railway.app/) - 免费额度$5/月
- [MongoDB Atlas账号](https://www.mongodb.com/atlas) - 免费层512MB

### 2. 安装工具
```bash
# 安装Railway CLI
npm install -g @railway/cli

# 或使用其他方式
curl -fsSL https://railway.app/install.sh | sh
```

### 3. 登录Railway
```bash
railway login
```

## 部署步骤

### 步骤1: 准备MongoDB数据库

1. **创建MongoDB Atlas集群**
   - 访问 [MongoDB Atlas](https://cloud.mongodb.com/)
   - 创建免费集群（M0 Sandbox）
   - 设置数据库用户和密码
   - 配置网络访问（允许所有IP: 0.0.0.0/0）

2. **获取连接字符串**
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/<dbname>?retryWrites=true&w=majority
   ```

### 步骤2: 部署到Railway

#### 方法一: 快速一键部署（推荐）
```bash
# 进入项目目录
cd myyz

# 运行一键部署脚本
./deploy-to-railway.sh
```

**脚本功能:**
- ✅ 自动检查环境和依赖
- ✅ 引导Railway登录和项目初始化
- ✅ 智能配置环境变量
- ✅ 自动部署和测试
- ✅ 提供部署后的管理命令

#### 方法二: 传统自动部署
```bash
# 运行传统部署脚本
./railway-deploy.sh
```

#### 方法三: 手动部署

1. **初始化Railway项目**
   ```bash
   railway init
   ```

2. **设置环境变量**
   ```bash
   # 设置MongoDB连接
   railway variables set MONGODB_URI="mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/taiwan_pk10?retryWrites=true&w=majority"
   
   # 设置数据库名
   railway variables set MONGODB_DB_NAME="taiwan_pk10"
   
   # 设置日志级别
   railway variables set LOG_LEVEL="INFO"
   ```

3. **部署应用**
   ```bash
   railway up
   ```

### 步骤3: 配置服务

Railway会自动检测到`Procfile`并创建两个服务：

1. **Web服务** (mongodb_api.py)
   - 提供API接口
   - 自动分配公网域名
   - 端口由Railway自动设置

2. **Worker服务** (auto_scraper.py)
   - 后台定时爬虫
   - 每5分钟执行一次
   - 无需公网访问

### 步骤4: 验证部署

1. **检查服务状态**
   ```bash
   railway status
   ```

2. **查看日志**
   ```bash
   # 查看API服务日志
   railway logs --service web
   
   # 查看爬虫服务日志
   railway logs --service worker
   ```

3. **获取API地址**
   ```bash
   railway domain
   ```

4. **测试API接口**
   ```bash
   # 健康检查
   curl https://your-app.railway.app/api/health
   
   # 获取今日数据
   curl https://your-app.railway.app/api/today-data
   ```

5. **使用自动化测试脚本**
   ```bash
   # 运行完整的部署测试
   python3 test_railway_deployment.py https://your-app.railway.app
   
   # 或使用快速测试命令
   ./deploy-to-railway.sh --test-only
   ```

## 环境变量配置

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `MONGODB_URI` | ✅ | - | MongoDB连接字符串 |
| `MONGODB_DB_NAME` | ❌ | taiwan_pk10 | 数据库名称 |
| `PORT` | ❌ | 自动设置 | API服务端口 |
| `LOG_LEVEL` | ❌ | INFO | 日志级别 |
| `ENVIRONMENT` | ❌ | production | 运行环境 |

## 前端配置

### 更新API端点

修改`TWPK.html`中的API地址：

```javascript
// 替换为您的Railway部署地址
const RAILWAY_API_BASE = 'https://your-app.railway.app';

// 更新API调用
const todayResponse = await fetch(`${RAILWAY_API_BASE}/api/today-data`);
const latestResponse = await fetch(`${RAILWAY_API_BASE}/api/latest-data`);
```

### Vercel部署前端

```bash
# 部署到Vercel
vercel --prod
```

## 监控和维护

### 查看服务状态
```bash
# 服务概览
railway status

# 详细信息
railway ps

# 资源使用情况
railway usage
```

### 查看日志
```bash
# 实时日志
railway logs --follow

# 特定服务日志
railway logs --service web
railway logs --service worker

# 历史日志
railway logs --since 1h
```

### 重启服务
```bash
# 重启所有服务
railway restart

# 重启特定服务
railway restart --service worker
```

## 成本分析

### Railway免费额度
- **计算时间**: $5/月免费额度
- **内存**: 512MB RAM
- **存储**: 1GB
- **带宽**: 100GB/月

### 预估使用量
- **API服务**: ~$2-3/月
- **爬虫服务**: ~$1-2/月
- **总计**: ~$3-5/月（在免费额度内）

### MongoDB Atlas免费层
- **存储**: 512MB
- **连接数**: 500
- **备份**: 无

## 故障排除

### 常见问题

1. **部署失败**
   ```bash
   # 检查构建日志
   railway logs --deployment
   
   # 检查依赖
   railway run pip list
   ```

2. **MongoDB连接失败**
   - 检查连接字符串格式
   - 确认网络访问设置
   - 验证用户名密码

3. **爬虫不工作**
   ```bash
   # 检查worker服务状态
   railway logs --service worker
   
   # 手动触发爬虫
   railway run python auto_scraper.py --mode single
   ```

4. **API无响应**
   ```bash
   # 检查web服务状态
   railway status
   
   # 重启web服务
   railway restart --service web
   ```

### 调试命令

```bash
# 进入Railway容器
railway shell

# 运行Python脚本
railway run python mongodb_api.py

# 检查环境变量
railway variables

# 查看项目信息
railway info
```

## 扩展和优化

### 性能优化
1. **增加内存**: 升级到Hobby计划（$5/月）
2. **数据库优化**: 创建索引，优化查询
3. **缓存策略**: 添加Redis缓存

### 功能扩展
1. **多地区部署**: 使用Railway的多地区功能
2. **监控告警**: 集成Sentry或其他监控服务
3. **自动备份**: 设置MongoDB定期备份

## 支持和帮助

- [Railway文档](https://docs.railway.app/)
- [MongoDB Atlas文档](https://docs.atlas.mongodb.com/)
- [项目GitHub仓库](https://github.com/your-repo)

---

**部署完成后，您将拥有一个完全自动化的Taiwan PK10数据采集和分析系统！**