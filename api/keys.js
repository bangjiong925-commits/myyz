// Vercel Serverless Function for Key Management
const { MongoClient } = require('mongodb');

// MongoDB连接配置
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const DB_NAME = process.env.MONGODB_DB_NAME || 'key_management';

let cachedClient = null;

async function connectToDatabase() {
    if (cachedClient) {
        return cachedClient;
    }
    
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    cachedClient = client;
    return client;
}

// 生成随机密钥
function generateKey(length = 32) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

// 解析有效期
function parseExpiration(expiration) {
    const match = expiration.match(/^(\d+)(分钟|小时|天|月)$/);
    if (!match) return null;
    
    const value = parseInt(match[1]);
    const unit = match[2];
    const now = new Date();
    
    switch (unit) {
        case '分钟':
            return new Date(now.getTime() + value * 60 * 1000);
        case '小时':
            return new Date(now.getTime() + value * 60 * 60 * 1000);
        case '天':
            return new Date(now.getTime() + value * 24 * 60 * 60 * 1000);
        case '月':
            return new Date(now.getTime() + value * 30 * 24 * 60 * 60 * 1000);
        default:
            return null;
    }
}

module.exports = async function handler(req, res) {
    // 设置CORS头
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }
    
    try {
        const client = await connectToDatabase();
        const db = client.db(DB_NAME);
        const keysCollection = db.collection('keys');
        
        const { method, query, body } = req;
        const path = query.path || [];
        
        // 路由处理
        if (method === 'GET' && path[0] === 'health') {
            return res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
        }
        
        if (method === 'GET' && path[0] === 'stats') {
            const total = await keysCollection.countDocuments();
            const active = await keysCollection.countDocuments({ 
                expiresAt: { $gt: new Date() },
                isActive: true 
            });
            const expired = await keysCollection.countDocuments({ 
                expiresAt: { $lte: new Date() } 
            });
            const used = await keysCollection.countDocuments({ 
                usageCount: { $gt: 0 } 
            });
            
            return res.status(200).json({
                success: true,
                total,
                active,
                expired,
                used,
                timestamp: new Date().toISOString()
            });
        }
        
        if (method === 'POST' && path[0] === 'create') {
            const { expiration, description, customKey } = body;
            
            if (!expiration) {
                return res.status(400).json({ error: '有效期不能为空' });
            }
            
            const expiresAt = parseExpiration(expiration);
            if (!expiresAt) {
                return res.status(400).json({ error: '无效的有效期格式' });
            }
            
            const key = customKey || generateKey();
            
            // 检查自定义密钥是否已存在
            if (customKey) {
                const existing = await keysCollection.findOne({ key: customKey });
                if (existing) {
                    return res.status(400).json({ error: '自定义密钥已存在' });
                }
            }
            
            const keyDoc = {
                key,
                description: description || '',
                createdAt: new Date(),
                expiresAt,
                isActive: true,
                usageCount: 0,
                lastUsed: null
            };
            
            await keysCollection.insertOne(keyDoc);
            
            return res.status(201).json({
                success: true,
                message: '密钥创建成功',
                key: keyDoc
            });
        }
        
        if (method === 'POST' && path[0] === 'validate') {
            const { key } = body;
            
            if (!key) {
                return res.status(400).json({ error: '密钥不能为空' });
            }
            
            const keyDoc = await keysCollection.findOne({ key });
            
            if (!keyDoc) {
                return res.status(404).json({ error: '密钥不存在' });
            }
            
            if (!keyDoc.isActive) {
                return res.status(400).json({ error: '密钥已被禁用' });
            }
            
            if (keyDoc.expiresAt <= new Date()) {
                return res.status(400).json({ error: '密钥已过期' });
            }
            
            // 更新使用次数和最后使用时间
            await keysCollection.updateOne(
                { key },
                { 
                    $inc: { usageCount: 1 },
                    $set: { lastUsed: new Date() }
                }
            );
            
            return res.status(200).json({
                success: true,
                message: '密钥验证成功',
                key: keyDoc
            });
        }
        
        if (method === 'GET' && path[0] === 'list') {
            const page = parseInt(query.page) || 1;
            const limit = parseInt(query.limit) || 10;
            const status = query.status;
            
            let filter = {};
            if (status === 'active') {
                filter = { 
                    expiresAt: { $gt: new Date() },
                    isActive: true 
                };
            } else if (status === 'expired') {
                filter = { expiresAt: { $lte: new Date() } };
            } else if (status === 'inactive') {
                filter = { isActive: false };
            }
            
            const total = await keysCollection.countDocuments(filter);
            const keys = await keysCollection
                .find(filter)
                .sort({ createdAt: -1 })
                .skip((page - 1) * limit)
                .limit(limit)
                .toArray();
            
            return res.status(200).json({
                success: true,
                keys,
                pagination: {
                    page,
                    limit,
                    total,
                    pages: Math.ceil(total / limit)
                }
            });
        }
        
        if (method === 'GET' && path[0] === 'details') {
            const key = query.key;
            if (!key) {
                return res.status(400).json({ error: '密钥参数不能为空' });
            }
            
            const keyDoc = await keysCollection.findOne({ key });
            if (!keyDoc) {
                return res.status(404).json({ error: '密钥不存在' });
            }
            
            return res.status(200).json({ key: keyDoc });
        }
        
        if (method === 'DELETE' && path[0] === 'delete') {
            const keyToDelete = query.key;
            if (!keyToDelete) {
                return res.status(400).json({ error: '密钥参数不能为空' });
            }
            
            const result = await keysCollection.deleteOne({ key: keyToDelete });
            
            if (result.deletedCount === 0) {
                return res.status(404).json({ error: '密钥不存在' });
            }
            
            return res.status(200).json({ 
                success: true,
                message: '密钥删除成功' 
            });
        }
        
        return res.status(404).json({ error: '接口不存在' });
        
    } catch (error) {
        console.error('API Error:', error);
        return res.status(500).json({ 
            error: '服务器内部错误',
            details: error.message 
        });
    }
}