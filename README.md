# 台湾PK10自动爬虫系统

一个完整的台湾PK10开奖数据自动抓取、存储和展示系统，支持多种部署方式和数据存储方案。

## 🎯 功能特性

### 核心功能
- **自动数据抓取**: 每5分钟自动抓取最新开奖数据
- **多存储支持**: 支持MongoDB数据库和JSON文件存储
- **实时展示**: Web界面实时显示开奖数据和统计信息
- **API服务**: 提供RESTful API接口
- **智能调度**: 支持定时任务和内置调度器
- **健康监控**: 完整的系统状态监控和日志记录

### 数据功能
- **开奖记录**: 完整的开奖号码、时间记录
- **统计分析**: 号码频率、遗漏值、热冷分析
- **数据验证**: 期号连续性检查和数据完整性验证
- **历史数据**: 支持历史数据查询和导出

### 部署方式
- **一键部署**: 自动化脚本部署
- **Docker容器**: 容器化部署方案
- **云服务器**: 支持主流云服务商
- **本地开发**: 快速本地测试环境

## 📁 项目结构

```
taiwan-pk10-scraper/
├── 核心文件
│   ├── auto_scraper.py          # 主要爬虫脚本
│   ├── api_server.py            # API服务器
│   ├── python_scraper.py        # 基础爬虫模块
│   └── TWPK.html               # Web展示界面
│
├── 配置文件
│   ├── requirements.txt         # Python依赖
│   ├── .env.docker             # Docker环境配置
│   ├── taiwan-pk10-scraper.service  # Systemd服务
│   └── crontab_example.txt     # Crontab示例
│
├── 部署脚本
│   ├── start_system.sh         # 系统启动脚本
│   ├── stop_system.sh          # 系统停止脚本
│   ├── deploy_server.sh        # 服务器部署脚本
│   ├── setup_auto_run.sh       # 自动运行设置
│   └── check_auto_status.py    # 状态检查脚本
│
├── Docker相关
│   ├── Dockerfile              # Docker镜像构建
│   ├── docker-compose.yml      # Docker Compose配置
│   └── mongo-init.js           # MongoDB初始化
│
├── 文档
│   ├── README.md               # 项目说明（本文件）
│   ├── DEPLOYMENT_SUMMARY.md   # 部署方案总览
│   ├── SERVER_DEPLOYMENT_GUIDE.md  # 服务器部署指南
│   ├── CLOUD_DEPLOYMENT.md     # 云服务器部署指南
│   └── DOCKER_DEPLOYMENT.md    # Docker部署指南
│
└── 数据目录
    ├── data/                   # 数据文件存储
    └── logs/                   # 日志文件
```

## 🚀 快速开始

### 方式一：一键启动（推荐新手）

```bash
# 1. 克隆项目
git clone <repository-url>
cd taiwan-pk10-scraper

# 2. 一键启动系统
./start_system.sh

# 3. 访问Web界面
open http://localhost:3000
```

### 方式二：Docker部署（推荐生产环境）

```bash
# 1. 准备环境配置
cp .env.docker .env
nano .env  # 修改密码等配置

# 2. 启动所有服务
docker compose up -d

# 3. 查看服务状态
docker compose ps

# 4. 访问服务
open http://localhost:3000      # Web界面
open http://localhost:8081      # MongoDB管理界面
```

### 方式三：服务器部署

```bash
# 1. 运行部署脚本（需要root权限）
sudo ./deploy_server.sh

# 2. 按提示完成配置
# 3. 系统将自动启动并设置定时任务
```

## 📊 系统监控

### 状态检查
```bash
# 检查系统状态
python3 check_auto_status.py

# 查看实时日志
tail -f logs/auto_scraper.log

# 查看API服务器日志
tail -f logs/api_server.log
```

### 数据验证
```bash
# 手动执行一次数据抓取
python3 auto_scraper.py --mode single

# 检查数据库连接
python3 auto_scraper.py --test-db

# 查看最新数据
cat data/latest_taiwan_pk10_data.json | jq '.[0:5]'
```

## 🔧 管理命令

### 系统管理

```bash
# 启动系统
./start_system.sh

# 停止系统
./stop_system.sh

# 停止系统（包括MongoDB）
./stop_system.sh --with-mongodb

# 重启系统
./stop_system.sh && ./start_system.sh
```

### Docker管理

```bash
# 启动所有服务
docker compose up -d

# 停止所有服务
docker compose down

# 重启特定服务
docker compose restart scraper

# 查看日志
docker compose logs -f scraper
```

## 🚨 故障排除

### 常见问题

**1. 爬虫无法获取数据**
```bash
# 检查网络连接
curl -I https://www.twpk10.com

# 查看详细错误
python3 auto_scraper.py --mode single --debug
```

**2. MongoDB连接失败**
```bash
# 检查MongoDB状态
sudo systemctl status mongod

# 测试连接
mongo --eval "db.runCommand('ping')"
```

**3. API服务无法访问**
```bash
# 检查端口占用
lsof -i :3000

# 查看API日志
tail -f logs/api_server.log
```

## 📞 技术支持

如果在部署过程中遇到问题，请按以下顺序排查：

1. **查看对应的部署指南文档**
2. **运行系统诊断脚本**: `python3 check_auto_status.py`
3. **检查日志文件**: `tail -f logs/*.log`
4. **验证网络和权限**
5. **查看常见问题解决方案**

---

**🎉 现在您可以选择适合的部署方式，开始使用台湾PK10自动爬虫系统！**

详细的部署指南请参考 `DEPLOYMENT_SUMMARY.md` 文件。
