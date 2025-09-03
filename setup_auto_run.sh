#!/bin/bash
# 台湾PK10自动爬虫设置脚本

echo "=== 台湾PK10自动爬虫设置 ==="
echo

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "项目目录: $SCRIPT_DIR"

# 检查Python依赖
echo "检查Python依赖..."
if ! python3 -c "import schedule, selenium, pymongo, loguru" 2>/dev/null; then
    echo "警告: 缺少必要的Python依赖包"
    echo "请运行: pip3 install -r requirements.txt"
    echo
fi

# 显示可用的自动运行选项
echo "可用的自动运行选项:"
echo
echo "1. 使用crontab定时任务 (推荐)"
echo "   - 每5分钟自动执行一次"
echo "   - 系统重启后自动恢复"
echo "   - 适合生产环境"
echo
echo "2. 使用内置调度器"
echo "   - Python脚本持续运行"
echo "   - 每5分钟自动执行"
echo "   - 需要手动启动"
echo
echo "3. 手动执行"
echo "   - 仅执行一次数据抓取"
echo "   - 适合测试和调试"
echo

# 用户选择
read -p "请选择运行方式 (1/2/3): " choice

case $choice in
    1)
        echo "设置crontab定时任务..."
        # 创建crontab条目
        CRON_JOB="*/5 * * * * cd $SCRIPT_DIR && /usr/bin/python3 auto_scraper.py --mode single >> $SCRIPT_DIR/logs/cron.log 2>&1"
        
        # 检查是否已存在相同的任务
        if crontab -l 2>/dev/null | grep -q "auto_scraper.py"; then
            echo "检测到已存在的crontab任务"
            read -p "是否要替换现有任务? (y/n): " replace
            if [[ $replace == "y" || $replace == "Y" ]]; then
                # 移除旧任务并添加新任务
                (crontab -l 2>/dev/null | grep -v "auto_scraper.py"; echo "$CRON_JOB") | crontab -
                echo "crontab任务已更新"
            else
                echo "保持现有crontab任务不变"
            fi
        else
            # 添加新任务
            (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
            echo "crontab任务已添加"
        fi
        
        echo "当前crontab任务:"
        crontab -l | grep "auto_scraper.py" || echo "未找到相关任务"
        echo
        echo "日志文件位置: $SCRIPT_DIR/logs/cron.log"
        echo "查看日志: tail -f $SCRIPT_DIR/logs/cron.log"
        ;;
        
    2)
        echo "启动内置调度器..."
        echo "注意: 此模式将持续运行，按Ctrl+C停止"
        echo "日志将显示在终端中"
        echo
        read -p "按Enter键开始，或Ctrl+C取消..."
        cd "$SCRIPT_DIR"
        python3 auto_scraper.py --mode schedule
        ;;
        
    3)
        echo "执行单次数据抓取..."
        cd "$SCRIPT_DIR"
        python3 auto_scraper.py --mode single
        echo "单次抓取完成"
        ;;
        
    *)
        echo "无效选择，退出"
        exit 1
        ;;
esac

echo
echo "=== 设置完成 ==="
echo "数据文件位置: $SCRIPT_DIR/data/"
echo "日志文件位置: $SCRIPT_DIR/logs/"
echo "查看最新数据: python3 show_data.py"
echo