#!/bin/bash
# -*- coding: utf-8 -*-

# 设置每日数据库清理任务
# 此脚本将自动配置crontab，每天凌晨2点执行数据库清理

echo "=== 设置每日数据库清理任务 ==="
echo

# 获取当前脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "脚本目录: $SCRIPT_DIR"

# 检查必要文件是否存在
if [ ! -f "$SCRIPT_DIR/daily_cleanup.py" ]; then
    echo "错误: 找不到 daily_cleanup.py 文件"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/cleanup_database.py" ]; then
    echo "错误: 找不到 cleanup_database.py 文件"
    exit 1
fi

# 检查Python3是否可用
if ! command -v python3 &> /dev/null; then
    echo "错误: 系统中未找到 python3 命令"
    exit 1
fi

PYTHON3_PATH=$(which python3)
echo "Python3 路径: $PYTHON3_PATH"

# 创建logs目录（如果不存在）
if [ ! -d "$SCRIPT_DIR/logs" ]; then
    mkdir -p "$SCRIPT_DIR/logs"
    echo "创建日志目录: $SCRIPT_DIR/logs"
fi

# 生成crontab条目
CRONTAB_ENTRY="0 2 * * * cd $SCRIPT_DIR && $PYTHON3_PATH daily_cleanup.py >> logs/daily_cleanup.log 2>&1"

echo
echo "将要添加的crontab任务:"
echo "$CRONTAB_ENTRY"
echo

# 检查是否已经存在相同的任务
if crontab -l 2>/dev/null | grep -q "daily_cleanup.py"; then
    echo "警告: 检测到已存在的daily_cleanup任务"
    echo "当前crontab中的相关任务:"
    crontab -l 2>/dev/null | grep "daily_cleanup.py"
    echo
    read -p "是否要替换现有任务？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "操作已取消"
        exit 0
    fi
    
    # 移除现有的daily_cleanup任务
    crontab -l 2>/dev/null | grep -v "daily_cleanup.py" | crontab -
    echo "已移除现有的daily_cleanup任务"
fi

# 添加新的crontab任务
echo "正在添加新的crontab任务..."
(crontab -l 2>/dev/null; echo "$CRONTAB_ENTRY") | crontab -

if [ $? -eq 0 ]; then
    echo "✓ crontab任务添加成功！"
    echo
    echo "任务详情:"
    echo "- 执行时间: 每天凌晨2点"
    echo "- 保留天数: 7天"
    echo "- 日志文件: $SCRIPT_DIR/logs/daily_cleanup.log"
    echo
    echo "查看当前所有crontab任务:"
    crontab -l
    echo
    echo "如需手动执行清理任务，请运行:"
    echo "cd $SCRIPT_DIR && python3 daily_cleanup.py"
else
    echo "✗ crontab任务添加失败！"
    exit 1
fi

echo
echo "=== 设置完成 ==="