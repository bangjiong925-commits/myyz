#!/bin/bash

# 台湾PK10自动爬虫系统启动脚本
# 用于快速启动整个系统

set -e

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

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装"
        exit 1
    fi
    
    # 检查MongoDB（可选）
    if command -v mongod &> /dev/null; then
        log_success "MongoDB 已安装"
        MONGODB_AVAILABLE=true
    else
        log_warning "MongoDB 未安装，将使用文件存储"
        MONGODB_AVAILABLE=false
    fi
    
    log_success "依赖检查完成"
}

# 安装Python依赖
install_python_deps() {
    log_info "安装Python依赖包..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        log_success "Python依赖安装完成"
    else
        log_warning "requirements.txt 不存在，跳过依赖安装"
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p data
    mkdir -p logs
    
    log_success "目录创建完成"
}

# 启动MongoDB（如果可用）
start_mongodb() {
    if [ "$MONGODB_AVAILABLE" = true ]; then
        log_info "启动MongoDB服务..."
        
        # 检查MongoDB是否已经运行
        if pgrep mongod > /dev/null; then
            log_success "MongoDB 已在运行"
        else
            # 尝试启动MongoDB
            if command -v systemctl &> /dev/null; then
                sudo systemctl start mongod
            elif command -v service &> /dev/null; then
                sudo service mongod start
            else
                mongod --fork --logpath /var/log/mongodb/mongod.log
            fi
            
            # 等待MongoDB启动
            sleep 3
            
            if pgrep mongod > /dev/null; then
                log_success "MongoDB 启动成功"
            else
                log_error "MongoDB 启动失败"
                MONGODB_AVAILABLE=false
            fi
        fi
    fi
}

# 测试系统
test_system() {
    log_info "测试系统功能..."
    
    # 测试爬虫脚本
    if [ -f "auto_scraper.py" ]; then
        log_info "测试爬虫脚本..."
        if python3 auto_scraper.py --mode single --test; then
            log_success "爬虫脚本测试通过"
        else
            log_warning "爬虫脚本测试失败，但系统仍可继续运行"
        fi
    fi
    
    # 检查数据文件
    if [ -f "data/latest_taiwan_pk10_data.json" ]; then
        log_success "数据文件存在"
    else
        log_warning "数据文件不存在，将在首次运行时创建"
    fi
}

# 启动服务
start_services() {
    log_info "启动系统服务..."
    
    # 启动API服务器（后台运行）
    if [ -f "api_server.py" ]; then
        log_info "启动API服务器..."
        nohup python3 api_server.py --port 3000 > logs/api_server.log 2>&1 &
        API_PID=$!
        echo $API_PID > logs/api_server.pid
        log_success "API服务器已启动 (PID: $API_PID)"
    fi
    
    # 启动自动爬虫（后台运行）
    if [ -f "auto_scraper.py" ]; then
        log_info "启动自动爬虫..."
        
        if [ "$MONGODB_AVAILABLE" = true ]; then
            # 使用MongoDB
            nohup python3 auto_scraper.py --mode schedule --mongodb-uri "mongodb://localhost:27017" --database taiwan_pk10 > logs/auto_scraper.log 2>&1 &
        else
            # 使用文件存储
            nohup python3 auto_scraper.py --mode schedule > logs/auto_scraper.log 2>&1 &
        fi
        
        SCRAPER_PID=$!
        echo $SCRAPER_PID > logs/auto_scraper.pid
        log_success "自动爬虫已启动 (PID: $SCRAPER_PID)"
    fi
    
    # 等待服务启动
    sleep 2
}

# 显示状态
show_status() {
    echo
    log_info "=== 系统状态 ==="
    
    # API服务器状态
    if [ -f "logs/api_server.pid" ]; then
        API_PID=$(cat logs/api_server.pid)
        if kill -0 $API_PID 2>/dev/null; then
            log_success "API服务器运行中 (PID: $API_PID)"
            log_info "访问地址: http://localhost:3000"
        else
            log_error "API服务器未运行"
        fi
    fi
    
    # 爬虫状态
    if [ -f "logs/auto_scraper.pid" ]; then
        SCRAPER_PID=$(cat logs/auto_scraper.pid)
        if kill -0 $SCRAPER_PID 2>/dev/null; then
            log_success "自动爬虫运行中 (PID: $SCRAPER_PID)"
        else
            log_error "自动爬虫未运行"
        fi
    fi
    
    # MongoDB状态
    if [ "$MONGODB_AVAILABLE" = true ]; then
        if pgrep mongod > /dev/null; then
            log_success "MongoDB运行中"
        else
            log_error "MongoDB未运行"
        fi
    fi
    
    # 数据文件状态
    if [ -f "data/latest_taiwan_pk10_data.json" ]; then
        RECORD_COUNT=$(python3 -c "import json; data=json.load(open('data/latest_taiwan_pk10_data.json')); print(len(data))" 2>/dev/null || echo "0")
        log_success "数据文件存在，包含 $RECORD_COUNT 条记录"
    else
        log_warning "数据文件不存在"
    fi
    
    echo
    log_info "=== 管理命令 ==="
    echo "停止系统: ./stop_system.sh"
    echo "查看状态: python3 check_auto_status.py"
    echo "查看日志: tail -f logs/auto_scraper.log"
    echo "访问界面: http://localhost:3000"
    echo
}

# 主函数
main() {
    echo "=== 台湾PK10自动爬虫系统启动脚本 ==="
    echo
    
    # 检查是否在正确目录
    if [ ! -f "auto_scraper.py" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    check_dependencies
    install_python_deps
    create_directories
    start_mongodb
    test_system
    start_services
    show_status
    
    log_success "系统启动完成！"
}

# 处理中断信号
trap 'log_warning "收到中断信号，正在停止..."; exit 1' INT TERM

# 运行主函数
main "$@"