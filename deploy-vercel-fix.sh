#!/bin/bash

echo "=========================================="
echo "🚀 Vercel 心跳功能修复 - 快速部署"
echo "=========================================="
echo ""

# 检查Git状态
echo "📋 检查Git状态..."
git status

echo ""
echo "📦 准备提交以下文件："
echo "  - api/keys.js (密钥列表API代理)"
echo "  - api/stats.js (统计API代理)"
echo "  - api/keys/validate-key.js (验证API代理)"
echo "  - api/keys/check-usage.js (检查使用API代理)"
echo "  - api/keys/heartbeat.js (心跳API代理 - 已存在)"
echo "  - vercel.json (Vercel配置)"
echo "  - test-vercel-heartbeat.html (测试页面)"
echo "  - VERCEL_DEPLOY.md (部署文档)"
echo ""

read -p "是否继续提交和推送？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ 已取消"
    exit 1
fi

echo ""
echo "📝 添加文件到Git..."
git add api/keys.js
git add api/stats.js
git add api/keys/validate-key.js
git add api/keys/check-usage.js
git add api/keys/heartbeat.js
git add vercel.json
git add test-vercel-heartbeat.html
git add VERCEL_DEPLOY.md
git add deploy-vercel-fix.sh

echo "✅ 文件已添加"
echo ""

echo "💾 创建提交..."
git commit -m "修复Vercel心跳功能：添加完整API代理支持在线状态显示

- 新增 api/keys.js - 密钥列表API代理
- 新增 api/stats.js - 统计API代理  
- 新增 api/keys/validate-key.js - 密钥验证API代理
- 新增 api/keys/check-usage.js - 检查使用API代理
- 更新 vercel.json - 优化CORS和函数配置
- 新增 test-vercel-heartbeat.html - Vercel测试页面
- 新增 VERCEL_DEPLOY.md - 详细部署文档

所有API请求通过Vercel代理转发到阿里云服务器，
解决Vercel无法显示在线状态的问题。"

if [ $? -ne 0 ]; then
    echo "⚠️ 提交失败或没有变更"
    echo "检查是否有冲突或文件已经提交"
    exit 1
fi

echo "✅ 提交成功"
echo ""

echo "🌐 推送到远程仓库..."
git push origin main

if [ $? -ne 0 ]; then
    echo "❌ 推送失败"
    echo "请检查网络连接和Git权限"
    exit 1
fi

echo "✅ 推送成功"
echo ""
echo "=========================================="
echo "✅ 部署脚本执行完成！"
echo "=========================================="
echo ""
echo "📌 后续步骤："
echo ""
echo "1. 等待 Vercel 自动部署（1-2分钟）"
echo "   访问: https://vercel.com/dashboard"
echo ""
echo "2. 测试心跳功能"
echo "   访问: https://your-app.vercel.app/test-vercel-heartbeat.html"
echo ""
echo "3. 查看密钥管理系统在线状态"
echo "   访问: https://your-app.vercel.app/key_management.html"
echo ""
echo "4. 如需详细测试步骤，请查看:"
echo "   VERCEL_DEPLOY.md"
echo ""
echo "=========================================="

