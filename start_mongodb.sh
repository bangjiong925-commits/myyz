#!/bin/bash

# 检查MongoDB服务状态并启动
echo "检查MongoDB服务状态..."

# 检查是否安装了Docker
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "检测到Docker环境，尝试使用docker-compose启动MongoDB..."
    cd "$(dirname "$0")"
    
    # 检查docker-compose.yml文件是否存在
    if [ -f "docker-compose.yml" ]; then
        echo "启动MongoDB容器..."
        docker-compose up -d mongodb
        echo "MongoDB容器启动命令已执行，请等待几秒钟让服务完全启动"
    else
        echo "错误: 未找到docker-compose.yml文件"
        exit 1
    fi
else
    # 检查本地MongoDB服务
    echo "检查本地MongoDB服务..."
    
    if command -v brew &> /dev/null; then
        # macOS环境使用Homebrew
        if brew services list | grep -q mongodb; then
            echo "使用Homebrew启动MongoDB服务..."
            brew services start mongodb-community
        else
            echo "MongoDB未通过Homebrew安装，请先安装:"
            echo "  brew tap mongodb/brew"
            echo "  brew install mongodb-community"
            exit 1
        fi
    elif command -v systemctl &> /dev/null; then
        # Linux环境使用systemd
        echo "使用systemd启动MongoDB服务..."
        sudo systemctl start mongod
    else
        echo "未检测到支持的MongoDB服务管理工具"
        echo "请手动启动MongoDB服务，或安装Docker和docker-compose"
        exit 1
    fi
fi

echo "\nMongoDB服务启动命令已执行"
echo "现在可以运行 python check_today_data.py 检查数据库连接"