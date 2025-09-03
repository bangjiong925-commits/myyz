# 服务器部署指南 - 台湾PK10自动爬虫系统

本指南将帮助您在服务器上部署完整的台湾PK10自动爬虫系统，实现数据自动抓取并保存到MongoDB数据库。

## 🚀 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   定时任务       │───▶│   Python爬虫    │───▶│   MongoDB数据库  │
│   (Crontab)     │    │   (auto_scraper) │    │   (数据存储)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   API服务器      │
                       │   (数据接口)     │
                       └─────────────────┘
```

## 📋 系统要求

### 服务器环境
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **内存**: 最低 2GB RAM
- **存储**: 最低 10GB 可用空间
- **网络**: 稳定的互联网连接

### 软件依赖
- Python 3.8+
- MongoDB 4.4+
- Chrome/Chromium 浏览器
- Git

## 🛠️ 部署步骤

### 1. 系统准备

#### Ubuntu/Debian 系统
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装基础依赖
sudo apt install -y python3 python3-pip git curl wget

# 安装Chrome浏览器
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# 安装MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt update
sudo apt install -y mongodb-org
```

#### CentOS/RHEL 系统
```bash
# 更新系统包
sudo yum update -y

# 安装基础依赖
sudo yum install -y python3 python3-pip git curl wget

# 安装Chrome浏览器
sudo yum install -y https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm

# 安装MongoDB
echo '[mongodb-org-4.4]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/4.4/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-4.4.asc' | sudo tee /etc/yum.repos.d/mongodb-org-4.4.repo
sudo yum install -y mongodb-org
```

### 2. MongoDB 配置

```bash
# 启动MongoDB服务
sudo systemctl start mongod
sudo systemctl enable mongod

# 检查服务状态
sudo systemctl status mongod

# 创建数据库用户（可选，用于安全配置）
mongo
```

在MongoDB shell中执行：
```javascript
// 创建管理员用户
use admin
db.createUser({
  user: "admin",
  pwd: "your_secure_password",
  roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
})

// 创建应用数据库和用户
use taiwan_pk10
db.createUser({
  user: "pk10_user",
  pwd: "your_app_password",
  roles: [ { role: "readWrite", db: "taiwan_pk10" } ]
})

exit
```

### 3. 项目部署

```bash
# 创建项目目录
sudo mkdir -p /opt/taiwan-pk10-scraper
sudo chown $USER:$USER /opt/taiwan-pk10-scraper
cd /opt/taiwan-pk10-scraper

# 克隆项目代码
git clone <your-repository-url> .
# 或者上传项目文件到服务器

# 安装Python依赖
pip3 install -r requirements.txt

# 创建必要目录
mkdir -p data logs

# 设置执行权限
chmod +x *.sh *.py
```

### 4. 环境配置

创建环境配置文件：
```bash
# 创建 .env 文件
cat > .env << EOF
# MongoDB配置
MONGODB_URI=mongodb://pk10_user:your_app_password@localhost:27017/taiwan_pk10
MONGODB_DB_NAME=taiwan_pk10

# 爬虫配置
SCRAPER_INTERVAL=300  # 5分钟
MAX_RETRIES=3
TIMEOUT=30

# 日志配置
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=7
EOF
```

### 5. 测试运行

```bash
# 测试单次数据抓取
python3 auto_scraper.py --mode single

# 检查数据是否成功保存到MongoDB
mongo taiwan_pk10 --eval "db.taiwan_pk10_data.count()"

# 查看最新数据
mongo taiwan_pk10 --eval "db.taiwan_pk10_data.find().sort({period: -1}).limit(5).pretty()"
```

### 6. 设置自动运行

#### 方法1: 使用Crontab（推荐）

```bash
# 编辑crontab
crontab -e

# 添加以下行（每5分钟执行一次）
*/5 * * * * cd /opt/taiwan-pk10-scraper && /usr/bin/python3 auto_scraper.py --mode single >> /var/log/taiwan-pk10-scraper.log 2>&1

# 添加日志清理任务（每天凌晨清理7天前的日志）
0 0 * * * find /opt/taiwan-pk10-scraper/logs -name "*.log" -mtime +7 -delete
```

#### 方法2: 使用Systemd服务

```bash
# 复制服务文件
sudo cp taiwan-pk10-scraper.service /etc/systemd/system/

# 修改服务文件中的路径
sudo sed -i 's|/opt/taiwan-pk10-scraper|'$(pwd)'|g' /etc/systemd/system/taiwan-pk10-scraper.service

# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动并启用服务
sudo systemctl start taiwan-pk10-scraper
sudo systemctl enable taiwan-pk10-scraper

# 检查服务状态
sudo systemctl status taiwan-pk10-scraper
```

### 7. API服务器部署（可选）

如果需要提供数据API接口：

```bash
# 启动API服务器
python3 api_server.py --port 3000 &

# 或者使用systemd管理API服务
cat > /etc/systemd/system/taiwan-pk10-api.service << EOF
[Unit]
Description=Taiwan PK10 API Server
After=network.target mongodb.service
Wants=mongodb.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/api_server.py --port 3000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start taiwan-pk10-api
sudo systemctl enable taiwan-pk10-api
```

## 📊 监控和维护

### 状态检查

```bash
# 检查系统状态
python3 check_auto_status.py

# 查看cron日志
tail -f /var/log/taiwan-pk10-scraper.log

# 查看系统服务日志
sudo journalctl -u taiwan-pk10-scraper -f

# 检查MongoDB状态
sudo systemctl status mongod
mongo --eval "db.adminCommand('ismaster')"
```

### 数据库维护

```bash
# 查看数据库大小
mongo taiwan_pk10 --eval "db.stats()"

# 创建索引优化查询
mongo taiwan_pk10 --eval "db.taiwan_pk10_data.createIndex({period: -1})"
mongo taiwan_pk10 --eval "db.taiwan_pk10_data.createIndex({drawDate: -1})"

# 数据备份
mongodump --db taiwan_pk10 --out /backup/mongodb/$(date +%Y%m%d)

# 数据恢复
mongorestore --db taiwan_pk10 /backup/mongodb/20231201/taiwan_pk10
```

### 日志管理

```bash
# 设置日志轮转
sudo cat > /etc/logrotate.d/taiwan-pk10 << EOF
/var/log/taiwan-pk10-scraper.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
```

## 🔧 故障排除

### 常见问题

1. **Chrome浏览器问题**
   ```bash
   # 安装缺失的依赖
   sudo apt install -y libnss3 libgconf-2-4 libxss1 libappindicator1 libindicator7
   ```

2. **MongoDB连接问题**
   ```bash
   # 检查MongoDB服务
   sudo systemctl status mongod
   
   # 检查端口是否开放
   sudo netstat -tlnp | grep 27017
   ```

3. **权限问题**
   ```bash
   # 设置正确的文件权限
   sudo chown -R $USER:$USER /opt/taiwan-pk10-scraper
   chmod +x *.py *.sh
   ```

4. **网络问题**
   ```bash
   # 测试网络连接
   curl -I https://www.taiwanlottery.com.tw
   ```

### 性能优化

1. **MongoDB优化**
   ```javascript
   // 在MongoDB中创建复合索引
   db.taiwan_pk10_data.createIndex({"drawDate": -1, "period": -1})
   
   // 设置TTL索引自动清理旧数据（可选）
   db.taiwan_pk10_data.createIndex({"scrapedAt": 1}, {expireAfterSeconds: 7776000}) // 90天
   ```

2. **系统资源监控**
   ```bash
   # 安装监控工具
   sudo apt install -y htop iotop
   
   # 监控系统资源
   htop
   iotop
   ```

## 🔒 安全配置

### 防火墙设置

```bash
# 配置UFW防火墙
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 3000/tcp  # API端口（如果需要）

# MongoDB只允许本地连接
sudo ufw deny 27017
```

### MongoDB安全

```bash
# 启用MongoDB认证
sudo sed -i 's/#security:/security:\n  authorization: enabled/' /etc/mongod.conf
sudo systemctl restart mongod
```

## 📈 扩展部署

### 多服务器部署

1. **主从架构**: 一台主服务器运行爬虫，多台从服务器提供API服务
2. **负载均衡**: 使用Nginx进行负载均衡
3. **数据库集群**: MongoDB副本集配置

### Docker部署（可选）

```dockerfile
# Dockerfile示例
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "auto_scraper.py", "--mode", "schedule"]
```

## 📞 技术支持

如果在部署过程中遇到问题，请检查：

1. 系统日志: `/var/log/syslog`
2. 应用日志: `logs/` 目录
3. MongoDB日志: `/var/log/mongodb/mongod.log`
4. Cron日志: `/var/log/cron.log`

---

**部署完成后，系统将自动每5分钟抓取一次台湾PK10开奖数据并保存到MongoDB数据库中。**