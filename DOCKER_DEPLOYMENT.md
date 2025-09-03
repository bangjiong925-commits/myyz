# Docker部署指南 - 台湾PK10自动爬虫系统

使用Docker容器化部署台湾PK10自动爬虫系统，支持一键部署和跨平台运行。

## 🐳 Docker部署优势

- **环境一致性**: 消除"在我机器上能运行"的问题
- **快速部署**: 一条命令完成整个系统部署
- **易于维护**: 容器化管理，便于更新和回滚
- **资源隔离**: 独立的运行环境，不影响宿主机
- **可扩展性**: 支持水平扩展和负载均衡

## 📋 系统要求

### 服务器配置
- **内存**: 最低 2GB RAM
- **存储**: 最低 10GB 可用空间
- **网络**: 稳定的互联网连接

### 软件要求
- Docker Engine 20.10+
- Docker Compose 2.0+

## 🚀 快速部署

### 1. 安装Docker

#### Ubuntu/Debian
```bash
# 卸载旧版本
sudo apt-get remove docker docker-engine docker.io containerd runc

# 安装依赖
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到docker组
sudo usermod -aG docker $USER
```

#### CentOS/RHEL
```bash
# 卸载旧版本
sudo yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine

# 安装依赖
sudo yum install -y yum-utils

# 添加Docker仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到docker组
sudo usermod -aG docker $USER
```

#### 验证安装
```bash
# 重新登录或执行
newgrp docker

# 验证Docker安装
docker --version
docker compose version

# 测试Docker运行
docker run hello-world
```

### 2. 部署应用

```bash
# 1. 克隆项目
git clone <your-repository-url>
cd taiwan-pk10-scraper

# 2. 配置环境变量
cp .env.docker .env

# 3. 编辑环境变量（重要！）
nano .env
# 修改以下配置：
# MONGO_ADMIN_PASSWORD=your_secure_admin_password
# MONGO_APP_PASSWORD=your_secure_app_password
# MONITOR_PASSWORD=your_monitor_password

# 4. 构建并启动服务
docker compose up -d

# 5. 查看服务状态
docker compose ps

# 6. 查看日志
docker compose logs -f scraper
```

## 🔧 服务配置

### 基础服务（默认启动）

1. **MongoDB数据库** (端口: 27017)
   - 数据持久化存储
   - 自动创建用户和索引
   - 健康检查

2. **爬虫服务**
   - 每5分钟自动抓取数据
   - 自动重启机制
   - 数据本地备份

### 可选服务

3. **API服务** (端口: 3000)
   ```bash
   # 启动API服务
   docker compose up -d api
   
   # 测试API
   curl http://localhost:3000/api/latest
   ```

4. **监控界面** (端口: 8081)
   ```bash
   # 启动监控服务
   docker compose --profile monitoring up -d
   
   # 访问监控界面
   # http://localhost:8081
   # 用户名: admin
   # 密码: 在.env文件中设置的MONITOR_PASSWORD
   ```

## 📊 管理命令

### 服务管理

```bash
# 启动所有服务
docker compose up -d

# 启动特定服务
docker compose up -d scraper

# 停止所有服务
docker compose down

# 重启服务
docker compose restart scraper

# 查看服务状态
docker compose ps

# 查看服务日志
docker compose logs -f scraper
docker compose logs -f mongodb

# 进入容器
docker compose exec scraper bash
docker compose exec mongodb mongo
```

### 数据管理

```bash
# 查看数据库数据
docker compose exec mongodb mongo taiwan_pk10 --eval "db.taiwan_pk10_data.find().limit(5).pretty()"

# 备份数据库
docker compose exec mongodb mongodump --db taiwan_pk10 --out /data/backup

# 查看数据文件
docker compose exec scraper ls -la /app/data/

# 查看日志文件
docker compose exec scraper ls -la /app/logs/
```

### 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker compose build --no-cache

# 重启服务
docker compose down
docker compose up -d

# 清理旧镜像
docker image prune -f
```

## 🔍 监控和调试

### 健康检查

```bash
# 检查所有服务健康状态
docker compose ps

# 查看详细健康检查信息
docker inspect taiwan-pk10-scraper | grep -A 10 Health

# 手动执行健康检查
docker compose exec scraper python3 -c "import os; print('OK' if os.path.exists('/app/data/latest_taiwan_pk10_data.json') else 'FAIL')"
```

### 性能监控

```bash
# 查看容器资源使用情况
docker stats

# 查看特定容器资源使用
docker stats taiwan-pk10-scraper

# 查看容器详细信息
docker inspect taiwan-pk10-scraper
```

### 日志分析

```bash
# 实时查看爬虫日志
docker compose logs -f --tail=100 scraper

# 查看MongoDB日志
docker compose logs -f --tail=50 mongodb

# 查看API日志
docker compose logs -f api

# 导出日志到文件
docker compose logs scraper > scraper.log
```

## 🔒 安全配置

### 1. 环境变量安全

```bash
# 生成安全密码
openssl rand -base64 32

# 设置文件权限
chmod 600 .env

# 确保.env文件不被提交到Git
echo ".env" >> .gitignore
```

### 2. 网络安全

```bash
# 只暴露必要端口
# 在docker-compose.yml中注释掉不需要的端口映射

# 使用防火墙限制访问
sudo ufw allow 22/tcp
sudo ufw allow 3000/tcp  # 仅在需要API访问时
sudo ufw deny 27017/tcp  # 禁止外部访问MongoDB
sudo ufw deny 8081/tcp   # 禁止外部访问监控界面
```

### 3. 数据安全

```bash
# 定期备份数据
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
docker compose exec -T mongodb mongodump --db taiwan_pk10 --archive > $BACKUP_DIR/taiwan_pk10.archive
echo "备份完成: $BACKUP_DIR"
EOF

chmod +x backup.sh

# 设置定时备份
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

## 🚀 生产环境部署

### 1. 生产环境配置

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mongodb:
    image: mongo:4.4
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ADMIN_PASSWORD}
    volumes:
      - mongodb_data:/data/db
      - ./mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
    networks:
      - pk10-network
    # 不暴露端口到宿主机
    
  scraper:
    build: .
    restart: always
    environment:
      MONGODB_URI: mongodb://pk10_user:${MONGO_APP_PASSWORD}@mongodb:27017/taiwan_pk10
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - mongodb
    networks:
      - pk10-network
      
  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - pk10-network

volumes:
  mongodb_data:

networks:
  pk10-network:
    driver: bridge
```

### 2. 使用外部数据库

```bash
# 使用云数据库服务
# 修改.env文件
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/taiwan_pk10

# 启动时排除本地MongoDB
docker compose up -d scraper api
```

### 3. 集群部署

```bash
# 使用Docker Swarm
docker swarm init

# 部署到集群
docker stack deploy -c docker-compose.yml taiwan-pk10

# 扩展服务
docker service scale taiwan-pk10_scraper=3
```

## 📈 性能优化

### 1. 资源限制

```yaml
# 在docker-compose.yml中添加资源限制
services:
  scraper:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 2. 缓存优化

```bash
# 使用多阶段构建减少镜像大小
# 在Dockerfile中优化层缓存

# 清理无用镜像和容器
docker system prune -f

# 清理无用卷
docker volume prune -f
```

## 🚨 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 查看详细错误信息
   docker compose logs scraper
   
   # 检查容器状态
   docker compose ps
   
   # 重新构建镜像
   docker compose build --no-cache scraper
   ```

2. **数据库连接失败**
   ```bash
   # 检查MongoDB容器状态
   docker compose logs mongodb
   
   # 测试数据库连接
   docker compose exec scraper python3 -c "import pymongo; print(pymongo.MongoClient('mongodb://pk10_user:password@mongodb:27017/taiwan_pk10').admin.command('ping'))"
   ```

3. **Chrome浏览器问题**
   ```bash
   # 进入容器检查Chrome
   docker compose exec scraper google-chrome --version
   
   # 重新构建镜像
   docker compose build --no-cache
   ```

4. **内存不足**
   ```bash
   # 增加交换空间
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   
   # 限制容器内存使用
   # 在docker-compose.yml中添加内存限制
   ```

### 调试技巧

```bash
# 进入容器调试
docker compose exec scraper bash

# 查看容器内进程
docker compose exec scraper ps aux

# 查看容器内网络
docker compose exec scraper netstat -tlnp

# 测试网络连接
docker compose exec scraper curl -I https://www.taiwanlottery.com.tw

# 手动运行爬虫
docker compose exec scraper python3 auto_scraper.py --mode single
```

## 📞 技术支持

### 获取帮助

1. **查看日志**: 首先查看相关服务的日志
2. **检查配置**: 确认环境变量和配置文件正确
3. **验证网络**: 确保容器间网络通信正常
4. **资源检查**: 确保有足够的内存和磁盘空间

### 有用的命令

```bash
# 一键诊断脚本
cat > diagnose.sh << 'EOF'
#!/bin/bash
echo "=== Docker版本 ==="
docker --version
docker compose version

echo "\n=== 服务状态 ==="
docker compose ps

echo "\n=== 资源使用 ==="
docker stats --no-stream

echo "\n=== 最新日志 ==="
docker compose logs --tail=10 scraper

echo "\n=== 数据库状态 ==="
docker compose exec -T mongodb mongo --eval "db.adminCommand('ping')" --quiet

echo "\n=== 最新数据 ==="
docker compose exec -T mongodb mongo taiwan_pk10 --eval "db.taiwan_pk10_data.find().sort({period: -1}).limit(1).pretty()" --quiet
EOF

chmod +x diagnose.sh
./diagnose.sh
```

---

**Docker部署完成后，系统将在容器中自动运行，数据持久化保存，支持自动重启和健康检查。**