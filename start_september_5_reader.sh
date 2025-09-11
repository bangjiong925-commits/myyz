#!/bin/bash
# 启动读取2024年9月5日数据的脚本

# 设置工作目录
cd "/Users/a1234/Documents/GitHub/myyz"

# 加载环境变量
if [ -f ".env" ]; then
    source .env
fi

# 运行Python脚本
python3 "/Users/a1234/Documents/GitHub/myyz/read_september_5_data.py"
