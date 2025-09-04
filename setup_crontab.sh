#!/bin/bash

# 设置crontab定时任务脚本
# 用于确保自动抓取服务在系统重启后自动启动

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
START_SCRIPT="$SCRIPT_DIR/start_auto_scraper.sh"
TEMP_CRON="/tmp/myyz_crontab_temp"

echo "设置自动抓取服务的定时任务..."

# 检查启动脚本是否存在
if [ ! -f "$START_SCRIPT" ]; then
    echo "错误: 启动脚本不存在: $START_SCRIPT"
    exit 1
fi

# 获取当前crontab内容（如果存在）
crontab -l > "$TEMP_CRON" 2>/dev/null || touch "$TEMP_CRON"

# 检查是否已经存在相关的cron任务
if grep -q "start_auto_scraper.sh" "$TEMP_CRON"; then
    echo "检测到已存在的自动抓取定时任务，先移除旧任务..."
    grep -v "start_auto_scraper.sh" "$TEMP_CRON" > "${TEMP_CRON}.new"
    mv "${TEMP_CRON}.new" "$TEMP_CRON"
fi

# 添加新的cron任务
echo "# 自动抓取服务管理任务" >> "$TEMP_CRON"
echo "# 系统启动后5分钟启动自动抓取服务" >> "$TEMP_CRON"
echo "@reboot sleep 300 && $START_SCRIPT start" >> "$TEMP_CRON"
echo "# 每天7:00检查并启动自动抓取服务（如果未运行）" >> "$TEMP_CRON"
echo "0 7 * * * $START_SCRIPT status || $START_SCRIPT start" >> "$TEMP_CRON"
echo "# 每小时检查服务状态，如果停止则重启" >> "$TEMP_CRON"
echo "*/30 * * * * $START_SCRIPT status > /dev/null || $START_SCRIPT start" >> "$TEMP_CRON"
echo "" >> "$TEMP_CRON"

# 安装新的crontab
if crontab "$TEMP_CRON"; then
    echo "✅ 定时任务设置成功！"
    echo ""
    echo "已设置的任务:"
    echo "1. 系统重启后5分钟自动启动抓取服务"
    echo "2. 每天7:00检查并启动服务（如果未运行）"
    echo "3. 每30分钟检查服务状态，如果停止则重启"
    echo ""
    echo "当前crontab内容:"
    crontab -l
else
    echo "❌ 定时任务设置失败！"
    exit 1
fi

# 清理临时文件
rm -f "$TEMP_CRON"

echo ""
echo "🎉 自动抓取服务定时任务配置完成！"
echo ""
echo "管理命令:"
echo "  启动服务: $START_SCRIPT start"
echo "  停止服务: $START_SCRIPT stop"
echo "  查看状态: $START_SCRIPT status"
echo "  重启服务: $START_SCRIPT restart"
echo "  查看日志: $START_SCRIPT logs"
echo ""
echo "要立即启动服务，请运行: $START_SCRIPT start"