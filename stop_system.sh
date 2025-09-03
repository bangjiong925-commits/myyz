#!/bin/bash

# 台湾PK10自动爬虫系统停止脚本
# 用于安全停止整个系统

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

# 停止进程函数
stop_process() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            log_info "停止 $service_name (PID: $pid)..."
            kill $pid
            
            # 等待进程停止
            local count=0
            while kill -0 $pid 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # 如果进程仍在运行，强制杀死
            if kill -0 $pid 2>/dev/null; then
                log_warning "强制停止 $service_name..."
                kill -9 $pid 2>/dev/null || true
            fi
            
            log_success "$service_name 已停止"
        else
            log_warning "$service_name 进程不存在 (PID: $pid)"
        fi
        
        # 删除PID文件
        rm -f "$pid_file"
    else
        log_info "$service_name PID文件不存在，可能未运行"
    fi
}

# 停止API服务器
stop_api_server() {
    log_info "停止API服务器..."
    stop_process "logs/api_server.pid" "API服务器"
    
    # 额外检查端口占用
    local api_pids=$(lsof -ti:3000 2>/dev/null || true)
    if [ -n "$api_pids" ]; then
        log_warning "发现端口3000仍被占用，强制停止相关进程..."
        echo $api_pids | xargs kill -9 2>/dev/null || true
    fi
}

# 停止自动爬虫
stop_auto_scraper() {
    log_info "停止自动爬虫..."
    stop_process "logs/auto_scraper.pid" "自动爬虫"
    
    # 停止所有相关的Python进程
    local scraper_pids=$(pgrep -f "auto_scraper.py" 2>/dev/null || true)
    if [ -n "$scraper_pids" ]; then
        log_warning "发现其他爬虫进程，正在停止..."
        echo $scraper_pids | xargs kill 2>/dev/null || true
        sleep 2
        
        # 强制停止仍在运行的进程
        scraper_pids=$(pgrep -f "auto_scraper.py" 2>/dev/null || true)
        if [ -n "$scraper_pids" ]; then
            echo $scraper_pids | xargs kill -9 2>/dev/null || true
        fi
    fi
}

# 停止MongoDB（可选）
stop_mongodb() {
    if [ "$1" = "--with-mongodb" ]; then
        log_info "停止MongoDB服务..."
        
        if command -v systemctl &> /dev/null; then
            if systemctl is-active --quiet mongod; then
                sudo systemctl stop mongod
                log_success "MongoDB服务已停止"
            else
                log_info "MongoDB服务未运行"
            fi
        elif command -v service &> /dev/null; then
            sudo service mongod stop 2>/dev/null || log_info "MongoDB服务未运行"
        else
            # 手动停止MongoDB进程
            local mongo_pids=$(pgrep mongod 2>/dev/null || true)
            if [ -n "$mongo_pids" ]; then
                log_info "停止MongoDB进程..."
                echo $mongo_pids | xargs kill 2>/dev/null || true
                sleep 3
                
                # 检查是否还在运行
                mongo_pids=$(pgrep mongod 2>/dev/null || true)
                if [ -n "$mongo_pids" ]; then
                    log_warning "强制停止MongoDB进程..."
                    echo $mongo_pids | xargs kill -9 2>/dev/null || true
                fi
                log_success "MongoDB进程已停止"
            else
                log_info "MongoDB进程未运行"
            fi
        fi
    fi
}

# 清理临时文件
cleanup_temp_files() {
    log_info "清理临时文件..."
    
    # 清理PID文件
    rm -f logs/*.pid
    
    # 清理Chrome临时文件（如果存在）
    if [ -d "/tmp/chrome_temp" ]; then
        rm -rf /tmp/chrome_temp
    fi
    
    # 清理Selenium临时文件
    find /tmp -name "*chrome*" -type d -user $(whoami) -exec rm -rf {} + 2>/dev/null || true
    find /tmp -name "*selenium*" -type d -user $(whoami) -exec rm -rf {} + 2>/dev/null || true
    
    log_success "临时文件清理完成"
}

# 显示最终状态
show_final_status() {
    echo
    log_info "=== 停止后状态检查 ==="
    
    # 检查API服务器
    local api_pids=$(lsof -ti:3000 2>/dev/null || true)
    if [ -z "$api_pids" ]; then
        log_success "API服务器已完全停止"
    else
        log_error "API服务器可能仍在运行 (端口3000被占用)"
    fi
    
    # 检查爬虫进程
    local scraper_pids=$(pgrep -f "auto_scraper.py" 2>/dev/null || true)
    if [ -z "$scraper_pids" ]; then
        log_success "自动爬虫已完全停止"
    else
        log_error "自动爬虫可能仍在运行"
    fi
    
    # 检查MongoDB（如果要求停止）
    if [ "$1" = "--with-mongodb" ]; then
        if pgrep mongod > /dev/null; then
            log_warning "MongoDB仍在运行"
        else
            log_success "MongoDB已停止"
        fi
    fi
    
    echo
    log_info "=== 重启命令 ==="
    echo "重新启动系统: ./start_system.sh"
    echo "查看日志文件: ls -la logs/"
    echo
}

# 主函数
main() {
    echo "=== 台湾PK10自动爬虫系统停止脚本 ==="
    echo
    
    # 检查是否在正确目录
    if [ ! -f "auto_scraper.py" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 创建logs目录（如果不存在）
    mkdir -p logs
    
    # 解析参数
    local with_mongodb=false
    if [ "$1" = "--with-mongodb" ] || [ "$1" = "-m" ]; then
        with_mongodb=true
    fi
    
    # 停止服务
    stop_api_server
    stop_auto_scraper
    
    if [ "$with_mongodb" = true ]; then
        stop_mongodb "--with-mongodb"
    fi
    
    cleanup_temp_files
    
    if [ "$with_mongodb" = true ]; then
        show_final_status "--with-mongodb"
    else
        show_final_status
    fi
    
    log_success "系统停止完成！"
    
    if [ "$with_mongodb" = false ]; then
        echo
        log_info "提示: 如需同时停止MongoDB，请使用: $0 --with-mongodb"
    fi
}

# 显示帮助信息
show_help() {
    echo "台湾PK10自动爬虫系统停止脚本"
    echo
    echo "用法:"
    echo "  $0                    # 停止爬虫和API服务器"
    echo "  $0 --with-mongodb    # 同时停止MongoDB服务"
    echo "  $0 -m                # 同时停止MongoDB服务（简写）"
    echo "  $0 --help            # 显示此帮助信息"
    echo
    echo "说明:"
    echo "  默认情况下只停止爬虫和API服务器，不会停止MongoDB"
    echo "  如果需要完全停止所有服务，请使用 --with-mongodb 参数"
    echo
}

# 处理命令行参数
case "$1" in
    --help|-h)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac