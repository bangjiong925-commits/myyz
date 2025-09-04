#!/bin/bash

# 自动抓取服务管理脚本
# 用法: ./start_auto_scraper.sh [start|stop|status|restart]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/auto_scraper.pid"
LOG_FILE="$SCRIPT_DIR/logs/auto_scraper_service.log"
PYTHON_SCRIPT="$SCRIPT_DIR/auto_scraper.py"

# 确保日志目录存在
mkdir -p "$SCRIPT_DIR/logs"

# 获取当前时间
get_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# 记录日志
log_message() {
    echo "[$(get_timestamp)] $1" | tee -a "$LOG_FILE"
}

# 检查服务状态
check_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "自动抓取服务正在运行 (PID: $PID)"
            return 0
        else
            echo "PID文件存在但进程不在运行，清理PID文件"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        echo "自动抓取服务未运行"
        return 1
    fi
}

# 启动服务
start_service() {
    if check_status > /dev/null 2>&1; then
        echo "自动抓取服务已在运行"
        return 1
    fi
    
    log_message "启动自动抓取服务..."
    
    # 使用智能调度模式启动
    cd "$SCRIPT_DIR"
    nohup python3 "$PYTHON_SCRIPT" --mode smart > "$LOG_FILE" 2>&1 &
    PID=$!
    
    # 保存PID
    echo $PID > "$PID_FILE"
    
    # 等待一下确认启动成功
    sleep 3
    
    if ps -p "$PID" > /dev/null 2>&1; then
        log_message "自动抓取服务启动成功 (PID: $PID)"
        echo "自动抓取服务启动成功 (PID: $PID)"
        echo "日志文件: $LOG_FILE"
        return 0
    else
        log_message "自动抓取服务启动失败"
        echo "自动抓取服务启动失败，请检查日志: $LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

# 停止服务
stop_service() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log_message "停止自动抓取服务 (PID: $PID)..."
            kill "$PID"
            
            # 等待进程结束
            for i in {1..10}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    break
                fi
                sleep 1
            done
            
            # 如果进程仍在运行，强制杀死
            if ps -p "$PID" > /dev/null 2>&1; then
                log_message "强制停止自动抓取服务"
                kill -9 "$PID"
            fi
            
            rm -f "$PID_FILE"
            log_message "自动抓取服务已停止"
            echo "自动抓取服务已停止"
        else
            echo "进程不在运行，清理PID文件"
            rm -f "$PID_FILE"
        fi
    else
        echo "自动抓取服务未运行"
    fi
}

# 重启服务
restart_service() {
    echo "重启自动抓取服务..."
    stop_service
    sleep 2
    start_service
}

# 显示日志
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo "=== 最近50行日志 ==="
        tail -n 50 "$LOG_FILE"
    else
        echo "日志文件不存在: $LOG_FILE"
    fi
}

# 主逻辑
case "${1:-start}" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    status)
        check_status
        ;;
    restart)
        restart_service
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "用法: $0 {start|stop|status|restart|logs}"
        echo "  start   - 启动自动抓取服务"
        echo "  stop    - 停止自动抓取服务"
        echo "  status  - 检查服务状态"
        echo "  restart - 重启服务"
        echo "  logs    - 显示最近日志"
        exit 1
        ;;
esac

exit $?