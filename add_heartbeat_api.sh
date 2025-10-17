#!/bin/bash

# 在阿里云密钥管理服务器添加心跳API和在线状态功能

cat << 'EOF'
====================================
添加密钥在线状态心跳API
====================================

需要在 key_management_server.js 中添加以下代码：

1. 在密钥文档结构中添加 lastOnline 字段（创建密钥时）：
   lastOnline: null  // 最后在线时间

2. 添加心跳API（在其他API路由后面添加）：

// 心跳API - 更新密钥在线状态
app.post('/api/keys/heartbeat', async (req, res) => {
    try {
        const { key } = req.body;
        
        if (!key) {
            return res.status(400).json({
                success: false,
                error: '请提供密钥'
            });
        }

        console.log(`💓 收到心跳: ${key.substring(0, 8)}...`);

        // 更新最后在线时间
        const result = await keysCollection.updateOne(
            { key },
            { 
                $set: { 
                    lastOnline: new Date()
                } 
            }
        );

        if (result.modifiedCount > 0) {
            return res.json({
                success: true,
                message: '心跳接收成功',
                timestamp: new Date().toISOString()
            });
        } else {
            // 密钥不存在或没有变化
            return res.json({
                success: true,
                message: '心跳接收（密钥未找到或未变化）',
                timestamp: new Date().toISOString()
            });
        }
    } catch (error) {
        console.error('心跳处理错误:', error);
        return res.status(500).json({
            success: false,
            error: '心跳处理失败',
            details: error.message
        });
    }
});

3. 在密钥列表API中添加在线状态计算：

   在返回密钥数据时，添加：
   
   // 计算在线状态（最后心跳时间在2分钟内视为在线）
   const isOnline = key.lastOnline && 
                    (new Date() - new Date(key.lastOnline)) < 2 * 60 * 1000;
   
   return {
       ...key,
       isOnline: isOnline,
       lastOnline: key.lastOnline
   };

====================================
实施步骤：
====================================
1. 备份当前文件：
   cp key_management_server.js key_management_server.js.backup_heartbeat

2. 编辑 key_management_server.js 添加上述代码

3. 重启服务：
   pm2 restart key_management_server

4. 测试心跳API：
   curl -X POST http://47.242.214.89/api/keys/heartbeat \
     -H "Content-Type: application/json" \
     -d '{"key":"YOUR_TEST_KEY"}'

====================================
EOF

