// ==================== 心跳API - 在线状态跟踪 ====================
// 将此代码添加到 key_management_server.js 的第1250行左右（cleanup API 后面，数据库管理API 前面）

// 心跳API - 更新密钥在线状态
app.post('/api/keys/heartbeat', async (req, res) => {
    try {
        const { key, deviceId } = req.body;
        
        if (!key) {
            return res.status(400).json({
                success: false,
                error: '请提供密钥'
            });
        }

        const now = new Date();
        console.log(`💓 收到心跳: ${key.substring(0, 8)}... 设备: ${deviceId || '未知'} 时间: ${now.toLocaleTimeString()}`);

        // 更新最后在线时间和设备信息
        const updateData = { 
            lastOnline: now
        };
        
        if (deviceId) {
            updateData.lastOnlineDeviceId = deviceId;
        }

        const result = await keysCollection.updateOne(
            { key },
            { 
                $set: updateData
            }
        );

        if (result.matchedCount > 0) {
            return res.json({
                success: true,
                message: '心跳接收成功',
                timestamp: now.toISOString()
            });
        } else {
            // 密钥不存在
            console.warn(`⚠️ 心跳密钥不存在: ${key.substring(0, 8)}...`);
            return res.status(404).json({
                success: false,
                error: '密钥不存在',
                timestamp: now.toISOString()
            });
        }
    } catch (error) {
        console.error('❌ 心跳处理错误:', error);
        return res.status(500).json({
            success: false,
            error: '心跳处理失败',
            details: error.message
        });
    }
});

// 获取所有在线密钥
app.get('/api/keys/online', async (req, res) => {
    try {
        const now = new Date();
        // 最后心跳时间在2分钟内视为在线
        const onlineThreshold = new Date(now.getTime() - 2 * 60 * 1000);
        
        const onlineKeys = await keysCollection.find({
            lastOnline: { $gte: onlineThreshold },
            status: 'active'
        }).toArray();
        
        const onlineKeysData = onlineKeys.map(key => ({
            key: key.key,
            description: key.description,
            lastOnline: key.lastOnline,
            lastOnlineDeviceId: key.lastOnlineDeviceId,
            usageCount: key.usageCount,
            expiresAt: key.expiresAt,
            onlineDuration: Math.floor((now - new Date(key.lastOnline)) / 1000) // 秒
        }));
        
        return res.json({
            success: true,
            data: {
                count: onlineKeysData.length,
                keys: onlineKeysData,
                threshold: onlineThreshold.toISOString()
            }
        });
    } catch (error) {
        console.error('❌ 获取在线密钥失败:', error);
        return res.status(500).json({
            success: false,
            error: '获取在线密钥失败',
            details: error.message
        });
    }
});


