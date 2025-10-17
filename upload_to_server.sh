#!/bin/bash
# 上传密钥管理系统到阿里云服务器

echo "正在上传 key_management.html 到阿里云服务器..."

# 备份服务器上的原文件
sshpass -p 'Zhu451277' ssh -o StrictHostKeyChecking=no root@47.242.214.89 \
    "cp /var/www/html/key_management.html /var/www/html/key_management.html.backup.$(date +%Y%m%d_%H%M%S)"

# 上传新文件
sshpass -p 'Zhu451277' scp -o StrictHostKeyChecking=no \
    /Users/a1234/Documents/GitHub/myyz/key_management.html \
    root@47.242.214.89:/var/www/html/key_management.html

# 验证上传
echo "验证文件..."
sshpass -p 'Zhu451277' ssh -o StrictHostKeyChecking=no root@47.242.214.89 \
    "grep -c '当前在线' /var/www/html/key_management.html"

if [ $? -eq 0 ]; then
    echo "✅ 上传成功！在线状态功能已添加"
    echo "🌐 访问: http://47.242.214.89/key_management.html"
else
    echo "❌ 上传失败，请检查网络连接"
fi










