#!/bin/bash

# 更新应用程序配置以使用MongoDB Atlas的脚本

echo "===== MongoDB Atlas配置更新工具 ====="
echo ""

# 检查是否提供了MongoDB Atlas连接字符串
if [ $# -lt 1 ]; then
    echo "错误: 请提供MongoDB Atlas连接字符串"
    echo "用法: $0 <MongoDB Atlas连接字符串> [数据库名称]"
    echo "例如: $0 'mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/taiwan_pk10?retryWrites=true&w=majority' 'taiwan_pk10'"
    exit 1
fi

# 获取参数
ATLAS_URI="$1"
DB_NAME="${2:-taiwan_pk10}"

echo "将使用以下配置:"
echo "MongoDB Atlas URI: ${ATLAS_URI//@*/@****}"
echo "数据库名称: $DB_NAME"
echo ""

# 创建或更新.env文件
ENV_FILE=".env"
echo "正在更新 $ENV_FILE 文件..."

# 检查文件是否存在
if [ -f "$ENV_FILE" ]; then
    # 文件存在，更新或添加配置
    grep -q "^MONGODB_URI=" "$ENV_FILE" && \
        sed -i "" "s|^MONGODB_URI=.*|MONGODB_URI=$ATLAS_URI|" "$ENV_FILE" || \
        echo "MONGODB_URI=$ATLAS_URI" >> "$ENV_FILE"
    
    grep -q "^MONGODB_DB_NAME=" "$ENV_FILE" && \
        sed -i "" "s|^MONGODB_DB_NAME=.*|MONGODB_DB_NAME=$DB_NAME|" "$ENV_FILE" || \
        echo "MONGODB_DB_NAME=$DB_NAME" >> "$ENV_FILE"
    
    echo "已更新 $ENV_FILE 文件"
else
    # 文件不存在，创建新文件
    echo "MONGODB_URI=$ATLAS_URI" > "$ENV_FILE"
    echo "MONGODB_DB_NAME=$DB_NAME" >> "$ENV_FILE"
    echo "已创建 $ENV_FILE 文件"
fi

# 检查docker-compose.yml文件
DOCKER_COMPOSE="docker-compose.yml"
if [ -f "$DOCKER_COMPOSE" ]; then
    echo "\n检测到 $DOCKER_COMPOSE 文件"
    echo "请手动更新 $DOCKER_COMPOSE 文件中的环境变量:"
    echo "services:"
    echo "  api:"
    echo "    environment:"
    echo "      - MONGODB_URI=$ATLAS_URI"
    echo "      - MONGODB_DB_NAME=$DB_NAME"
    echo "  crawler:"
    echo "    environment:"
    echo "      - MONGODB_URI=$ATLAS_URI"
    echo "      - MONGODB_DB_NAME=$DB_NAME"
fi

# 设置当前会话的环境变量
echo "\n为当前会话设置环境变量..."
export MONGODB_URI="$ATLAS_URI"
export MONGODB_DB_NAME="$DB_NAME"
echo "已设置环境变量"

echo "\n===== 配置更新完成 ====="
echo "您现在可以运行应用程序连接到MongoDB Atlas"
echo "例如: python check_today_data.py"