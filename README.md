# Taiwan PK10 MongoDB API System

一个基于 MongoDB 的台湾PK10数据管理系统，提供RESTful API接口。

## 功能特性

- 🗄️ MongoDB 数据库存储
- 🚀 Express.js API 服务器
- 📊 数据统计和查询
- 🔍 按期号和日期范围查询
- 📱 响应式Web界面
- 🔧 健康检查和监控

## 技术栈

- **后端**: Node.js + Express.js
- **数据库**: MongoDB
- **前端**: HTML + JavaScript
- **部署**: Railway

## 快速开始

### 环境要求

- Node.js 16+
- MongoDB 4.4+
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 环境配置

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
MONGODB_URI=mongodb://localhost:27017/taiwan_pk10
PORT=3000
```

### 启动服务

```bash
# 启动 API 服务器
npm run api

# 开发模式（自动重启）
npm run dev-api

# 启动静态文件服务器
npm start
```

## API 接口

### 基础接口

- `GET /api/health` - 健康检查
- `GET /api/stats` - 获取统计信息

### 数据查询

- `GET /api/latest` - 获取最新数据
- `GET /api/data/:period` - 按期号查询
- `GET /api/data/range/:start/:end` - 按日期范围查询

### 数据管理

- `POST /api/data` - 添加单条数据
- `POST /api/data/batch` - 批量添加数据
- `DELETE /api/data/cleanup/:days` - 清理指定天数前的数据

### 备份恢复

- `GET /api/backup` - 数据备份
- `POST /api/restore` - 数据恢复

## 项目结构

```
├── api_server_mongodb.js    # MongoDB API 服务器
├── simple_server.py         # 静态文件服务器
├── deploy/                  # 部署相关文件
│   ├── mongodb_manager.py   # MongoDB 管理器
│   └── mongodb_setup.py     # MongoDB 初始化脚本
├── data/                    # 数据文件
├── public/                  # 静态资源
└── views/                   # 视图文件
```

## 部署

### Railway 部署

1. 连接 GitHub 仓库到 Railway
2. 设置环境变量
3. 部署完成

### 本地部署

```bash
# 启动 MongoDB
mongod

# 初始化数据库
cd deploy
python3 mongodb_setup.py

# 启动服务
npm run api
```

## 许可证

MIT License