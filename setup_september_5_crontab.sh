#!/bin/bash

# 设置读取2024年9月5日数据的定时任务
# 在凌晨00:00到早上07:05之间运行

echo "设置读取2024年9月5日数据的定时任务..."

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/read_september_5_data.py"
START_SCRIPT="$SCRIPT_DIR/start_september_5_reader.sh"

# 检查Python脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "错误: Python脚本不存在: $PYTHON_SCRIPT"
    exit 1
fi

# 创建启动脚本
cat > "$START_SCRIPT" << EOF
#!/bin/bash
# 启动读取2024年9月5日数据的脚本

# 设置工作目录
cd "$SCRIPT_DIR"

# 加载环境变量
if [ -f ".env" ]; then
    source .env
fi

# 运行Python脚本
python3 "$PYTHON_SCRIPT"
EOF

# 给启动脚本执行权限
chmod +x "$START_SCRIPT"

# 获取当前crontab内容
crontab -l > /tmp/current_crontab 2>/dev/null || touch /tmp/current_crontab

# 移除已存在的相关任务
grep -v "read_september_5_data" /tmp/current_crontab > /tmp/new_crontab
grep -v "start_september_5_reader" /tmp/new_crontab > /tmp/temp_crontab
mv /tmp/temp_crontab /tmp/new_crontab

# 添加新的定时任务
echo "" >> /tmp/new_crontab
echo "# 读取2024年9月5日数据的定时任务" >> /tmp/new_crontab
echo "# 每天凌晨1点运行" >> /tmp/new_crontab
echo "0 1 * * * $START_SCRIPT >> $SCRIPT_DIR/logs/cron_september_5.log 2>&1" >> /tmp/new_crontab
echo "# 每天凌晨3点运行" >> /tmp/new_crontab
echo "0 3 * * * $START_SCRIPT >> $SCRIPT_DIR/logs/cron_september_5.log 2>&1" >> /tmp/new_crontab
echo "# 每天凌晨5点运行" >> /tmp/new_crontab
echo "0 5 * * * $START_SCRIPT >> $SCRIPT_DIR/logs/cron_september_5.log 2>&1" >> /tmp/new_crontab
echo "# 每天早上7点运行" >> /tmp/new_crontab
echo "0 7 * * * $START_SCRIPT >> $SCRIPT_DIR/logs/cron_september_5.log 2>&1" >> /tmp/new_crontab

# 安装新的crontab
crontab /tmp/new_crontab

# 清理临时文件
rm -f /tmp/current_crontab /tmp/new_crontab

echo "定时任务设置完成！"
echo "已添加以下定时任务:"
echo "- 每天凌晨1点运行读取2024年9月5日数据"
echo "- 每天凌晨3点运行读取2024年9月5日数据"
echo "- 每天凌晨5点运行读取2024年9月5日数据"
echo "- 每天早上7点运行读取2024年9月5日数据"
echo ""
echo "查看当前crontab:"
crontab -l | grep -A 10 -B 2 "september_5"

echo ""
echo "管理命令:"
echo "- 查看定时任务: crontab -l"
echo "- 移除定时任务: crontab -r"
echo "- 查看日志: tail -f $SCRIPT_DIR/logs/cron_september_5.log"
echo "- 手动运行: $START_SCRIPT"