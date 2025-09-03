# Taiwan PK10 自动爬虫系统部署指南

## 系统概述

这是一个完整的Taiwan PK10彩票数据自动抓取和展示系统，包含以下组件：

- **Python爬虫**: 自动抓取彩票开奖数据
- **MongoDB数据库**: 存储历史数据
- **API服务器**: 提供数据接口
- **Web前端**: 数据展示界面
- **自动化调度**: 定时任务管理

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │───▶│   API Server    │───▶│    MongoDB      │
│   (TWPK.html)   │    │ (mongodb_api.py)│    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │
                       ┌─────────────────┐
                       │  Auto Scraper   │
                       │(auto_scraper.py)│
                       └─────────────────┘
                                ▲
                                │
                       ┌─────────────────┐
                       │   Scheduler     │
                       │ (systemd/cron)  │
                       └─────────────────┘
```

## 快速部署

### 方法1: 自动部署脚本（推荐）

```bash
# 1. 克隆或下载项目文件到服务器
git clone <repository-url> /tmp/taiwan-pk10
cd /tmp/taiwan-pk10

# 2. 给部署脚本执行权限
chmod +x deploy.sh

# 3. 运行自动部署脚本
sudo ./deploy.sh
```

### 方法2: 手动部署

#### 1. 系统要求

- **操作系统**: Ubuntu 18.04+ / CentOS 7+ / Debian 10+
- **Python**: 3.8+
- **MongoDB**: 4.4+
- **内存**: 最少512MB
- **磁盘**: 最少2GB可用空间

#### 2. 安装系统依赖

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv mongodb curl wget git cron
sudo systemctl enable mongod
sudo systemctl start mongod
```

**CentOS/RHEL:**
```bash
sudo yum update -y
sudo yum install -y python3 python3-pip mongodb-server curl wget git cronie
sudo systemctl enable mongod
sudo systemctl start mongod
sudo systemctl enable crond
sudo systemctl start crond
```

#### 3. 创建项目环境

```bash
# 创建项目目录
sudo mkdir -p /opt/taiwan-pk10-scraper
cd /opt/taiwan-pk10-scraper

# 复制项目文件
sudo cp -r /path/to/your/project/* .

# 创建专用用户
sudo useradd -r -s /bin/false -d /opt/taiwan-pk10-scraper scraper

# 设置权限
sudo chown -R scraper:scraper /opt/taiwan-pk10-scraper
sudo chmod +x auto_scraper.py

# 创建必要目录
sudo mkdir -p logs data
sudo chown -R scraper:scraper logs data
```

#### 4. 安装Python依赖

```bash
# 创建虚拟环境
sudo -u scraper python3 -m venv venv
sudo -u scraper venv/bin/pip install --upgrade pip

# 安装依赖
sudo -u scraper venv/bin/pip install -r requirements.txt
```

#### 5. 配置服务

**设置systemd服务:**
```bash
# 复制服务文件
sudo cp taiwan-pk10-scraper.service /etc/systemd/system/
sudo cp taiwan-pk10-api.service /etc/systemd/system/  # 如果存在

# 重新加载systemd
sudo systemctl daemon-reload

# 启用并启动服务
sudo systemctl enable taiwan-pk10-scraper
sudo systemctl start taiwan-pk10-scraper

# 启动API服务
sudo systemctl enable taiwan-pk10-api
sudo systemctl start taiwan-pk10-api
```

**或者使用cron任务:**
```bash
# 编辑scraper用户的crontab
sudo crontab -u scraper -e

# 添加以下行（每5分钟执行一次）
*/5 * * * * cd /opt/taiwan-pk10-scraper && /opt/taiwan-pk10-scraper/venv/bin/python auto_scraper.py --mode single >> /opt/taiwan-pk10-scraper/logs/cron.log 2>&1
```

## 服务管理

### 查看服务状态

```bash
# 查看爬虫服务状态
sudo systemctl status taiwan-pk10-scraper

# 查看API服务状态
sudo systemctl status taiwan-pk10-api

# 查看MongoDB状态
sudo systemctl status mongod
```

### 查看日志

```bash
# 查看爬虫服务日志
sudo journalctl -u taiwan-pk10-scraper -f

# 查看API服务日志
sudo journalctl -u taiwan-pk10-api -f

# 查看应用日志
sudo tail -f /opt/taiwan-pk10-scraper/logs/*.log
```

### 重启服务

```bash
# 重启爬虫服务
sudo systemctl restart taiwan-pk10-scraper

# 重启API服务
sudo systemctl restart taiwan-pk10-api

# 重启MongoDB
sudo systemctl restart mongod
```

## API接口

系统提供以下API端点：

### 1. 获取今日数据
```
GET http://localhost:5000/api/today-data
```

### 2. 获取最新数据
```
GET http://localhost:5000/api/latest-data
```

### 3. 健康检查
```
GET http://localhost:5000/api/health
```

### 4. 手动触发爬虫
```
POST http://localhost:3001/api/scrape
```

## 配置说明

### 环境变量

可以通过环境变量配置系统参数：

```bash
# MongoDB连接
export MONGODB_URI="mongodb://localhost:27017"
export DB_NAME="taiwan_pk10"

# API服务器
export API_HOST="0.0.0.0"
export API_PORT="5000"

# 爬虫配置
export SCRAPER_INTERVAL="300"  # 5分钟
export SCRAPER_TIMEOUT="30"    # 30秒超时
```

### 修改抓取频率

**systemd服务方式:**
编辑 `auto_scraper.py` 中的调度设置：
```python
# 修改这一行来改变频率
schedule.every(5).minutes.do(self.run_scraper_job)  # 每5分钟
```

**cron方式:**
```bash
# 编辑crontab
sudo crontab -u scraper -e

# 修改频率（例如每10分钟）
*/10 * * * * cd /opt/taiwan-pk10-scraper && ...
```

## 监控和维护

### 1. 数据库维护

```bash
# 连接MongoDB
mongo taiwan_pk10

# 查看数据统计
db.lottery_data.count()
db.web_formatted_data.count()

# 查看最新数据
db.web_formatted_data.find().sort({"期号": -1}).limit(5)

# 清理旧数据（保留30天）
db.lottery_data.deleteMany({
    "scrapedAt": {
        "$lt": new Date(Date.now() - 30*24*60*60*1000)
    }
})
```

### 2. 日志轮转

创建logrotate配置：
```bash
sudo tee /etc/logrotate.d/taiwan-pk10-scraper << EOF
/opt/taiwan-pk10-scraper/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    su scraper scraper
}
EOF
```

### 3. 系统监控

创建简单的监控脚本：
```bash
#!/bin/bash
# /opt/taiwan-pk10-scraper/monitor.sh

# 检查服务状态
if ! systemctl is-active --quiet taiwan-pk10-scraper; then
    echo "爬虫服务已停止，正在重启..."
    systemctl restart taiwan-pk10-scraper
fi

if ! systemctl is-active --quiet taiwan-pk10-api; then
    echo "API服务已停止，正在重启..."
    systemctl restart taiwan-pk10-api
fi

# 检查数据更新
LAST_UPDATE=$(mongo taiwan_pk10 --quiet --eval "db.web_formatted_data.findOne({}, {scrapedAt: 1}, {sort: {scrapedAt: -1}}).scrapedAt")
CURRENT_TIME=$(date +%s)
LAST_UPDATE_TIME=$(date -d "$LAST_UPDATE" +%s)
DIFF=$((CURRENT_TIME - LAST_UPDATE_TIME))

if [ $DIFF -gt 1800 ]; then  # 30分钟没有更新
    echo "数据更新异常，最后更新时间: $LAST_UPDATE"
    # 可以发送告警邮件或通知
fi
```

添加到cron：
```bash
# 每10分钟检查一次
*/10 * * * * /opt/taiwan-pk10-scraper/monitor.sh >> /var/log/taiwan-pk10-monitor.log 2>&1
```

## 故障排除

### 常见问题

1. **服务无法启动**
   - 检查Python依赖是否安装完整
   - 检查文件权限是否正确
   - 查看systemd日志: `journalctl -u taiwan-pk10-scraper`

2. **数据库连接失败**
   - 确认MongoDB服务正在运行: `systemctl status mongod`
   - 检查防火墙设置
   - 验证连接字符串

3. **爬虫抓取失败**
   - 检查网络连接
   - 验证目标网站是否可访问
   - 查看爬虫日志文件

4. **API服务无响应**
   - 检查端口是否被占用: `netstat -tlnp | grep 5000`
   - 查看API服务日志
   - 验证防火墙规则

### 调试模式

```bash
# 手动运行爬虫（调试模式）
sudo -u scraper /opt/taiwan-pk10-scraper/venv/bin/python auto_scraper.py --mode single

# 手动运行API服务器（调试模式）
sudo -u scraper /opt/taiwan-pk10-scraper/venv/bin/python mongodb_api.py
```

## 安全建议

1. **防火墙配置**
   ```bash
   # 只允许必要的端口
   sudo ufw allow 22    # SSH
   sudo ufw allow 5000  # API服务
   sudo ufw enable
   ```

2. **MongoDB安全**
   ```bash
   # 绑定到本地接口
   sudo sed -i 's/#bindIp: 127.0.0.1/bindIp: 127.0.0.1/' /etc/mongod.conf
   sudo systemctl restart mongod
   ```

3. **定期更新**
   ```bash
   # 定期更新系统和依赖
   sudo apt update && sudo apt upgrade -y
   sudo -u scraper /opt/taiwan-pk10-scraper/venv/bin/pip install --upgrade -r requirements.txt
   ```

## 性能优化

1. **数据库索引**
   ```javascript
   // 在MongoDB中创建索引
   db.lottery_data.createIndex({"期号": 1})
   db.lottery_data.createIndex({"scrapedAt": 1})
   db.web_formatted_data.createIndex({"期号": 1})
   ```

2. **系统资源**
   ```bash
   # 调整系统参数
   echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
   echo 'net.core.somaxconn=65535' | sudo tee -a /etc/sysctl.conf
   sudo sysctl -p
   ```

## 备份和恢复

### 数据备份

```bash
#!/bin/bash
# 创建备份脚本 /opt/taiwan-pk10-scraper/backup.sh

BACKUP_DIR="/opt/backups/taiwan-pk10"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份MongoDB数据
mongodump --db taiwan_pk10 --out $BACKUP_DIR/mongodb_$DATE

# 备份配置文件
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /opt/taiwan-pk10-scraper/*.py /opt/taiwan-pk10-scraper/*.service

# 清理7天前的备份
find $BACKUP_DIR -name "*" -mtime +7 -delete

echo "备份完成: $BACKUP_DIR"
```

### 数据恢复

```bash
# 恢复MongoDB数据
mongorestore --db taiwan_pk10 /path/to/backup/mongodb_YYYYMMDD_HHMMSS/taiwan_pk10

# 恢复配置文件
tar -xzf /path/to/backup/config_YYYYMMDD_HHMMSS.tar.gz -C /
```

## 联系和支持

如果遇到问题，请检查：
1. 系统日志: `journalctl -u taiwan-pk10-scraper`
2. 应用日志: `/opt/taiwan-pk10-scraper/logs/`
3. MongoDB日志: `/var/log/mongodb/mongod.log`

---

**注意**: 请确保遵守相关法律法规，仅将此系统用于合法用途。