#!/bin/bash
# Taiwan PK10 自动爬虫系统部署脚本

set -e  # 遇到错误时退出

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

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        log_info "请使用: sudo $0"
        exit 1
    fi
}

# 检测操作系统
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        log_error "无法检测操作系统"
        exit 1
    fi
    log_info "检测到操作系统: $OS $VER"
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        apt update
        apt install -y python3 python3-pip python3-venv mongodb curl wget git cron
        systemctl enable mongod
        systemctl start mongod
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        yum update -y
        yum install -y python3 python3-pip mongodb-server curl wget git cronie
        systemctl enable mongod
        systemctl start mongod
        systemctl enable crond
        systemctl start crond
    else
        log_warning "未识别的操作系统，请手动安装依赖"
    fi
    
    log_success "系统依赖安装完成"
}

# 创建项目目录和用户
setup_project() {
    log_info "设置项目环境..."
    
    # 创建项目目录
    PROJECT_DIR="/opt/taiwan-pk10-scraper"
    mkdir -p $PROJECT_DIR
    
    # 创建专用用户（如果不存在）
    if ! id "scraper" &>/dev/null; then
        useradd -r -s /bin/false -d $PROJECT_DIR scraper
        log_info "创建用户: scraper"
    fi
    
    # 复制项目文件
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cp -r $SCRIPT_DIR/* $PROJECT_DIR/
    
    # 设置权限
    chown -R scraper:scraper $PROJECT_DIR
    chmod +x $PROJECT_DIR/auto_scraper.py
    
    # 创建日志目录
    mkdir -p $PROJECT_DIR/logs
    mkdir -p $PROJECT_DIR/data
    chown -R scraper:scraper $PROJECT_DIR/logs
    chown -R scraper:scraper $PROJECT_DIR/data
    
    log_success "项目环境设置完成"
}

# 安装Python依赖
install_python_deps() {
    log_info "安装Python依赖..."
    
    cd $PROJECT_DIR
    
    # 创建虚拟环境
    python3 -m venv venv
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
    else
        # 手动安装主要依赖
        pip install selenium pymongo schedule requests beautifulsoup4 flask flask-cors
    fi
    
    log_success "Python依赖安装完成"
}

# 配置MongoDB
setup_mongodb() {
    log_info "配置MongoDB..."
    
    # 确保MongoDB正在运行
    systemctl start mongod
    systemctl enable mongod
    
    # 等待MongoDB启动
    sleep 5
    
    # 创建数据库和集合（可选）
    mongo taiwan_pk10 --eval "db.createCollection('lottery_data')"
    mongo taiwan_pk10 --eval "db.createCollection('web_formatted_data')"
    
    log_success "MongoDB配置完成"
}

# 设置systemd服务
setup_systemd_service() {
    log_info "设置systemd服务..."
    
    # 修改服务文件中的路径
    sed -i "s|/opt/taiwan-pk10-scraper|$PROJECT_DIR|g" $PROJECT_DIR/taiwan-pk10-scraper.service
    sed -i "s|/usr/bin/python3|$PROJECT_DIR/venv/bin/python|g" $PROJECT_DIR/taiwan-pk10-scraper.service
    sed -i "s|User=www-data|User=scraper|g" $PROJECT_DIR/taiwan-pk10-scraper.service
    sed -i "s|Group=www-data|Group=scraper|g" $PROJECT_DIR/taiwan-pk10-scraper.service
    
    # 复制服务文件
    cp $PROJECT_DIR/taiwan-pk10-scraper.service /etc/systemd/system/
    
    # 重新加载systemd
    systemctl daemon-reload
    
    # 启用并启动服务
    systemctl enable taiwan-pk10-scraper
    systemctl start taiwan-pk10-scraper
    
    log_success "systemd服务设置完成"
}

# 设置cron任务（备选方案）
setup_cron() {
    log_info "设置cron任务（备选方案）..."
    
    # 为scraper用户添加cron任务
    CRON_JOB="*/5 * * * * cd $PROJECT_DIR && $PROJECT_DIR/venv/bin/python auto_scraper.py --mode single >> $PROJECT_DIR/logs/cron.log 2>&1"
    
    # 添加到scraper用户的crontab
    (crontab -u scraper -l 2>/dev/null; echo "$CRON_JOB") | crontab -u scraper -
    
    log_success "cron任务设置完成"
}

# 启动API服务器
setup_api_server() {
    log_info "设置API服务器..."
    
    # 创建API服务器的systemd服务文件
    cat > /etc/systemd/system/taiwan-pk10-api.service << EOF
[Unit]
Description=Taiwan PK10 MongoDB API Server
After=network.target mongodb.service
Wants=mongodb.service

[Service]
Type=simple
User=scraper
Group=scraper
WorkingDirectory=$PROJECT_DIR
Environment=PYTHONPATH=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/mongodb_api.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=taiwan-pk10-api

[Install]
WantedBy=multi-user.target
EOF

    # 启用并启动API服务
    systemctl daemon-reload
    systemctl enable taiwan-pk10-api
    systemctl start taiwan-pk10-api
    
    log_success "API服务器设置完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    echo "MongoDB状态:"
    systemctl status mongod --no-pager -l
    
    echo "\n爬虫服务状态:"
    systemctl status taiwan-pk10-scraper --no-pager -l
    
    echo "\nAPI服务状态:"
    systemctl status taiwan-pk10-api --no-pager -l
    
    echo "\n端口监听状态:"
    netstat -tlnp | grep -E ':(27017|5000)'
}

# 显示使用说明
show_usage() {
    log_success "部署完成！"
    echo ""
    echo "服务管理命令:"
    echo "  查看爬虫服务状态: systemctl status taiwan-pk10-scraper"
    echo "  查看API服务状态:  systemctl status taiwan-pk10-api"
    echo "  查看服务日志:     journalctl -u taiwan-pk10-scraper -f"
    echo "  重启爬虫服务:     systemctl restart taiwan-pk10-scraper"
    echo "  重启API服务:      systemctl restart taiwan-pk10-api"
    echo ""
    echo "API端点:"
    echo "  今日数据: http://localhost:5000/api/today-data"
    echo "  最新数据: http://localhost:5000/api/latest-data"
    echo "  健康检查: http://localhost:5000/api/health"
    echo ""
    echo "日志文件位置:"
    echo "  爬虫日志: $PROJECT_DIR/logs/"
    echo "  系统日志: journalctl -u taiwan-pk10-scraper"
    echo ""
}

# 主函数
main() {
    log_info "开始部署Taiwan PK10自动爬虫系统..."
    
    check_root
    detect_os
    install_system_deps
    setup_project
    install_python_deps
    setup_mongodb
    setup_systemd_service
    setup_api_server
    
    # 等待服务启动
    sleep 10
    
    check_services
    show_usage
    
    log_success "部署完成！系统已开始自动运行。"
}

# 如果直接运行此脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi