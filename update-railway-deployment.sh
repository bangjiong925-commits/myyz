#!/bin/bash

# Railway项目更新部署脚本
# 用于更新现有的Railway项目而不是创建新项目

set -e

echo "🚀 Railway项目更新部署脚本"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查函数
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 未安装，请先安装 $1${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ $1 已安装${NC}"
}

# 检查文件是否存在
check_file() {
    if [ ! -f "$1" ]; then
        echo -e "${RED}❌ 文件不存在: $1${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ 文件存在: $1${NC}"
}

echo "\n📋 环境检查..."
check_command "railway"
check_command "git"
check_command "python3"

# 检查Railway登录状态
echo "\n🔐 检查Railway登录状态..."
if ! railway whoami &> /dev/null; then
    echo -e "${RED}❌ 未登录Railway，请先运行: railway login${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Railway已登录${NC}"

# 检查必要文件
echo "\n📁 检查项目文件..."
check_file "requirements.txt"
check_file "Procfile"
check_file "mongodb_api.py"
check_file "auto_scraper.py"
check_file "python_scraper.py"
check_file "TWPK.html"

# 检查是否在Railway项目目录中
echo "\n🔍 检查Railway项目状态..."
if ! railway status &> /dev/null; then
    echo -e "${RED}❌ 当前目录不是Railway项目，请确保在正确的项目目录中${NC}"
    echo -e "${YELLOW}💡 如果这是新目录，请运行: railway link${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 检测到Railway项目${NC}"
railway status

# 显示当前环境变量
echo "\n🔧 当前环境变量:"
railway variables

# 自动更新环境变量
echo "\n🔧 自动配置环境变量..."
if [ -f ".env.railway" ]; then
    echo "📄 从 .env.railway 读取环境变量..."
    while IFS='=' read -r key value; do
        if [[ ! $key =~ ^# ]] && [[ $key ]] && [[ $value ]]; then
            # 移除值中的引号
            value=$(echo $value | sed 's/^"\|"$//g')
            echo "设置: $key"
                        railway variables --set "$key=$value"
        fi
    done < .env.railway
    echo -e "${GREEN}✅ 环境变量已从 .env.railway 设置${NC}"
else
    echo "⏭️ 未找到 .env.railway 文件，跳过环境变量更新"
fi

# Git提交和推送
echo "\n📦 准备代码提交..."
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 检测到代码变更，准备提交..."
    git add .
    git commit -m "Update Taiwan PK10 system for Railway deployment - $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${GREEN}✅ 代码已提交${NC}"
else
    echo "📝 没有检测到代码变更"
fi

# 推送到Railway
echo "\n🚀 部署到Railway..."
echo "这将更新您现有的Railway项目..."
railway up

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}🎉 部署成功!${NC}"
    
    # 获取部署信息
    echo "\n📊 部署信息:"
    railway status
    
    echo "\n🌐 获取服务URL..."
    railway domain
    
    # 等待服务启动
    echo "\n⏳ 等待服务启动 (30秒)..."
    sleep 30
    
    # 测试部署
    echo "\n🧪 测试部署状态..."
    if command -v python3 &> /dev/null && [ -f "test_railway_deployment.py" ]; then
        echo "运行自动化测试..."
        python3 test_railway_deployment.py
    else
        echo "手动测试说明:"
        echo "1. 访问您的Railway域名"
        echo "2. 测试API端点: /api/health"
        echo "3. 测试数据端点: /api/taiwan-pk10/today"
    fi
    
    echo -e "\n${GREEN}🎊 Railway项目更新完成!${NC}"
    echo "\n📋 后续步骤:"
    echo "1. 检查服务日志: railway logs"
    echo "2. 监控服务状态: railway status"
    echo "3. 查看域名: railway domain"
    echo "4. 管理环境变量: railway variables"
    
else
    echo -e "\n${RED}❌ 部署失败${NC}"
    echo "请检查错误信息并重试"
    exit 1
fi

# 显示有用的命令
echo "\n💡 有用的Railway命令:"
echo "  railway logs          - 查看应用日志"
echo "  railway logs -f       - 实时查看日志"
echo "  railway status        - 查看项目状态"
echo "  railway variables     - 查看环境变量"
echo "  railway domain        - 查看/设置域名"
echo "  railway restart       - 重启服务"
echo "  railway shell         - 连接到容器shell"

echo -e "\n${BLUE}📚 更多信息请查看: README_RAILWAY.md${NC}"