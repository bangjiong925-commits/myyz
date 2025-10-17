#!/bin/bash
# 阿里云服务器部署脚本

echo "🚀 开始部署到阿里云服务器..."

# 创建部署脚本内容
cat > /tmp/aliyun-deploy.sh << 'EOF'
#!/bin/bash
echo "🔍 查找 server.js 文件..."
SERVER_FILE=$(find /root -name 'server.js' -path '*/aliyun-key-server/*' 2>/dev/null | head -1)

if [ -z "$SERVER_FILE" ]; then
    echo "📁 常见路径尝试..."
    for path in /root/aliyun-key-server /home/aliyun-key-server /opt/aliyun-key-server; do
        if [ -f "$path/server.js" ]; then
            SERVER_FILE="$path/server.js"
            break
        fi
    done
fi

if [ -z "$SERVER_FILE" ]; then
    echo "❌ 未找到 server.js，请手动输入完整路径："
    read SERVER_FILE
fi

echo "📁 使用文件: $SERVER_FILE"
BACKUP_FILE="${SERVER_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo "💾 备份到: $BACKUP_FILE"
cp "$SERVER_FILE" "$BACKUP_FILE"

if grep -q "app.post('/api/keys/validate-key'" "$SERVER_FILE"; then
    echo "✅ 检测到已存在 validate-key API"
    exit 0
fi

LINE_NUM=$(grep -n "// 404处理" "$SERVER_FILE" | head -1 | cut -d: -f1)
if [ -z "$LINE_NUM" ]; then
    LINE_NUM=$(grep -n "app.use('\*'" "$SERVER_FILE" | head -1 | cut -d: -f1)
fi

echo "📍 插入位置: 第 $LINE_NUM 行"

# 创建新API代码
cat > /tmp/new_apis.txt << 'APICODE'

// 用户密钥验证API（用于前端TWPK.html登录验证）
app.post('/api/keys/validate-key', [
    body('key').notEmpty(),
    body('deviceId').optional().isString(),
    body('clientTime').optional().isNumeric()
], async (req, res) => {
    try {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ success: false, valid: false, reason: '输入验证失败', details: errors.array() });
        }
        const { key, deviceId, clientTime } = req.body;
        const ipAddress = req.ip || req.headers['x-forwarded-for'] || req.connection.remoteAddress;
        const userAgent = req.headers['user-agent'] || 'unknown';
        if (!validateKeyFormat(key)) {
            return res.status(400).json({ success: false, valid: false, reason: '密钥格式无效' });
        }
        const keyRecord = await keysCollection.findOne({ key: key });
        if (!keyRecord) {
            return res.json({ success: false, valid: false, reason: '密钥不存在或已被删除' });
        }
        if (keyRecord.status === 'inactive' || keyRecord.status === 'disabled') {
            return res.json({ success: false, valid: false, reason: '密钥已被禁用' });
        }
        const now = new Date();
        if (keyRecord.expiresAt && new Date(keyRecord.expiresAt) < now) {
            await keysCollection.updateOne({ key: key }, { $set: { status: 'expired' } });
            return res.json({ success: false, valid: false, reason: '密钥已过期' });
        }
        if (deviceId) {
            if (!keyRecord.firstDeviceInfo) {
                await keysCollection.updateOne({ key: key }, { $set: { firstDeviceInfo: { deviceId: deviceId, ip: ipAddress, userAgent: userAgent, firstVerified: now, lastVerified: now }, activatedAt: now, status: 'active', lastUsed: now }, $inc: { usageCount: 1 } });
            } else {
                if (keyRecord.firstDeviceInfo.deviceId !== deviceId) {
                    return res.json({ success: false, valid: false, reason: '此密钥已在其他设备上激活，每个密钥只能在一个设备上使用' });
                }
                await keysCollection.updateOne({ key: key }, { $set: { 'firstDeviceInfo.lastVerified': now, 'firstDeviceInfo.ip': ipAddress, lastUsed: now }, $inc: { usageCount: 1 } });
            }
        } else {
            await keysCollection.updateOne({ key: key }, { $inc: { usageCount: 1 }, $set: { lastUsed: now } });
        }
        const updatedKey = await keysCollection.findOne({ key: key });
        let remainingTime = '永久有效', totalDuration = '永久';
        if (updatedKey.expiresAt) {
            const expiresAt = new Date(updatedKey.expiresAt);
            const remaining = expiresAt.getTime() - now.getTime();
            if (remaining > 0) {
                const days = Math.floor(remaining / (1000 * 60 * 60 * 24));
                const hours = Math.floor((remaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
                remainingTime = days > 0 ? `${days}天 ${hours}小时` : hours > 0 ? `${hours}小时 ${minutes}分钟` : `${minutes}分钟`;
            } else {
                remainingTime = '已过期';
            }
            if (updatedKey.createdAt) {
                const total = expiresAt.getTime() - new Date(updatedKey.createdAt).getTime();
                const totalDays = Math.floor(total / (1000 * 60 * 60 * 24));
                const totalHours = Math.floor((total % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                totalDuration = totalDays > 0 ? `${totalDays}天 ${totalHours}小时` : `${totalHours}小时`;
            }
        }
        res.json({ success: true, valid: true, reason: '密钥验证成功', data: { key: updatedKey.key, description: updatedKey.description || updatedKey.name || '', status: updatedKey.status, createdAt: updatedKey.createdAt, activatedAt: updatedKey.activatedAt, expiresAt: updatedKey.expiresAt, lastUsed: updatedKey.lastUsed, usageCount: updatedKey.usageCount || 0, remainingTime, totalDuration, deviceBound: !!updatedKey.firstDeviceInfo, deviceInfo: updatedKey.firstDeviceInfo ? { deviceId: updatedKey.firstDeviceInfo.deviceId, firstVerified: updatedKey.firstDeviceInfo.firstVerified, lastVerified: updatedKey.firstDeviceInfo.lastVerified } : null } });
    } catch (error) {
        console.error('密钥验证错误:', error);
        res.status(500).json({ success: false, valid: false, reason: '服务器内部错误', error: error.message });
    }
});

app.post('/api/keys/check-usage', [ body('key').notEmpty() ], async (req, res) => {
    try {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ success: false, used: false, reason: '输入验证失败', details: errors.array() });
        }
        const { key } = req.body;
        if (!validateKeyFormat(key)) {
            return res.status(400).json({ success: false, used: false, reason: '密钥格式无效' });
        }
        const keyRecord = await keysCollection.findOne({ key: key });
        if (!keyRecord) {
            return res.json({ success: false, used: false, reason: '密钥不存在' });
        }
        const isUsed = !!(keyRecord.firstDeviceInfo || keyRecord.activatedAt || (keyRecord.usageCount && keyRecord.usageCount > 0));
        res.json({ success: true, used: isUsed, reason: isUsed ? '密钥已被使用' : '密钥未被使用', data: { key: keyRecord.key, status: keyRecord.status, usageCount: keyRecord.usageCount || 0, activatedAt: keyRecord.activatedAt, deviceBound: !!keyRecord.firstDeviceInfo } });
    } catch (error) {
        console.error('检查密钥使用错误:', error);
        res.status(500).json({ success: false, used: false, reason: '服务器内部错误', error: error.message });
    }
});

APICODE

INSERT_LINE=$((LINE_NUM - 1))
head -n $INSERT_LINE "$SERVER_FILE" > /tmp/server_new.js
cat /tmp/new_apis.txt >> /tmp/server_new.js
tail -n +$LINE_NUM "$SERVER_FILE" >> /tmp/server_new.js
mv /tmp/server_new.js "$SERVER_FILE"

echo "✅ 新API已添加！"
if command -v pm2 &> /dev/null; then
    pm2 restart all && echo "✅ PM2已重启"
else
    echo "⚠️  请手动重启服务"
fi
echo "✅ 部署完成！备份: $BACKUP_FILE"
EOF

echo "📤 上传部署脚本到阿里云服务器..."
scp /tmp/aliyun-deploy.sh root@47.242.214.89:/tmp/

echo "🚀 在阿里云服务器上执行部署..."
ssh root@47.242.214.89 "chmod +x /tmp/aliyun-deploy.sh && /tmp/aliyun-deploy.sh"

echo "✅ 部署完成！"


