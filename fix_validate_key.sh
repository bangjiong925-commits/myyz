#!/bin/bash

# 修复阿里云 validate-key API 逻辑
# 确保密钥状态正确管理：
# - usageCount=0: 未激活
# - usageCount=1: 已激活（第一次验证后）
# - usageCount>1: 多次使用

ssh root@47.242.214.89 << 'ENDSSH'
cd /root

# 创建修复后的validate-key逻辑
cat > /tmp/validate_key_fix.js << 'EOF'
app.post('/api/keys/validate-key', async (req, res) => {
    try {
        const { key, deviceId } = req.body;
        
        if (!key) {
            return res.status(400).json({
                success: false,
                valid: false,
                reason: '请提供密钥'
            });
        }

        console.log('🔒 服务器端密钥验证:', key, '设备ID:', deviceId || '未提供');

        // 1. 查找密钥
        const existingKey = await keysCollection.findOne({ key });
        
        if (!existingKey) {
            // 密钥不存在于数据库
            // 尝试验证格式（短密钥格式）
            if (key.length >= 20 && key.length <= 25) {
                const identifier = key.substring(0, 4);
                const timestampPart = key.substring(4, 10);
                const randomPadding = key.substring(10, 16);
                const checksum = key.substring(16, 22);

                const expiry = parseInt(timestampPart, 36);
                
                if (isNaN(expiry) || expiry <= 0) {
                    return res.json({
                        success: false,
                        valid: false,
                        reason: '密钥格式无效：时间戳无效'
                    });
                }

                const currentTime = Math.floor(Date.now() / 1000);
                if (currentTime > expiry) {
                    return res.json({
                        success: false,
                        valid: false,
                        reason: '密钥已过期'
                    });
                }

                const expectedChecksum = generateEnhancedChecksum(identifier + timestampPart + randomPadding);
                if (checksum !== expectedChecksum) {
                    return res.json({
                        success: false,
                        valid: false,
                        reason: '密钥格式无效：校验失败'
                    });
                }

                // 格式有效但不在数据库，自动注册为未激活状态
                const now = new Date();
                const expiresAt = new Date(expiry * 1000);
                const totalDuration = expiresAt.getTime() - now.getTime();

                const newKeyDocument = {
                    key,
                    description: `用户密钥 - ${identifier}`,
                    status: 'inactive',  // 未激活状态
                    createdAt: now,
                    activatedAt: null,
                    expiresAt: expiresAt,
                    totalDuration: totalDuration,
                    usageCount: 0,  // 未激活，计数为0
                    lastUsed: null,
                    deviceId: deviceId || null,
                    keyType: 'short',
                    identifier: identifier
                };

                await keysCollection.insertOne(newKeyDocument);

                return res.json({
                    success: false,
                    valid: false,
                    reason: '密钥未激活，请先激活密钥',
                    data: {
                        key,
                        status: 'inactive',
                        usageCount: 0,
                        expiresAt: expiresAt
                    }
                });
            } else {
                return res.json({
                    success: false,
                    valid: false,
                    reason: '密钥不存在'
                });
            }
        }

        // 2. 密钥存在，检查状态
        const now = new Date();
        const remainingTime = calculateRemainingTime(existingKey.expiresAt);
        
        if (remainingTime <= 0) {
            await keysCollection.updateOne(
                { key },
                { $set: { status: 'expired' } }
            );
            return res.json({
                success: false,
                valid: false,
                reason: '密钥已过期',
                data: {
                    key,
                    status: 'expired',
                    usageCount: existingKey.usageCount,
                    expiresAt: existingKey.expiresAt
                }
            });
        }

        // 3. 检查密钥激活状态
        if (existingKey.usageCount === 0) {
            // 未激活，需要激活
            // 第一次验证时激活
            await keysCollection.updateOne(
                { key },
                {
                    $set: {
                        status: 'active',
                        activatedAt: now,
                        usageCount: 1,
                        lastUsed: now,
                        deviceId: deviceId || existingKey.deviceId
                    }
                }
            );

            return res.json({
                success: true,
                valid: true,
                reason: '密钥激活成功',
                data: {
                    key,
                    status: 'active',
                    usageCount: 1,
                    activatedAt: now,
                    expiresAt: existingKey.expiresAt,
                    remainingTime: formatDuration(remainingTime)
                }
            });
        } else if (existingKey.usageCount >= 1) {
            // 已激活，检查设备绑定
            if (deviceId && existingKey.deviceId && existingKey.deviceId !== deviceId) {
                return res.json({
                    success: false,
                    valid: false,
                    reason: '密钥已绑定其他设备',
                    data: {
                        key,
                        status: existingKey.status,
                        usageCount: existingKey.usageCount,
                        boundDevice: existingKey.deviceId
                    }
                });
            }

            // 同一设备或无设备ID限制，允许使用
            await keysCollection.updateOne(
                { key },
                {
                    $set: {
                        lastUsed: now
                    }
                }
            );

            return res.json({
                success: true,
                valid: true,
                reason: '密钥验证成功',
                data: {
                    key,
                    status: existingKey.status,
                    usageCount: existingKey.usageCount,
                    activatedAt: existingKey.activatedAt,
                    expiresAt: existingKey.expiresAt,
                    remainingTime: formatDuration(remainingTime)
                }
            });
        }
    } catch (error) {
        console.error('密钥验证错误:', error);
        res.status(500).json({
            success: false,
            valid: false,
            reason: '服务器内部错误',
            error: error.message
        });
    }
});
EOF

echo "✅ 修复脚本已创建"
echo "📝 请手动更新 key_management_server.js 文件中的 validate-key API"
echo "📍 位置：第552行开始的 app.post('/api/keys/validate-key') 函数"
echo "🔧 需要替换整个函数体"

ENDSSH

