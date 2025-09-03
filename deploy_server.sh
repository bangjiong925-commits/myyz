#!/bin/bash

# 台湾PK10自动爬虫系统 - 服务器一键部署脚本
# 支持 Ubuntu/Debian 和 CentOS/RHEL 系统

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    else
        log_error "无法检测操作系统类型"
        exit 1
    fi
    
    log_info "检测到操作系统: $OS $VER"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "检测到root用户，建议使用普通用户运行此脚本"
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 安装基础依赖 - Ubuntu/Debian
install_deps_ubuntu() {
    log_info "更新系统包..."
    sudo apt update && sudo apt upgrade -y
    
    log_info "安装基础依赖..."
    sudo apt install -y python3 python3-pip git curl wget unzip gnupg lsb-release
    
    log_info "安装Chrome浏览器..."
    if ! command -v google-chrome &> /dev/null; then
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
        sudo apt update
        sudo apt install -y google-chrome-stable
    else
        log_success "Chrome浏览器已安装"
    fi
    
    log_info "安装MongoDB..."
    if ! command -v mongod &> /dev/null; then
        wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
        echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
        sudo apt update
        sudo apt install -y mongodb-org
    else
        log_success "MongoDB已安装"
    fi
}

# 安装基础依赖 - CentOS/RHEL
install_deps_centos() {
    log_info "更新系统包..."
    sudo yum update -y
    
    log_info "安装基础依赖..."
    sudo yum install -y python3 python3-pip git curl wget unzip
    
    log_info "安装Chrome浏览器..."
    if ! command -v google-chrome &> /dev/null; then
        sudo yum install -y https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
    else
        log_success "Chrome浏览器已安装"
    fi
    
    log_info "安装MongoDB..."
    if ! command -v mongod &> /dev/null; then
        cat > /tmp/mongodb-org-4.4.repo << EOF
[mongodb-org-4.4]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/\$releasever/mongodb-org/4.4/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-4.4.asc
EOF
        sudo mv /tmp/mongodb-org-4.4.repo /etc/yum.repos.d/
        sudo yum install -y mongodb-org
    else
        log_success "MongoDB已安装"
    fi
}

# 配置MongoDB
setup_mongodb() {
    log_info "配置MongoDB..."
    
    # 启动MongoDB服务
    sudo systemctl start mongod
    sudo systemctl enable mongod
    
    # 等待MongoDB启动
    sleep 5
    
    # 检查MongoDB状态
    if sudo systemctl is-active --quiet mongod; then
        log_success "MongoDB服务启动成功"
    else
        log_error "MongoDB服务启动失败"
        exit 1
    fi
    
    # 创建数据库和用户
    log_info "创建数据库用户..."
    
    # 生成随机密码
    ADMIN_PASSWORD=$(openssl rand -base64 32)
    APP_PASSWORD=$(openssl rand -base64 32)
    
    # 创建用户脚本
    cat > /tmp/create_users.js << EOF
// 创建管理员用户
use admin
db.createUser({
  user: "admin",
  pwd: "$ADMIN_PASSWORD",
  roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
})

// 创建应用数据库和用户
use taiwan_pk10
db.createUser({
  user: "pk10_user",
  pwd: "$APP_PASSWORD",
  roles: [ { role: "readWrite", db: "taiwan_pk10" } ]
})

// 创建索引
db.taiwan_pk10_data.createIndex({period: -1})
db.taiwan_pk10_data.createIndex({drawDate: -1})
db.taiwan_pk10_data.createIndex({"drawDate": -1, "period": -1})
EOF
    
    mongo < /tmp/create_users.js
    rm /tmp/create_users.js
    
    # 保存密码到文件
    cat > ~/.mongodb_credentials << EOF
MongoDB管理员账户:
用户名: admin
密码: $ADMIN_PASSWORD

应用账户:
用户名: pk10_user
密码: $APP_PASSWORD

MongoDB连接URI:
mongodb://pk10_user:$APP_PASSWORD@localhost:27017/taiwan_pk10
EOF
    
    chmod 600 ~/.mongodb_credentials
    
    log_success "MongoDB配置完成，凭据已保存到 ~/.mongodb_credentials"
    
    # 返回应用密码供后续使用
    echo $APP_PASSWORD
}

# 设置项目目录
setup_project() {
    local app_password=$1
    
    log_info "设置项目目录..."
    
    # 创建项目目录
    PROJECT_DIR="/opt/taiwan-pk10-scraper"
    sudo mkdir -p $PROJECT_DIR
    sudo chown $USER:$USER $PROJECT_DIR
    
    # 如果当前目录包含项目文件，复制到项目目录
    if [ -f "auto_scraper.py" ]; then
        log_info "复制项目文件到 $PROJECT_DIR"
        cp -r * $PROJECT_DIR/
    else
        log_warning "未找到项目文件，请手动将项目文件复制到 $PROJECT_DIR"
    fi
    
    cd $PROJECT_DIR
    
    # 创建必要目录
    mkdir -p data logs
    
    # 安装Python依赖
    log_info "安装Python依赖..."
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    else
        # 安装基本依赖
        pip3 install selenium beautifulsoup4 requests pymongo schedule python-dotenv
    fi
    
    # 创建环境配置文件
    log_info "创建环境配置文件..."
    cat > .env << EOF
# MongoDB配置
MONGODB_URI=mongodb://pk10_user:$app_password@localhost:27017/taiwan_pk10
MONGODB_DB_NAME=taiwan_pk10

# 爬虫配置
SCRAPER_INTERVAL=300
MAX_RETRIES=3
TIMEOUT=30

# 日志配置
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=7
EOF
    
    # 设置执行权限
    chmod +x *.py *.sh 2>/dev/null || true
    
    log_success "项目目录设置完成: $PROJECT_DIR"
}

# 测试系统
test_system() {
    log_info "测试系统功能..."
    
    cd $PROJECT_DIR
    
    # 测试MongoDB连接
    log_info "测试MongoDB连接..."
    if mongo taiwan_pk10 --eval "db.runCommand('ping').ok" --quiet; then
        log_success "MongoDB连接正常"
    else
        log_error "MongoDB连接失败"
        return 1
    fi
    
    # 测试爬虫脚本
    if [ -f "auto_scraper.py" ]; then
        log_info "测试爬虫脚本..."
        if timeout 60 python3 auto_scraper.py --mode single; then
            log_success "爬虫脚本测试成功"
            
            # 检查数据是否保存到数据库
            local count=$(mongo taiwan_pk10 --eval "db.taiwan_pk10_data.count()" --quiet)
            if [ "$count" -gt 0 ]; then
                log_success "数据成功保存到数据库，共 $count 条记录"
            else
                log_warning "数据库中暂无数据，可能需要等待下次抓取"
            fi
        else
            log_warning "爬虫脚本测试超时或失败，请检查网络连接"
        fi
    else
        log_warning "未找到爬虫脚本文件"
    fi
}

# 设置自动运行
setup_automation() {
    log_info "设置自动运行..."
    
    cd $PROJECT_DIR
    
    echo "请选择自动运行方式:"
    echo "1) Crontab定时任务 (推荐)"
    echo "2) Systemd服务"
    echo "3) 跳过自动设置"
    read -p "请输入选择 (1-3): " choice
    
    case $choice in
        1)
            setup_crontab
            ;;
        2)
            setup_systemd
            ;;
        3)
            log_info "跳过自动运行设置"
            ;;
        *)
            log_warning "无效选择，跳过自动运行设置"
            ;;
    esac
}

# 设置Crontab
setup_crontab() {
    log_info "设置Crontab定时任务..."
    
    # 备份现有crontab
    crontab -l > /tmp/crontab_backup 2>/dev/null || true
    
    # 添加新的cron任务
    (
        crontab -l 2>/dev/null || true
        echo "# Taiwan PK10 Auto Scraper"
        echo "*/5 * * * * cd $PROJECT_DIR && /usr/bin/python3 auto_scraper.py --mode single >> $PROJECT_DIR/logs/cron.log 2>&1"
        echo "# Clean old logs daily"
        echo "0 0 * * * find $PROJECT_DIR/logs -name '*.log' -mtime +7 -delete"
    ) | crontab -
    
    log_success "Crontab定时任务设置完成"
    log_info "任务将每5分钟执行一次数据抓取"
}

# 设置Systemd服务
setup_systemd() {
    log_info "设置Systemd服务..."
    
    # 创建服务文件
    sudo tee /etc/systemd/system/taiwan-pk10-scraper.service > /dev/null << EOF
[Unit]
Description=Taiwan PK10 Auto Scraper Service
After=network.target mongodb.service
Wants=mongodb.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 $PROJECT_DIR/auto_scraper.py --mode schedule
Restart=always
RestartSec=10
EnvironmentFile=$PROJECT_DIR/.env

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载systemd配置
    sudo systemctl daemon-reload
    
    # 启动并启用服务
    sudo systemctl start taiwan-pk10-scraper
    sudo systemctl enable taiwan-pk10-scraper
    
    # 检查服务状态
    if sudo systemctl is-active --quiet taiwan-pk10-scraper; then
        log_success "Systemd服务设置完成并已启动"
    else
        log_error "Systemd服务启动失败"
        sudo systemctl status taiwan-pk10-scraper
    fi
}

# 设置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    
    if command -v ufw &> /dev/null; then
        # Ubuntu/Debian UFW
        sudo ufw --force enable
        sudo ufw allow ssh
        sudo ufw deny 27017  # MongoDB端口
        log_success "UFW防火墙配置完成"
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL firewalld
        sudo systemctl start firewalld
        sudo systemctl enable firewalld
        sudo firewall-cmd --permanent --add-service=ssh
        sudo firewall-cmd --permanent --remove-port=27017/tcp
        sudo firewall-cmd --reload
        log_success "Firewalld防火墙配置完成"
    else
        log_warning "未检测到防火墙工具，请手动配置防火墙"
    fi
}

# 显示部署总结
show_summary() {
    log_success "\n=== 部署完成 ==="
    echo
    log_info "项目目录: $PROJECT_DIR"
    log_info "MongoDB凭据: ~/.mongodb_credentials"
    log_info "环境配置: $PROJECT_DIR/.env"
    log_info "日志目录: $PROJECT_DIR/logs"
    echo
    log_info "常用命令:"
    echo "  查看系统状态: cd $PROJECT_DIR && python3 check_auto_status.py"
    echo "  手动执行抓取: cd $PROJECT_DIR && python3 auto_scraper.py --mode single"
    echo "  查看MongoDB数据: mongo taiwan_pk10 --eval 'db.taiwan_pk10_data.find().limit(5).pretty()'"
    echo "  查看cron日志: tail -f $PROJECT_DIR/logs/cron.log"
    echo "  查看服务状态: sudo systemctl status taiwan-pk10-scraper"
    echo
    log_warning "重要提示:"
    echo "  1. MongoDB凭据已保存到 ~/.mongodb_credentials，请妥善保管"
    echo "  2. 系统将每5分钟自动抓取一次数据"
    echo "  3. 建议定期备份MongoDB数据库"
    echo "  4. 如需API服务，请手动启动 api_server.py"
    echo
}

# 主函数
main() {
    echo "=== 台湾PK10自动爬虫系统 - 服务器部署脚本 ==="
    echo
    
    # 检查系统
    check_root
    detect_os
    
    # 安装依赖
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        install_deps_ubuntu
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        install_deps_centos
    else
        log_error "不支持的操作系统: $OS"
        exit 1
    fi
    
    # 配置MongoDB并获取密码
    app_password=$(setup_mongodb)
    
    # 设置项目
    setup_project "$app_password"
    
    # 测试系统
    test_system
    
    # 设置自动运行
    setup_automation
    
    # 配置防火墙
    setup_firewall
    
    # 显示总结
    show_summary
    
    log_success "部署完成！系统已准备就绪。"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"