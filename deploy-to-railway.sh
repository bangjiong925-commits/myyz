#!/bin/bash

# Railway部署快速启动脚本
# 自动化部署Taiwan PK10系统到Railway平台

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "==========================================="
    echo "🚀 Taiwan PK10 Railway 部署脚本"
    echo "==========================================="
    echo -e "${NC}"
}

# 检查必要的工具
check_requirements() {
    print_info "检查部署环境..."
    
    # 检查Railway CLI
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI 未安装"
        print_info "请运行: npm install -g @railway/cli"
        exit 1
    fi
    
    # 检查Git
    if ! command -v git &> /dev/null; then
        print_error "Git 未安装"
        exit 1
    fi
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    
    print_success "环境检查通过"
}

# 检查Railway登录状态
check_railway_auth() {
    print_info "检查Railway登录状态..."
    
    if ! railway whoami &> /dev/null; then
        print_warning "未登录Railway，正在启动登录流程..."
        railway login
        
        if ! railway whoami &> /dev/null; then
            print_error "Railway登录失败"
            exit 1
        fi
    fi
    
    USER=$(railway whoami 2>/dev/null || echo "Unknown")
    print_success "已登录Railway，用户: $USER"
}

# 检查必要文件
check_files() {
    print_info "检查项目文件..."
    
    required_files=(
        "requirements.txt"
        "Procfile"
        "mongodb_api.py"
        "auto_scraper.py"
        "python_scraper.py"
        "TWPK.html"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "缺少必要文件: $file"
            exit 1
        fi
    done
    
    print_success "项目文件检查完成"
}

# 初始化Railway项目
init_railway_project() {
    print_info "初始化Railway项目..."
    
    # 检查是否已经初始化
    if [[ -f "railway.json" ]] && railway status &> /dev/null; then
        print_warning "Railway项目已存在，是否重新初始化? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            railway logout
            rm -f railway.json
        else
            print_info "使用现有Railway项目"
            return
        fi
    fi
    
    # 初始化新项目
    print_info "创建新的Railway项目..."
    railway login
    railway init
    
    print_success "Railway项目初始化完成"
}

# 设置环境变量
setup_environment() {
    print_info "配置环境变量..."
    
    # 检查是否有.env.railway文件
    if [[ -f ".env.railway" ]]; then
        print_info "发现.env.railway配置文件"
        print_warning "请手动在Railway Dashboard中设置以下环境变量:"
        echo ""
        cat .env.railway | grep -E '^[A-Z_]+='
        echo ""
        print_info "Railway Dashboard地址: https://railway.app/dashboard"
        print_warning "按Enter键继续，确认已设置环境变量..."
        read -r
    else
        print_warning "未找到.env.railway文件，请手动设置环境变量:"
        echo "MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/taiwan_pk10"
        echo "MONGODB_DB_NAME=taiwan_pk10"
        echo "ENVIRONMENT=production"
        print_warning "按Enter键继续，确认已设置环境变量..."
        read -r
    fi
    
    print_success "环境变量配置完成"
}

# 部署到Railway
deploy_to_railway() {
    print_info "开始部署到Railway..."
    
    # 确保代码已提交
    if [[ -n $(git status --porcelain) ]]; then
        print_info "检测到未提交的更改，正在提交..."
        git add .
        git commit -m "Deploy to Railway - $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    # 部署
    print_info "正在部署，请稍候..."
    railway up
    
    if [[ $? -eq 0 ]]; then
        print_success "部署完成！"
    else
        print_error "部署失败，请检查错误信息"
        exit 1
    fi
}

# 获取部署信息
get_deployment_info() {
    print_info "获取部署信息..."
    
    # 获取服务URL
    RAILWAY_URL=$(railway domain 2>/dev/null || echo "未设置域名")
    
    if [[ "$RAILWAY_URL" != "未设置域名" ]]; then
        print_success "部署URL: https://$RAILWAY_URL"
        
        # 测试部署
        print_info "测试部署状态..."
        if command -v python3 &> /dev/null && [[ -f "test_railway_deployment.py" ]]; then
            python3 test_railway_deployment.py "https://$RAILWAY_URL" || true
        fi
    else
        print_warning "未设置自定义域名，使用Railway生成的URL"
        print_info "请在Railway Dashboard中查看部署URL"
    fi
    
    # 显示有用的命令
    echo ""
    print_info "有用的Railway命令:"
    echo "  railway logs        - 查看日志"
    echo "  railway status      - 查看状态"
    echo "  railway domain      - 管理域名"
    echo "  railway variables   - 管理环境变量"
    echo "  railway open        - 在浏览器中打开"
}

# 主函数
main() {
    print_header
    
    # 检查参数
    if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --help, -h     显示帮助信息"
        echo "  --test-only    仅运行测试，不部署"
        echo ""
        echo "环境变量:"
        echo "  SKIP_CHECKS=1  跳过环境检查"
        echo ""
        exit 0
    fi
    
    if [[ "$1" == "--test-only" ]]; then
        if [[ -f "test_railway_deployment.py" ]]; then
            print_info "运行部署测试..."
            read -p "请输入Railway部署URL: " RAILWAY_URL
            python3 test_railway_deployment.py "$RAILWAY_URL"
        else
            print_error "测试脚本不存在"
        fi
        exit 0
    fi
    
    # 执行部署流程
    if [[ "$SKIP_CHECKS" != "1" ]]; then
        check_requirements
        check_railway_auth
        check_files
    fi
    
    init_railway_project
    setup_environment
    deploy_to_railway
    get_deployment_info
    
    print_success "🎉 Railway部署完成！"
    print_info "请查看上方的部署URL和测试结果"
}

# 错误处理
trap 'print_error "部署过程中发生错误，请检查上方的错误信息"' ERR

# 运行主函数
main "$@"