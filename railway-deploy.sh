#!/bin/bash

# Railway部署脚本 - Taiwan PK10 Scraper System
# 使用方法: ./railway-deploy.sh

set -e

echo "🚀 开始Railway部署流程..."

# 检查Railway CLI是否安装
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI未安装，请先安装:"
    echo "npm install -g @railway/cli"
    echo "或访问: https://docs.railway.app/develop/cli"
    exit 1
fi

# 检查是否已登录Railway
if ! railway whoami &> /dev/null; then
    echo "🔐 请先登录Railway:"
    railway login
fi

# 检查必要文件
echo "📋 检查部署文件..."
required_files=("requirements.txt" "Procfile" "mongodb_api.py" "auto_scraper.py" "python_scraper.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 缺少必要文件: $file"
        exit 1
    fi
done
echo "✅ 所有必要文件检查完成"

# 创建新的Railway项目（如果不存在）
echo "🏗️ 初始化Railway项目..."
if [ ! -f ".railway" ]; then
    railway init
fi

# 设置环境变量
echo "⚙️ 配置环境变量..."
echo "请设置以下环境变量:"
echo "1. MONGODB_URI - MongoDB连接字符串"
echo "2. PORT - 服务端口（Railway会自动设置）"
echo ""
echo "在Railway Dashboard中设置环境变量:"
echo "railway open"
echo ""
read -p "环境变量设置完成后，按Enter继续..."

# 部署到Railway
echo "🚀 开始部署..."
railway up

echo "✅ 部署完成！"
echo ""
echo "📊 查看部署状态:"
echo "railway status"
echo ""
echo "📝 查看日志:"
echo "railway logs"
echo ""
echo "🌐 打开项目面板:"
echo "railway open"
echo ""
echo "🔗 获取部署URL:"
railway domain

echo "🎉 Railway部署流程完成！"