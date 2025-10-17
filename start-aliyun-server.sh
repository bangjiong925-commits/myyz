#!/bin/bash

echo "🚀 连接阿里云服务器并启动密钥管理服务..."

# SSH连接信息
SERVER_IP="47.242.214.89"
SERVER_USER="root"
SERVER_PASS="Zhu451277"

# 使用sshpass自动输入密码（如果没有安装sshpass，需要手动输入密码）
echo "正在连接到 ${SERVER_USER}@${SERVER_IP}..."

ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
echo "✅ 已连接到阿里云服务器"
echo ""

# 检查PM2服务状态
echo "📊 检查PM2服务状态..."
pm2 status

echo ""
echo "🔍 检查密钥管理服务..."
pm2 list | grep key-management-server

echo ""
echo "💡 如需启动密钥管理服务，请执行："
echo "   cd /opt/key-management-server"
echo "   pm2 start server.js --name key-management-server"
echo ""
echo "或重启服务："
echo "   pm2 restart key-management-server"
echo ""
echo "查看日志："
echo "   pm2 logs key-management-server"

ENDSSH

echo ""
echo "✅ 服务器连接已断开"









