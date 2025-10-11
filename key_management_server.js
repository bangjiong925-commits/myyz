import express from 'express';
import cors from 'cors';
import { MongoClient } from 'mongodb';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import crypto from 'crypto';
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 加载环境变量
dotenv.config({ path: join(__dirname, '.env') });

const app = express();
const PORT = process.env.KEY_MANAGEMENT_PORT || 3002;

// 配置 CORS
app.use(cors({
    origin: true,
    credentials: true
}));
app.use(express.json());
app.use(express.static('public'));
// 静态文件服务
app.use(express.static(__dirname));

// MongoDB 配置
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const DATABASE_NAME = process.env.DATABASE_NAME || 'myyz_db';
const KEYS_COLLECTION = 'api_keys';

// 活跃用户会话存储
const activeSessions = new Map(); // sessionId -> { keyUsed, userAgent, ip, lastActivity, keyDetails }

// 清理过期会话的定时器
setInterval(() => {
    const now = Date.now();
    const expiredSessions = [];
    
    for (const [sessionId, session] of activeSessions.entries()) {
        // 如果超过30分钟没有活动，则认为会话过期
        if (now - session.lastActivity > 30 * 60 * 1000) {
            expiredSessions.push(sessionId);
        }
    }
    
    expiredSessions.forEach(sessionId => {
        activeSessions.delete(sessionId);
    });
    
    if (expiredSessions.length > 0) {
        console.log(`🧹 清理了 ${expiredSessions.length} 个过期用户会话`);
    }
}, 5 * 60 * 1000); // 每5分钟检查一次

let db;
let keysCollection;

// 连接 MongoDB
async function connectToMongoDB() {
    try {
        const client = new MongoClient(MONGODB_URI);
        await client.connect();
        db = client.db(DATABASE_NAME);
        keysCollection = db.collection(KEYS_COLLECTION);
        
        // 创建索引
        await keysCollection.createIndex({ "key": 1 }, { unique: true });
        await keysCollection.createIndex({ "status": 1 });
        await keysCollection.createIndex({ "expiresAt": 1 });
        
        console.log('✅ MongoDB 连接成功');
        console.log(`📊 数据库: ${DATABASE_NAME}`);
        console.log(`🔑 密钥集合: ${KEYS_COLLECTION}`);
    } catch (error) {
        console.error('❌ MongoDB 连接失败:', error);
        process.exit(1);
    }
}

// 生成增强校验和（6个字符）- 与TWPK.html保持一致
function generateEnhancedChecksum(input) {
    let hash1 = 0;
    let hash2 = 0;
    
    for (let i = 0; i < input.length; i++) {
        const char = input.charCodeAt(i);
        // 第一个哈希
        hash1 = ((hash1 << 5) - hash1) + char;
        hash1 = hash1 & hash1;
        
        // 第二个哈希（不同的算法）
        hash2 = ((hash2 << 3) + hash2) ^ char;
        hash2 = hash2 & hash2;
    }
    
    // 组合两个哈希值
    const combinedHash = Math.abs(hash1) + Math.abs(hash2);
    
    // 生成6位校验和
    let checksum = combinedHash.toString(36).substring(0, 6);
    if (checksum.length < 6) {
        // 如果不足6位，用确定性字符补充
        const padding = '0123456789abcdefghijklmnopqrstuvwxyz';
        for (let i = checksum.length; i < 6; i++) {
            checksum += padding[(combinedHash + i) % padding.length];
        }
    }
    
    return checksum.substring(0, 6);
}

// 生成安全随机字符串
function generateSecureRandomString(length) {
    const chars = '0123456789abcdefghijklmnopqrstuvwxyz';
    
    let result = '';
    for (let i = 0; i < length; i++) {
        const randomByte = crypto.randomBytes(1)[0];
        result += chars[randomByte % chars.length];
    }
    return result;
}

// 生成指定范围内的安全随机数
function getSecureRandom(min, max) {
    const randomByte = crypto.randomBytes(4);
    const randomValue = randomByte.readUInt32BE(0);
    return min + (randomValue % (max - min + 1));
}

// 生成高随机性标识符（4个字符）
function generateHighRandomIdentifier(validityPeriodSeconds) {
    // 根据有效期生成基础类型码（只用1位）
    let typeCode;
    if (validityPeriodSeconds <= 60) {
        typeCode = '1'; // 1分钟
    } else if (validityPeriodSeconds <= 2 * 60 * 60) {
        typeCode = 'H'; // 2小时
    } else if (validityPeriodSeconds <= 3 * 24 * 60 * 60) {
        typeCode = '3'; // 3天
    } else if (validityPeriodSeconds <= 7 * 24 * 60 * 60) {
        typeCode = '7'; // 7天
    } else if (validityPeriodSeconds <= 30 * 24 * 60 * 60) {
        typeCode = 'M'; // 30天（月）
    } else if (validityPeriodSeconds <= 90 * 24 * 60 * 60) {
        typeCode = 'Q'; // 90天（季）
    } else {
        typeCode = 'Y'; // 365天或更长（年）
    }
    
    // 生成3位高随机性后缀
    const randomSuffix = generateSecureRandomString(3);
    
    return typeCode + randomSuffix;
}

// 生成22位短密钥（与本地工具算法完全一致）
function generateKey(validityPeriodSeconds) {
    // 计算过期时间戳
    const currentTime = Math.floor(Date.now() / 1000);
    
    // 添加随机扰动到时间戳（±30秒内的随机偏移）
    const randomOffset = getSecureRandom(-30, 30);
    const expiryTime = currentTime + validityPeriodSeconds + randomOffset;
    
    // 生成核心数据
    const identifier = generateHighRandomIdentifier(validityPeriodSeconds);
    const timestampPart = expiryTime.toString(36).substring(-6).padStart(6, '0'); // 6位时间戳
    
    // 扩大随机填充部分（使用加密安全的随机数）
    const randomPadding = generateSecureRandomString(6); // 6位安全随机字符
    
    // 组合密钥：4位标识符 + 6位时间戳 + 6位随机 + 6位校验 = 22位
    const coreData = identifier + timestampPart + randomPadding;
    const checksum = generateEnhancedChecksum(coreData);
    
    return coreData + checksum;
}

// 计算剩余时间（毫秒）
function calculateRemainingTime(expiresAt) {
    const now = new Date();
    const expiry = new Date(expiresAt);
    return Math.max(0, expiry.getTime() - now.getTime());
}

// 格式化时间显示
function formatDuration(milliseconds) {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}天 ${hours % 24}小时`;
    if (hours > 0) return `${hours}小时 ${minutes % 60}分钟`;
    if (minutes > 0) return `${minutes}分钟 ${seconds % 60}秒`;
    return `${seconds}秒`;
}

// API 路由

// 健康检查
app.get('/api/health', async (req, res) => {
    try {
        await keysCollection.findOne({});
        res.json({
            status: 'ok',
            service: 'Key Management API',
            database: 'connected',
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            status: 'error',
            service: 'Key Management API',
            database: 'disconnected',
            error: error.message
        });
    }
});

// 创建新密钥
app.post('/api/keys', async (req, res) => {
    try {
        const { duration, unit, description, customKey } = req.body;
        
        if (!duration || duration <= 0) {
            return res.status(400).json({
                success: false,
                message: '请提供有效的持续时间'
            });
        }
        
        if (!unit || !['minutes', 'hours', 'days', 'months'].includes(unit)) {
            return res.status(400).json({
                success: false,
                message: '请提供有效的时间单位（minutes/hours/days/months）'
            });
        }
        
        // 验证时间限制
        if (unit === 'minutes' && duration > 60) { // 最多60分钟
            return res.status(400).json({
                success: false,
                message: '分钟数不能超过60分钟'
            });
        }
        
        if (unit === 'hours' && duration > 24 * 30) { // 最多30天的小时数
            return res.status(400).json({
                success: false,
                message: '小时数不能超过720小时（30天）'
            });
        }
        
        if (unit === 'days' && duration > 30) {
            return res.status(400).json({
                success: false,
                message: '天数不能超过30天'
            });
        }
        
        if (unit === 'months' && duration > 12) {
            return res.status(400).json({
                success: false,
                message: '月数不能超过12个月'
            });
        }
        
        // 根据单位计算秒数（用于密钥生成）
        let durationSeconds;
        switch (unit) {
            case 'minutes':
                durationSeconds = duration * 60;
                break;
            case 'hours':
                durationSeconds = duration * 60 * 60;
                break;
            case 'days':
                durationSeconds = duration * 24 * 60 * 60;
                break;
            case 'months':
                durationSeconds = duration * 30 * 24 * 60 * 60; // 按30天计算
                break;
            default:
                durationSeconds = duration * 60 * 60; // 默认小时
        }
        
        const key = customKey || generateKey(durationSeconds);
        const now = new Date();
        
        // 根据单位计算毫秒数（用于数据库存储）
        let durationMs;
        switch (unit) {
            case 'hours':
                durationMs = duration * 60 * 60 * 1000;
                break;
            case 'days':
                durationMs = duration * 24 * 60 * 60 * 1000;
                break;
            case 'months':
                durationMs = duration * 30 * 24 * 60 * 60 * 1000; // 按30天计算
                break;
        }
        
        const expiresAt = new Date(now.getTime() + durationMs);
        
        // 检查密钥是否已存在
        const existingKey = await keysCollection.findOne({ key });
        if (existingKey) {
            return res.status(409).json({
                success: false,
                message: '密钥已存在，请使用其他密钥'
            });
        }
        
        const keyDocument = {
            key,
            description: description || '',
            status: 'active',
            createdAt: now,
            activatedAt: null,
            expiresAt,
            totalDuration: durationMs,
            usageCount: 0,
            lastUsed: null,
            createdBy: req.ip || 'unknown'
        };
        
        await keysCollection.insertOne(keyDocument);
        
        res.json({
            success: true,
            message: '密钥创建成功',
            data: {
                key,
                description: keyDocument.description,
                status: keyDocument.status,
                createdAt: keyDocument.createdAt,
                expiresAt: keyDocument.expiresAt,
                totalDuration: formatDuration(durationMs),
                remainingTime: formatDuration(durationMs)
            }
        });
    } catch (error) {
        console.error('创建密钥错误:', error);
        res.status(500).json({
            success: false,
            message: '创建密钥失败',
            error: error.message
        });
    }
});

// 验证密钥
app.post('/api/keys/validate', async (req, res) => {
    try {
        const { key } = req.body;
        
        if (!key) {
            return res.status(400).json({
                success: false,
                message: '请提供密钥'
            });
        }
        
        const keyDocument = await keysCollection.findOne({ key });
        
        if (!keyDocument) {
            return res.status(404).json({
                success: false,
                message: '密钥不存在'
            });
        }
        
        const now = new Date();
        const remainingTime = calculateRemainingTime(keyDocument.expiresAt);
        
        // 检查密钥是否过期
        if (remainingTime <= 0) {
            await keysCollection.updateOne(
                { key },
                { 
                    $set: { 
                        status: 'expired',
                        lastUsed: now
                    }
                }
            );
            
            return res.status(410).json({
                success: false,
                message: '密钥已过期',
                data: {
                    key,
                    status: 'expired',
                    expiresAt: keyDocument.expiresAt,
                    remainingTime: '0秒'
                }
            });
        }
        
        // 检查密钥状态
        if (keyDocument.status !== 'active') {
            return res.status(403).json({
                success: false,
                message: `密钥状态异常: ${keyDocument.status}`,
                data: {
                    key,
                    status: keyDocument.status,
                    remainingTime: formatDuration(remainingTime)
                }
            });
        }
        
        // 更新使用记录
        await keysCollection.updateOne(
            { key },
            { 
                $set: { 
                    lastUsed: now,
                    activatedAt: keyDocument.activatedAt || now
                },
                $inc: { usageCount: 1 }
            }
        );

        // 记录用户会话
        const sessionId = crypto.randomUUID();
        const userAgent = req.headers['user-agent'] || 'Unknown';
        const clientIP = req.ip || req.connection.remoteAddress || 'Unknown';
        
        activeSessions.set(sessionId, {
            keyUsed: key,
            userAgent,
            ip: clientIP,
            lastActivity: now.getTime(),
            keyDetails: {
                description: keyDocument.description,
                expiresAt: keyDocument.expiresAt,
                usageCount: (keyDocument.usageCount || 0) + 1
            }
        });
        
        res.json({
            success: true,
            message: '密钥验证成功',
            data: {
                key,
                description: keyDocument.description,
                status: 'active',
                createdAt: keyDocument.createdAt,
                activatedAt: keyDocument.activatedAt || now,
                expiresAt: keyDocument.expiresAt,
                totalDuration: formatDuration(keyDocument.totalDuration),
                remainingTime: formatDuration(remainingTime),
                usageCount: keyDocument.usageCount + 1
            }
        });
    } catch (error) {
        console.error('验证密钥错误:', error);
        res.status(500).json({
            success: false,
            message: '验证密钥失败',
            error: error.message
        });
    }
});

// 检查密钥使用状态并自动注册新密钥
app.post('/api/keys/check-usage', async (req, res) => {
    try {
        const { key } = req.body;
        
        if (!key) {
            return res.status(400).json({
                success: false,
                message: '请提供密钥'
            });
        }

        // 首先检查密钥是否已存在
        const existingKey = await keysCollection.findOne({ key });
        
        if (existingKey) {
            // 密钥已存在，检查状态
            const now = new Date();
            const remainingTime = calculateRemainingTime(existingKey.expiresAt);
            
            if (remainingTime <= 0) {
                return res.json({
                    success: false,
                    exists: true,
                    used: true,
                    expired: true,
                    message: '密钥已过期',
                    data: {
                        key,
                        status: 'expired',
                        expiresAt: existingKey.expiresAt,
                        usageCount: existingKey.usageCount || 0
                    }
                });
            }
            
            return res.json({
                success: false,
                exists: true,
                used: true,
                expired: false,
                message: '密钥已被使用',
                data: {
                    key,
                    status: existingKey.status,
                    createdAt: existingKey.createdAt,
                    expiresAt: existingKey.expiresAt,
                    usageCount: existingKey.usageCount || 0,
                    lastUsed: existingKey.lastUsed
                }
            });
        }

        // 密钥不存在，验证密钥格式并自动注册
        try {
            // 验证短密钥格式
            if (key.length <= 25 && key.length >= 20) {
                const identifier = key.substring(0, 4);
                const timestampPart = key.substring(4, 10);
                const randomPadding = key.substring(10, 16);
                const checksum = key.substring(16, 22);

                // 解析过期时间
                const expiry = parseInt(timestampPart, 36);
                
                if (isNaN(expiry) || expiry <= 0) {
                    return res.status(400).json({
                        success: false,
                        exists: false,
                        message: '密钥格式无效：时间戳无效'
                    });
                }

                // 检查是否过期
                const currentTime = Math.floor(Date.now() / 1000);
                if (currentTime > expiry) {
                    return res.json({
                        success: false,
                        exists: false,
                        expired: true,
                        message: '密钥已过期'
                    });
                }

                // 验证校验和
                const expectedChecksum = generateEnhancedChecksum(identifier + timestampPart + randomPadding);
                if (checksum !== expectedChecksum) {
                    return res.status(400).json({
                        success: false,
                        exists: false,
                        message: '密钥格式无效：校验失败'
                    });
                }

                // 密钥有效且不存在，自动注册到数据库
                const now = new Date();
                const expiresAt = new Date(expiry * 1000);
                const totalDuration = expiresAt.getTime() - now.getTime();

                const newKeyDocument = {
                    key,
                    description: `自动注册的短密钥 - ${identifier}`,
                    status: 'active',
                    createdAt: now,
                    expiresAt: expiresAt,
                    totalDuration: totalDuration,
                    usageCount: 0,
                    autoRegistered: true,
                    keyType: 'short',
                    identifier: identifier
                };

                await keysCollection.insertOne(newKeyDocument);

                return res.json({
                    success: true,
                    exists: false,
                    used: false,
                    autoRegistered: true,
                    message: '密钥有效，已自动注册到数据库',
                    data: {
                        key,
                        status: 'active',
                        createdAt: now,
                        expiresAt: expiresAt,
                        totalDuration: formatDuration(totalDuration),
                        remainingTime: formatDuration(totalDuration),
                        usageCount: 0
                    }
                });
            } else {
                return res.status(400).json({
                    success: false,
                    exists: false,
                    message: '不支持的密钥格式'
                });
            }
        } catch (error) {
            return res.status(400).json({
                success: false,
                exists: false,
                message: '密钥格式验证失败：' + error.message
            });
        }
    } catch (error) {
        console.error('检查密钥使用状态错误:', error);
        res.status(500).json({
            success: false,
            message: '检查密钥使用状态失败',
            error: error.message
        });
    }
});

// 修改现有的验证API，支持自动注册
app.post('/api/keys/validate-and-register', async (req, res) => {
    try {
        const { key } = req.body;
        
        if (!key) {
            return res.status(400).json({
                success: false,
                message: '请提供密钥'
            });
        }

        // 首先检查使用状态
        const checkResponse = await fetch(`http://localhost:${PORT}/api/keys/check-usage`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ key })
        });

        const checkResult = await checkResponse.json();

        if (!checkResult.success) {
            if (checkResult.exists && checkResult.used) {
                return res.status(409).json({
                    success: false,
                    message: checkResult.expired ? '密钥已过期' : '密钥已被使用，每个密钥只能使用一次',
                    data: checkResult.data
                });
            } else {
                return res.status(400).json({
                    success: false,
                    message: checkResult.message
                });
            }
        }

        // 密钥有效且已注册，现在进行验证和使用
        const keyDocument = await keysCollection.findOne({ key });
        
        if (!keyDocument) {
            return res.status(404).json({
                success: false,
                message: '密钥注册失败'
            });
        }

        const now = new Date();
        const remainingTime = calculateRemainingTime(keyDocument.expiresAt);

        // 更新使用记录
        await keysCollection.updateOne(
            { key },
            { 
                $set: { 
                    lastUsed: now,
                    activatedAt: keyDocument.activatedAt || now
                },
                $inc: { usageCount: 1 }
            }
        );

        // 记录用户会话
        const sessionId = crypto.randomUUID();
        const userAgent = req.headers['user-agent'] || 'Unknown';
        const clientIP = req.ip || req.connection.remoteAddress || 'Unknown';
        
        activeSessions.set(sessionId, {
            keyUsed: key,
            userAgent,
            ip: clientIP,
            lastActivity: now.getTime(),
            keyDetails: {
                description: keyDocument.description,
                expiresAt: keyDocument.expiresAt,
                usageCount: (keyDocument.usageCount || 0) + 1
            }
        });

        res.json({
            success: true,
            message: checkResult.autoRegistered ? '密钥验证成功（已自动注册）' : '密钥验证成功',
            data: {
                key,
                description: keyDocument.description,
                status: 'active',
                createdAt: keyDocument.createdAt,
                activatedAt: keyDocument.activatedAt || now,
                expiresAt: keyDocument.expiresAt,
                totalDuration: formatDuration(keyDocument.totalDuration),
                remainingTime: formatDuration(remainingTime),
                usageCount: (keyDocument.usageCount || 0) + 1,
                autoRegistered: checkResult.autoRegistered,
                sessionId: sessionId
            }
        });
    } catch (error) {
        console.error('验证并注册密钥错误:', error);
        res.status(500).json({
            success: false,
            message: '验证并注册密钥失败',
            error: error.message
        });
    }
});

// 获取所有密钥
app.get('/api/keys', async (req, res) => {
    try {
        const { status, page = 1, limit = 20 } = req.query;
        const skip = (page - 1) * limit;
        
        const filter = {};
        if (status) filter.status = status;
        
        const keys = await keysCollection
            .find(filter)
            .sort({ createdAt: -1 })
            .skip(skip)
            .limit(parseInt(limit))
            .toArray();
        
        const total = await keysCollection.countDocuments(filter);
        
        // 计算每个密钥的剩余时间
        const keysWithRemainingTime = keys.map(keyDoc => {
            const remainingTime = calculateRemainingTime(keyDoc.expiresAt);
            return {
                ...keyDoc,
                remainingTime: formatDuration(remainingTime),
                totalDuration: formatDuration(keyDoc.totalDuration),
                isExpired: remainingTime <= 0
            };
        });
        
        res.json({
            success: true,
            data: keysWithRemainingTime,
            pagination: {
                page: parseInt(page),
                limit: parseInt(limit),
                total,
                pages: Math.ceil(total / limit)
            }
        });
    } catch (error) {
        console.error('获取密钥列表错误:', error);
        res.status(500).json({
            success: false,
            message: '获取密钥列表失败',
            error: error.message
        });
    }
});

// 获取单个密钥详情
app.get('/api/keys/:key', async (req, res) => {
    try {
        const { key } = req.params;
        
        const keyDocument = await keysCollection.findOne({ key });
        
        if (!keyDocument) {
            return res.status(404).json({
                success: false,
                message: '密钥不存在'
            });
        }
        
        const remainingTime = calculateRemainingTime(keyDocument.expiresAt);
        
        res.json({
            success: true,
            data: {
                ...keyDocument,
                remainingTime: formatDuration(remainingTime),
                totalDuration: formatDuration(keyDocument.totalDuration),
                isExpired: remainingTime <= 0
            }
        });
    } catch (error) {
        console.error('获取密钥详情错误:', error);
        res.status(500).json({
            success: false,
            message: '获取密钥详情失败',
            error: error.message
        });
    }
});

// 更新密钥
app.put('/api/keys/:key', async (req, res) => {
    try {
        const { key } = req.params;
        const { description, status, extendHours } = req.body;
        
        const keyDocument = await keysCollection.findOne({ key });
        
        if (!keyDocument) {
            return res.status(404).json({
                success: false,
                message: '密钥不存在'
            });
        }
        
        const updateData = {};
        
        if (description !== undefined) updateData.description = description;
        if (status !== undefined) updateData.status = status;
        
        // 延长时间
        if (extendHours && extendHours > 0) {
            const extensionMs = extendHours * 60 * 60 * 1000;
            updateData.expiresAt = new Date(keyDocument.expiresAt.getTime() + extensionMs);
            updateData.totalDuration = keyDocument.totalDuration + extensionMs;
        }
        
        updateData.updatedAt = new Date();
        
        await keysCollection.updateOne({ key }, { $set: updateData });
        
        const updatedKey = await keysCollection.findOne({ key });
        const remainingTime = calculateRemainingTime(updatedKey.expiresAt);
        
        res.json({
            success: true,
            message: '密钥更新成功',
            data: {
                ...updatedKey,
                remainingTime: formatDuration(remainingTime),
                totalDuration: formatDuration(updatedKey.totalDuration),
                isExpired: remainingTime <= 0
            }
        });
    } catch (error) {
        console.error('更新密钥错误:', error);
        res.status(500).json({
            success: false,
            message: '更新密钥失败',
            error: error.message
        });
    }
});

// 删除密钥
app.delete('/api/keys/:key', async (req, res) => {
    try {
        const { key } = req.params;
        
        const result = await keysCollection.deleteOne({ key });
        
        if (result.deletedCount === 0) {
            return res.status(404).json({
                success: false,
                message: '密钥不存在'
            });
        }
        
        res.json({
            success: true,
            message: '密钥删除成功'
        });
    } catch (error) {
        console.error('删除密钥错误:', error);
        res.status(500).json({
            success: false,
            message: '删除密钥失败',
            error: error.message
        });
    }
});

// 密钥延期接口
app.post('/api/keys/:key/extend', async (req, res) => {
    try {
        const { key } = req.params;
        const { extendDuration, extendUnit } = req.body;
        
        if (!key) {
            return res.status(400).json({
                success: false,
                message: '密钥不能为空'
            });
        }
        
        if (!extendDuration || !extendUnit) {
            return res.status(400).json({
                success: false,
                message: '延期时长和单位不能为空'
            });
        }
        
        // 验证延期参数
        const duration = parseInt(extendDuration);
        if (isNaN(duration) || duration <= 0) {
            return res.status(400).json({
                success: false,
                message: '延期时长必须是正整数'
            });
        }
        
        // 计算延期时间（毫秒）
        let extendMs = 0;
        switch (extendUnit) {
            case 'minutes':
                if (duration > 60) {
                    return res.status(400).json({
                        success: false,
                        message: '分钟数不能超过60分钟'
                    });
                }
                extendMs = duration * 60 * 1000;
                break;
            case 'hours':
                if (duration > 24) {
                    return res.status(400).json({
                        success: false,
                        message: '小时数不能超过24小时'
                    });
                }
                extendMs = duration * 60 * 60 * 1000;
                break;
            case 'days':
                if (duration > 30) {
                    return res.status(400).json({
                        success: false,
                        message: '天数不能超过30天'
                    });
                }
                extendMs = duration * 24 * 60 * 60 * 1000;
                break;
            case 'months':
                if (duration > 12) {
                    return res.status(400).json({
                        success: false,
                        message: '月数不能超过12个月'
                    });
                }
                extendMs = duration * 30 * 24 * 60 * 60 * 1000;
                break;
            default:
                return res.status(400).json({
                    success: false,
                    message: '无效的时间单位，支持: minutes, hours, days, months'
                });
        }
        
        // 查找密钥
        const existingKey = await keysCollection.findOne({ key });
        if (!existingKey) {
            return res.status(404).json({
                success: false,
                message: '密钥不存在'
            });
        }
        
        // 计算新的过期时间
        const now = new Date();
        const currentExpiresAt = new Date(existingKey.expiresAt);
        const newExpiresAt = new Date(Math.max(currentExpiresAt.getTime(), now.getTime()) + extendMs);
        
        // 更新密钥
        const updateResult = await keysCollection.updateOne(
            { key },
            {
                $set: {
                    expiresAt: newExpiresAt,
                    status: 'active',
                    updatedAt: now,
                    lastExtended: now,
                    extensionHistory: {
                        ...existingKey.extensionHistory,
                        [now.toISOString()]: {
                            duration: duration,
                            unit: extendUnit,
                            extendedBy: req.session.username,
                            previousExpiresAt: existingKey.expiresAt
                        }
                    }
                }
            }
        );
        
        if (updateResult.modifiedCount === 0) {
            return res.status(500).json({
                success: false,
                message: '密钥延期失败'
            });
        }
        
        // 获取更新后的密钥信息
        const updatedKey = await keysCollection.findOne({ key });
        const remainingTime = calculateRemainingTime(updatedKey.expiresAt);
        
        res.json({
            success: true,
            message: `密钥延期成功，延长了${duration}${extendUnit === 'minutes' ? '分钟' : extendUnit === 'hours' ? '小时' : extendUnit === 'days' ? '天' : '个月'}`,
            data: {
                key: updatedKey.key,
                description: updatedKey.description,
                status: updatedKey.status,
                expiresAt: updatedKey.expiresAt,
                remainingTime: formatDuration(remainingTime),
                totalDuration: formatDuration(updatedKey.totalDuration),
                lastExtended: updatedKey.lastExtended,
                extendedBy: req.session.username
            }
        });
    } catch (error) {
        console.error('密钥延期错误:', error);
        res.status(500).json({
            success: false,
            message: '密钥延期失败',
            error: error.message
        });
    }
});

// 获取密钥统计信息
app.get('/api/keys/stats/summary', async (req, res) => {
    try {
        const now = new Date();
        
        const [total, active, expired, used] = await Promise.all([
            keysCollection.countDocuments({}),
            keysCollection.countDocuments({ status: 'active', expiresAt: { $gt: now } }),
            keysCollection.countDocuments({ $or: [{ status: 'expired' }, { expiresAt: { $lte: now } }] }),
            keysCollection.countDocuments({ usageCount: { $gt: 0 } })
        ]);
        
        res.json({
            success: true,
            data: {
                total,
                active,
                expired,
                used,
                unused: total - used,
                timestamp: now.toISOString()
            }
        });
    } catch (error) {
        console.error('获取统计信息错误:', error);
        res.status(500).json({
            success: false,
            message: '获取统计信息失败',
            error: error.message
        });
    }
});

// 获取活跃用户列表
app.get('/api/sessions/active', async (req, res) => {
    try {
        const now = Date.now();
        const activeUsers = [];
        
        for (const [sessionId, session] of activeSessions.entries()) {
            // 计算会话持续时间
            const sessionDuration = now - session.lastActivity;
            const isActive = sessionDuration < 30 * 60 * 1000; // 30分钟内活跃
            
            if (isActive) {
                activeUsers.push({
                    sessionId,
                    keyUsed: session.keyUsed,
                    userAgent: session.userAgent,
                    ip: session.ip,
                    lastActivity: new Date(session.lastActivity).toISOString(),
                    sessionDuration: formatDuration(sessionDuration),
                    keyDetails: session.keyDetails
                });
            }
        }
        
        // 按最后活动时间排序（最近的在前）
        activeUsers.sort((a, b) => new Date(b.lastActivity) - new Date(a.lastActivity));
        
        res.json({
            success: true,
            message: '获取活跃用户成功',
            data: {
                totalActiveSessions: activeUsers.length,
                sessions: activeUsers,
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('获取活跃用户错误:', error);
        res.status(500).json({
            success: false,
            message: '获取活跃用户失败',
            error: error.message
        });
    }
});

// 清理过期密钥
app.post('/api/keys/cleanup', async (req, res) => {
    try {
        const now = new Date();
        
        // 更新过期密钥状态
        const updateResult = await keysCollection.updateMany(
            { expiresAt: { $lte: now }, status: { $ne: 'expired' } },
            { $set: { status: 'expired', updatedAt: now } }
        );
        
        // 可选：删除过期超过指定天数的密钥
        const { deleteExpired } = req.body;
        let deleteResult = { deletedCount: 0 };
        
        if (deleteExpired) {
            const deleteThreshold = new Date(now.getTime() - (deleteExpired * 24 * 60 * 60 * 1000));
            deleteResult = await keysCollection.deleteMany({
                status: 'expired',
                expiresAt: { $lte: deleteThreshold }
            });
        }
        
        res.json({
            success: true,
            message: '清理完成',
            data: {
                updatedExpired: updateResult.modifiedCount,
                deletedExpired: deleteResult.deletedCount,
                timestamp: now.toISOString()
            }
        });
    } catch (error) {
        console.error('清理过期密钥错误:', error);
        res.status(500).json({
            success: false,
            message: '清理过期密钥失败',
            error: error.message
        });
    }
});

// ==================== 数据库管理API接口 ====================

// 获取数据库列表和统计信息
app.get('/api/database/info', async (req, res) => {
    try {
        const client = db.client;
        const admin = client.db().admin();
        
        // 获取数据库列表
        const databasesList = await admin.listDatabases();
        
        // 获取当前连接的数据库信息
        const currentDbStats = await db.stats();
        
        // 获取各个数据库的详细信息
        const databases = [];
        for (const dbInfo of databasesList.databases) {
            try {
                const database = client.db(dbInfo.name);
                const collections = await database.listCollections().toArray();
                const stats = await database.stats();
                
                databases.push({
                    name: dbInfo.name,
                    sizeOnDisk: dbInfo.sizeOnDisk,
                    empty: dbInfo.empty,
                    collections: collections.map(col => ({
                        name: col.name,
                        type: col.type
                    })),
                    stats: {
                        collections: stats.collections,
                        objects: stats.objects,
                        dataSize: stats.dataSize,
                        storageSize: stats.storageSize,
                        indexes: stats.indexes,
                        indexSize: stats.indexSize
                    }
                });
            } catch (error) {
                console.warn(`无法获取数据库 ${dbInfo.name} 的详细信息:`, error.message);
                databases.push({
                    name: dbInfo.name,
                    sizeOnDisk: dbInfo.sizeOnDisk,
                    empty: dbInfo.empty,
                    error: error.message
                });
            }
        }
        
        res.json({
            success: true,
            data: {
                currentDatabase: DATABASE_NAME,
                totalDatabases: databasesList.totalSize,
                databases: databases,
                currentDbStats: currentDbStats
            }
        });
    } catch (error) {
        console.error('获取数据库信息错误:', error);
        res.status(500).json({
            success: false,
            message: '获取数据库信息失败',
            error: error.message
        });
    }
});

// 获取PK10数据统计
app.get('/api/database/pk10/stats', async (req, res) => {
    try {
        const pk10Database = db.client.db('taiwan_pk10');
        const pk10Collection = pk10Database.collection('pk10_results');
        
        // 获取基本统计信息
        const totalCount = await pk10Collection.countDocuments();
        const latestData = await pk10Collection.findOne({}, { sort: { timestamp: -1 } });
        const oldestData = await pk10Collection.findOne({}, { sort: { timestamp: 1 } });
        
        // 获取今日数据统计
        const today = new Date();
        const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
        const todayCount = await pk10Collection.countDocuments({
            timestamp: { $gte: todayStart.toISOString() }
        });
        
        // 获取最近7天的数据统计
        const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
        const weekCount = await pk10Collection.countDocuments({
            timestamp: { $gte: weekAgo.toISOString() }
        });
        
        // 获取数据库大小信息
        const dbStats = await pk10Database.stats();
        
        res.json({
            success: true,
            data: {
                totalRecords: totalCount,
                todayRecords: todayCount,
                weekRecords: weekCount,
                latestRecord: latestData ? {
                    issue: latestData.issue,
                    numbers: latestData.numbers,
                    timestamp: latestData.timestamp
                } : null,
                oldestRecord: oldestData ? {
                    issue: oldestData.issue,
                    timestamp: oldestData.timestamp
                } : null,
                databaseStats: {
                    collections: dbStats.collections,
                    objects: dbStats.objects,
                    dataSize: dbStats.dataSize,
                    storageSize: dbStats.storageSize,
                    indexes: dbStats.indexes,
                    indexSize: dbStats.indexSize
                }
            }
        });
    } catch (error) {
        console.error('获取PK10数据统计错误:', error);
        res.status(500).json({
            success: false,
            message: '获取PK10数据统计失败',
            error: error.message
        });
    }
});

// 获取PK10数据列表
app.get('/api/database/pk10/data', async (req, res) => {
    try {
        const pk10Database = db.client.db('taiwan_pk10');
        const pk10Collection = pk10Database.collection('pk10_results');
        
        const page = parseInt(req.query.page) || 1;
        const limit = parseInt(req.query.limit) || 20;
        const skip = (page - 1) * limit;
        
        // 获取数据
        const data = await pk10Collection
            .find({})
            .sort({ timestamp: -1 })
            .skip(skip)
            .limit(limit)
            .toArray();
        
        // 获取总数
        const total = await pk10Collection.countDocuments();
        
        res.json({
            success: true,
            data: {
                records: data.map(record => ({
                    _id: record._id,
                    issue: record.issue,
                    numbers: record.numbers,
                    date: record.date,
                    time: record.time,
                    timestamp: record.timestamp
                })),
                pagination: {
                    page: page,
                    limit: limit,
                    total: total,
                    pages: Math.ceil(total / limit)
                }
            }
        });
    } catch (error) {
        console.error('获取PK10数据列表错误:', error);
        res.status(500).json({
            success: false,
            message: '获取PK10数据列表失败',
            error: error.message
        });
    }
});

// 搜索PK10数据
app.get('/api/database/pk10/search', async (req, res) => {
    try {
        const pk10Database = db.client.db('taiwan_pk10');
        const pk10Collection = pk10Database.collection('pk10_results');
        
        const { issue, date, startDate, endDate } = req.query;
        const page = parseInt(req.query.page) || 1;
        const limit = parseInt(req.query.limit) || 20;
        const skip = (page - 1) * limit;
        
        // 构建查询条件
        let query = {};
        
        if (issue) {
            query.issue = { $regex: issue, $options: 'i' };
        }
        
        if (date) {
            query.date = date;
        }
        
        if (startDate && endDate) {
            query.date = {
                $gte: startDate,
                $lte: endDate
            };
        }
        
        // 获取数据
        const data = await pk10Collection
            .find(query)
            .sort({ timestamp: -1 })
            .skip(skip)
            .limit(limit)
            .toArray();
        
        // 获取总数
        const total = await pk10Collection.countDocuments(query);
        
        res.json({
            success: true,
            data: {
                records: data.map(record => ({
                    _id: record._id,
                    issue: record.issue,
                    numbers: record.numbers,
                    date: record.date,
                    time: record.time,
                    timestamp: record.timestamp
                })),
                pagination: {
                    page: page,
                    limit: limit,
                    total: total,
                    pages: Math.ceil(total / limit)
                },
                query: query
            }
        });
    } catch (error) {
        console.error('搜索PK10数据错误:', error);
        res.status(500).json({
            success: false,
            message: '搜索PK10数据失败',
            error: error.message
        });
    }
});

// 删除PK10数据记录
app.delete('/api/database/pk10/data/:id', async (req, res) => {
    try {
        const pk10Database = db.client.db('taiwan_pk10');
        const pk10Collection = pk10Database.collection('pk10_results');
        
        const { id } = req.params;
        
        // 验证ObjectId格式
        if (!id.match(/^[0-9a-fA-F]{24}$/)) {
            return res.status(400).json({
                success: false,
                message: '无效的记录ID格式'
            });
        }
        
        const result = await pk10Collection.deleteOne({ _id: new db.client.ObjectId(id) });
        
        if (result.deletedCount === 0) {
            return res.status(404).json({
                success: false,
                message: '记录不存在'
            });
        }
        
        res.json({
            success: true,
            message: '记录删除成功',
            data: {
                deletedId: id,
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('删除PK10数据记录错误:', error);
        res.status(500).json({
            success: false,
            message: '删除记录失败',
            error: error.message
        });
    }
});

// 数据库备份
app.post('/api/database/backup', async (req, res) => {
    try {
        const { databases } = req.body;
        const backupData = {};
        
        // 如果没有指定数据库，备份所有数据库
        const databasesToBackup = databases || ['taiwan_pk10', 'myyz_db'];
        
        for (const dbName of databasesToBackup) {
            try {
                const database = db.client.db(dbName);
                const collections = await database.listCollections().toArray();
                
                backupData[dbName] = {};
                
                for (const collectionInfo of collections) {
                    const collection = database.collection(collectionInfo.name);
                    const data = await collection.find({}).toArray();
                    backupData[dbName][collectionInfo.name] = data;
                }
            } catch (error) {
                console.warn(`备份数据库 ${dbName} 时出错:`, error.message);
                backupData[dbName] = { error: error.message };
            }
        }
        
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `database_backup_${timestamp}.json`;
        
        res.setHeader('Content-Type', 'application/json');
        res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
        res.json({
            success: true,
            timestamp: new Date().toISOString(),
            databases: databasesToBackup,
            data: backupData
        });
    } catch (error) {
        console.error('数据库备份错误:', error);
        res.status(500).json({
            success: false,
            message: '数据库备份失败',
            error: error.message
        });
    }
});

// 清理旧数据
app.post('/api/database/cleanup', async (req, res) => {
    try {
        const { database, collection, days } = req.body;
        
        if (!database || !collection || !days) {
            return res.status(400).json({
                success: false,
                message: '缺少必要参数: database, collection, days'
            });
        }
        
        const targetDatabase = db.client.db(database);
        const targetCollection = targetDatabase.collection(collection);
        
        // 计算删除阈值时间
        const deleteThreshold = new Date(Date.now() - (days * 24 * 60 * 60 * 1000));
        
        // 删除旧数据
        const result = await targetCollection.deleteMany({
            timestamp: { $lt: deleteThreshold.toISOString() }
        });
        
        res.json({
            success: true,
            message: `清理完成，删除了 ${result.deletedCount} 条记录`,
            data: {
                database: database,
                collection: collection,
                deletedCount: result.deletedCount,
                threshold: deleteThreshold.toISOString(),
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('清理旧数据错误:', error);
        res.status(500).json({
            success: false,
            message: '清理旧数据失败',
            error: error.message
        });
    }
});

// 启动服务器
async function startServer() {
    await connectToMongoDB();
    
    app.listen(PORT, () => {
        console.log(`🚀 密钥管理服务器启动成功`);
        console.log(`📡 服务地址: http://localhost:${PORT}`);
        console.log(`🔑 API 接口:`);
        console.log(`   GET  /api/health              - 健康检查`);
        console.log(`   POST /api/keys                - 创建密钥`);
        console.log(`   POST /api/keys/validate       - 验证密钥`);
        console.log(`   GET  /api/keys                - 获取密钥列表`);
        console.log(`   GET  /api/keys/:key           - 获取密钥详情`);
        console.log(`   PUT  /api/keys/:key           - 更新密钥`);
        console.log(`   POST /api/keys/:key/extend    - 延期密钥`);
        console.log(`   DELETE /api/keys/:key         - 删除密钥`);
        console.log(`   GET  /api/keys/stats/summary  - 获取统计信息`);
        console.log(`   GET  /api/sessions/active     - 获取活跃会话`);
        console.log(`   POST /api/keys/cleanup        - 清理过期密钥`);
        console.log(`⏰ 启动时间: ${new Date().toLocaleString()}`);
    });
}

startServer().catch(console.error);