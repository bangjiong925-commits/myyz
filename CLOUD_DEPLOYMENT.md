# 云服务器部署指南 - 台湾PK10自动爬虫系统

本指南提供在主流云服务商上快速部署台湾PK10自动爬虫系统的步骤。

## 🚀 一键部署

### 快速开始

1. **获取服务器**（选择任一云服务商）
2. **连接服务器**
3. **运行部署脚本**：
   ```bash
   # 下载项目文件到服务器
   git clone <your-repository-url>
   cd taiwan-pk10-scraper
   
   # 运行一键部署脚本
   ./deploy_server.sh
   ```

## ☁️ 云服务商部署指南

### 1. 阿里云 ECS

#### 服务器配置推荐
- **实例规格**: ecs.t5-lc1m2.small (1核2GB) 或更高
- **操作系统**: Ubuntu 20.04 LTS
- **存储**: 40GB SSD云盘
- **网络**: 按量付费，1Mbps带宽

#### 部署步骤
```bash
# 1. 连接服务器
ssh root@your-server-ip

# 2. 创建普通用户（推荐）
adduser pk10user
usermod -aG sudo pk10user
su - pk10user

# 3. 下载并部署
wget https://github.com/your-username/taiwan-pk10-scraper/archive/main.zip
unzip main.zip
cd taiwan-pk10-scraper-main
./deploy_server.sh
```

#### 安全组配置
- **入方向规则**:
  - SSH: 22/TCP (限制来源IP)
  - 自定义: 3000/TCP (如需API访问)

### 2. 腾讯云 CVM

#### 服务器配置推荐
- **实例规格**: S5.SMALL2 (1核2GB)
- **操作系统**: Ubuntu Server 20.04 LTS
- **存储**: 50GB高性能云硬盘
- **网络**: 按量计费，1Mbps带宽

#### 部署步骤
```bash
# 1. 连接服务器
ssh ubuntu@your-server-ip

# 2. 更新系统
sudo apt update && sudo apt upgrade -y

# 3. 下载并部署
git clone https://github.com/your-username/taiwan-pk10-scraper.git
cd taiwan-pk10-scraper
./deploy_server.sh
```

#### 安全组配置
- **入站规则**:
  - SSH: 22 (限制来源)
  - HTTP: 3000 (如需API)

### 3. 华为云 ECS

#### 服务器配置推荐
- **规格**: s6.small.1 (1核2GB)
- **镜像**: Ubuntu 20.04 server 64bit
- **磁盘**: 40GB SSD云硬盘
- **带宽**: 1Mbps

#### 部署步骤
```bash
# 1. 连接服务器
ssh root@your-server-ip

# 2. 安装Git
apt update && apt install -y git

# 3. 下载并部署
git clone https://github.com/your-username/taiwan-pk10-scraper.git
cd taiwan-pk10-scraper
./deploy_server.sh
```

### 4. AWS EC2

#### 实例配置推荐
- **实例类型**: t3.micro (1核1GB) 或 t3.small (1核2GB)
- **AMI**: Ubuntu Server 20.04 LTS
- **存储**: 20GB gp3
- **安全组**: 自定义

#### 部署步骤
```bash
# 1. 连接服务器
ssh -i your-key.pem ubuntu@your-server-ip

# 2. 下载并部署
git clone https://github.com/your-username/taiwan-pk10-scraper.git
cd taiwan-pk10-scraper
./deploy_server.sh
```

#### 安全组规则
- **入站规则**:
  - SSH: 22 (限制IP)
  - Custom TCP: 3000 (可选)

### 5. Google Cloud Platform (GCP)

#### 实例配置推荐
- **机器类型**: e2-small (1核2GB)
- **操作系统**: Ubuntu 20.04 LTS
- **磁盘**: 20GB 标准永久磁盘
- **网络**: 默认

#### 部署步骤
```bash
# 1. 通过SSH连接
gcloud compute ssh your-instance-name

# 2. 下载并部署
git clone https://github.com/your-username/taiwan-pk10-scraper.git
cd taiwan-pk10-scraper
./deploy_server.sh
```

#### 防火墙规则
```bash
# 创建防火墙规则（如需API访问）
gcloud compute firewall-rules create allow-pk10-api \
    --allow tcp:3000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow PK10 API access"
```

### 6. DigitalOcean Droplet

#### Droplet配置推荐
- **大小**: Basic - $6/月 (1GB RAM, 1 vCPU)
- **镜像**: Ubuntu 20.04 (LTS) x64
- **数据中心**: 选择最近的区域

#### 部署步骤
```bash
# 1. 连接服务器
ssh root@your-droplet-ip

# 2. 创建用户
adduser pk10user
usermod -aG sudo pk10user
su - pk10user

# 3. 下载并部署
git clone https://github.com/your-username/taiwan-pk10-scraper.git
cd taiwan-pk10-scraper
./deploy_server.sh
```

## 🔧 部署后配置

### 1. 验证部署

```bash
# 检查系统状态
cd /opt/taiwan-pk10-scraper
python3 check_auto_status.py

# 查看MongoDB数据
mongo taiwan_pk10 --eval "db.taiwan_pk10_data.find().limit(5).pretty()"

# 检查定时任务
crontab -l

# 查看日志
tail -f logs/cron.log
```

### 2. 性能优化

```bash
# 调整系统参数
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'net.core.rmem_max=16777216' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# 设置时区
sudo timedatectl set-timezone Asia/Shanghai

# 优化MongoDB
mongo taiwan_pk10 --eval "db.taiwan_pk10_data.createIndex({period: -1, drawDate: -1})"
```

### 3. 监控设置

```bash
# 安装监控工具
sudo apt install -y htop iotop nethogs

# 设置系统监控脚本
cat > /opt/taiwan-pk10-scraper/monitor.sh << 'EOF'
#!/bin/bash
echo "=== 系统状态监控 $(date) ==="
echo "CPU使用率:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
echo "内存使用:"
free -h
echo "磁盘使用:"
df -h /
echo "MongoDB状态:"
sudo systemctl is-active mongod
echo "最新数据:"
mongo taiwan_pk10 --eval "db.taiwan_pk10_data.find().sort({period: -1}).limit(1).pretty()" --quiet
EOF

chmod +x /opt/taiwan-pk10-scraper/monitor.sh

# 添加监控定时任务
(crontab -l; echo "0 */6 * * * /opt/taiwan-pk10-scraper/monitor.sh >> /opt/taiwan-pk10-scraper/logs/monitor.log 2>&1") | crontab -
```

## 📊 成本估算

### 月度成本预估（人民币）

| 云服务商 | 配置 | 月费用 | 备注 |
|---------|------|--------|------|
| 阿里云 | 1核2GB | ¥30-50 | 新用户有优惠 |
| 腾讯云 | 1核2GB | ¥25-45 | 学生优惠可用 |
| 华为云 | 1核2GB | ¥35-55 | 企业用户优惠 |
| AWS | t3.micro | ¥0-70 | 免费套餐12个月 |
| GCP | e2-small | ¥40-60 | 新用户$300额度 |
| DigitalOcean | 1GB | ¥40 | 固定价格 |

### 成本优化建议

1. **选择合适的配置**: 1核2GB足够运行系统
2. **利用新用户优惠**: 大部分云服务商都有新用户折扣
3. **按量付费**: 对于测试环境，选择按量付费更经济
4. **定期清理**: 清理旧日志和数据文件
5. **监控使用量**: 设置费用告警，避免超支

## 🔒 安全最佳实践

### 1. 服务器安全

```bash
# 禁用root登录
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# 设置SSH密钥登录
ssh-keygen -t rsa -b 4096
# 将公钥添加到 ~/.ssh/authorized_keys

# 安装fail2ban防止暴力破解
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
```

### 2. 数据库安全

```bash
# 启用MongoDB认证
sudo sed -i 's/#security:/security:\n  authorization: enabled/' /etc/mongod.conf
sudo systemctl restart mongod

# 定期备份数据
mkdir -p /backup/mongodb
echo "0 2 * * * mongodump --db taiwan_pk10 --out /backup/mongodb/\$(date +\%Y\%m\%d)" | crontab -
```

### 3. 网络安全

```bash
# 配置防火墙
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
# 只在需要时开放API端口
# sudo ufw allow 3000
```

## 🚨 故障排除

### 常见问题

1. **Chrome浏览器无法启动**
   ```bash
   # 安装缺失依赖
   sudo apt install -y libnss3 libgconf-2-4 libxss1 libappindicator1
   ```

2. **MongoDB连接失败**
   ```bash
   # 检查服务状态
   sudo systemctl status mongod
   # 查看日志
   sudo tail -f /var/log/mongodb/mongod.log
   ```

3. **内存不足**
   ```bash
   # 创建交换文件
   sudo fallocate -l 1G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

4. **网络连接问题**
   ```bash
   # 测试网络连接
   curl -I https://www.taiwanlottery.com.tw
   # 检查DNS
   nslookup www.taiwanlottery.com.tw
   ```

### 日志查看

```bash
# 系统日志
sudo journalctl -u taiwan-pk10-scraper -f

# 应用日志
tail -f /opt/taiwan-pk10-scraper/logs/cron.log

# MongoDB日志
sudo tail -f /var/log/mongodb/mongod.log

# 系统日志
sudo tail -f /var/log/syslog
```

## 📞 技术支持

如果在部署过程中遇到问题：

1. **检查部署日志**: 部署脚本会输出详细的错误信息
2. **查看系统日志**: 使用上述日志查看命令
3. **验证网络连接**: 确保服务器可以访问目标网站
4. **检查系统资源**: 确保有足够的内存和磁盘空间

---

**部署完成后，系统将自动每5分钟抓取一次台湾PK10开奖数据并保存到MongoDB数据库中。**

**推荐配置**: 阿里云或腾讯云的1核2GB实例，月费用约30-50元，性价比最高。