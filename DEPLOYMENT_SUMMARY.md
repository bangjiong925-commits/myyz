# 台湾PK10自动爬虫系统 - 部署方案总览

本文档汇总了台湾PK10自动爬虫系统的所有部署方案，帮助您选择最适合的部署方式。

## 🎯 部署方案对比

| 部署方式 | 难度 | 适用场景 | 优势 | 劣势 |
|---------|------|----------|------|------|
| **一键脚本部署** | ⭐⭐ | 传统服务器 | 自动化程度高，配置完整 | 需要手动管理依赖 |
| **Docker部署** | ⭐⭐⭐ | 现代化环境 | 环境一致，易于维护 | 需要学习Docker |
| **云服务器部署** | ⭐⭐ | 生产环境 | 稳定可靠，可扩展 | 需要付费 |
| **手动部署** | ⭐⭐⭐⭐ | 自定义需求 | 完全控制 | 配置复杂 |

## 📁 部署文件说明

### 核心文件
- `auto_scraper.py` - 主要爬虫脚本
- `api_server.py` - API服务器
- `check_auto_status.py` - 状态检查脚本
- `requirements.txt` - Python依赖包

### 配置文件
- `.env.docker` - Docker环境配置模板
- `taiwan-pk10-scraper.service` - Systemd服务配置
- `crontab_example.txt` - Crontab配置示例

### 部署脚本
- `deploy_server.sh` - 一键服务器部署脚本
- `setup_auto_run.sh` - 自动运行设置脚本

### Docker相关
- `Dockerfile` - Docker镜像构建文件
- `docker-compose.yml` - Docker Compose配置
- `mongo-init.js` - MongoDB初始化脚本

### 文档
- `SERVER_DEPLOYMENT_GUIDE.md` - 详细服务器部署指南
- `CLOUD_DEPLOYMENT.md` - 云服务器部署指南
- `DOCKER_DEPLOYMENT.md` - Docker部署指南
- `DEPLOYMENT_SUMMARY.md` - 本文档

## 🚀 推荐部署方案

### 1. 新手推荐：一键脚本部署

**适用场景**: 第一次部署，希望快速上手

```bash
# 1. 获取代码
git clone <repository-url>
cd taiwan-pk10-scraper

# 2. 运行一键部署
./deploy_server.sh
```

**优势**:
- 全自动安装依赖
- 自动配置MongoDB
- 自动设置定时任务
- 包含完整的错误处理

### 2. 生产环境推荐：Docker部署

**适用场景**: 生产环境，需要稳定可靠的部署

```bash
# 1. 准备环境
cp .env.docker .env
nano .env  # 修改密码配置

# 2. 启动服务
docker compose up -d

# 3. 查看状态
docker compose ps
```

**优势**:
- 环境隔离，不影响宿主机
- 支持一键更新和回滚
- 内置健康检查和自动重启
- 支持水平扩展

### 3. 云服务器推荐：阿里云/腾讯云

**适用场景**: 需要稳定的网络环境和专业运维

**配置推荐**:
- **规格**: 1核2GB内存
- **系统**: Ubuntu 20.04 LTS
- **存储**: 40GB SSD
- **带宽**: 1Mbps
- **月费用**: ¥30-50

## 📊 部署后验证

### 基础验证
```bash
# 1. 检查系统状态
python3 check_auto_status.py

# 2. 查看数据库数据
mongo taiwan_pk10 --eval "db.taiwan_pk10_data.find().limit(5).pretty()"

# 3. 检查定时任务
crontab -l

# 4. 查看日志
tail -f logs/cron.log
```

### Docker验证
```bash
# 1. 检查容器状态
docker compose ps

# 2. 查看服务日志
docker compose logs -f scraper

# 3. 检查数据
docker compose exec mongodb mongo taiwan_pk10 --eval "db.taiwan_pk10_data.count()"
```

## 🔧 常用管理命令

### 传统部署
```bash
# 手动执行抓取
cd /opt/taiwan-pk10-scraper
python3 auto_scraper.py --mode single

# 查看系统状态
sudo systemctl status taiwan-pk10-scraper

# 重启服务
sudo systemctl restart taiwan-pk10-scraper

# 查看MongoDB状态
sudo systemctl status mongod
```

### Docker部署
```bash
# 重启爬虫服务
docker compose restart scraper

# 查看实时日志
docker compose logs -f scraper

# 进入容器调试
docker compose exec scraper bash

# 备份数据
docker compose exec mongodb mongodump --db taiwan_pk10 --out /data/backup
```

## 🔍 监控和维护

### 日常监控
1. **数据更新检查**: 确保每5分钟有新数据
2. **系统资源监控**: CPU、内存、磁盘使用率
3. **日志文件检查**: 查看是否有错误信息
4. **网络连接测试**: 确保能正常访问目标网站

### 定期维护
1. **数据库备份**: 每天自动备份
2. **日志清理**: 清理7天前的日志文件
3. **系统更新**: 定期更新系统和依赖包
4. **性能优化**: 根据使用情况调整配置

## 🚨 故障排除

### 常见问题

1. **爬虫无法获取数据**
   - 检查网络连接
   - 验证目标网站是否可访问
   - 查看Chrome浏览器是否正常

2. **MongoDB连接失败**
   - 检查MongoDB服务状态
   - 验证连接字符串和凭据
   - 查看防火墙设置

3. **定时任务不执行**
   - 检查crontab配置
   - 验证脚本路径和权限
   - 查看cron日志

4. **系统资源不足**
   - 增加内存或交换空间
   - 清理临时文件和日志
   - 优化数据库索引

### 获取帮助

1. **查看日志**: 首先查看相关服务的日志文件
2. **运行诊断**: 使用 `check_auto_status.py` 检查系统状态
3. **测试网络**: 确保能访问目标网站
4. **检查配置**: 验证所有配置文件的正确性

## 📈 扩展部署

### 高可用部署
- **负载均衡**: 使用Nginx进行负载均衡
- **数据库集群**: MongoDB副本集配置
- **多服务器**: 主从架构部署

### 性能优化
- **缓存策略**: Redis缓存热点数据
- **数据库优化**: 索引优化和分片
- **网络优化**: CDN和代理配置

### 监控告警
- **Prometheus + Grafana**: 系统监控
- **ELK Stack**: 日志分析
- **钉钉/微信**: 告警通知

## 📞 技术支持

如果在部署过程中遇到问题，请按以下顺序排查：

1. **查看对应的部署指南文档**
2. **运行系统诊断脚本**
3. **检查日志文件**
4. **验证网络和权限**
5. **查看常见问题解决方案**

---

**选择适合您的部署方案，按照对应的指南文档进行部署，系统将自动每5分钟抓取一次台湾PK10开奖数据并保存到数据库中。**