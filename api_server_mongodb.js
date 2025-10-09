#!/usr/bin/env node
/**
 * 台湾PK10 API服务器 - MongoDB版本
 * 提供MongoDB数据库接口和实时数据服务
 */

import express from 'express';
import cors from 'cors';
import { MongoClient } from 'mongodb';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import dotenv from 'dotenv';

// ES模块中获取__dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 加载环境变量
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件配置
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '.')));

// MongoDB配置
const MONGODB_URI = process.env.MONGODB_URI;
const DB_NAME = process.env.MONGODB_DB_NAME || 'taiwan_pk10';
const COLLECTION_NAME = 'pk10_results';

if (!MONGODB_URI) {
    console.error('❌ MongoDB连接字符串未配置，请设置MONGODB_URI环境变量');
    process.exit(1);
}

let client;
let db;
let collection;

// 连接MongoDB
async function connectMongoDB() {
    try {
        client = new MongoClient(MONGODB_URI, {
            serverSelectionTimeoutMS: 5000,
            connectTimeoutMS: 10000,
            socketTimeoutMS: 10000,
        });
        
        await client.connect();
        await client.db('admin').command({ ping: 1 });
        
        db = client.db(DB_NAME);
        collection = db.collection(COLLECTION_NAME);
        
        // 创建索引
        await createIndexes();
        
        console.log('✅ MongoDB连接成功');
        console.log(`📍 数据库: ${DB_NAME}`);
        console.log(`📋 集合: ${COLLECTION_NAME}`);
        
    } catch (error) {
        console.error('❌ MongoDB连接失败:', error.message);
        process.exit(1);
    }
}

// 创建数据库索引
async function createIndexes() {
    try {
        // 为期号创建唯一索引
        await collection.createIndex({ issue: 1 }, { unique: true });
        
        // 为时间戳创建索引
        await collection.createIndex({ timestamp: 1 });
        
        // 为日期创建索引
        await collection.createIndex({ date: 1 });
        
        console.log('✅ 数据库索引创建完成');
        
    } catch (error) {
        console.warn('⚠️ 创建索引时出现警告:', error.message);
    }
}

// 工具函数：格式化数据
function formatData(doc) {
    if (!doc) return null;
    
    return {
        issue: doc.issue,
        numbers: doc.numbers,
        date: doc.date,
        time: doc.time,
        timestamp: doc.timestamp,
        created_at: doc.created_at
    };
}

// API路由

// 获取最新数据
app.get('/api/latest', async (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 100;
        
        const docs = await collection
            .find({})
            .sort({ timestamp: -1 })
            .limit(limit)
            .toArray();
        
        const data = docs.map(formatData);
        
        res.json({
            success: true,
            data: data,
            count: data.length
        });
        
    } catch (error) {
        console.error('❌ 查询失败:', error.message);
        res.status(500).json({ 
            success: false,
            error: '查询失败' 
        });
    }
});

// 根据期号获取数据
app.get('/api/period/:issue', async (req, res) => {
    try {
        const issue = req.params.issue;
        
        const doc = await collection.findOne({ issue: issue });
        
        if (doc) {
            res.json({
                success: true,
                data: formatData(doc)
            });
        } else {
            res.status(404).json({
                success: false,
                error: '未找到数据'
            });
        }
        
    } catch (error) {
        console.error('❌ 查询失败:', error.message);
        res.status(500).json({ 
            success: false,
            error: '查询失败' 
        });
    }
});

// 根据日期范围获取数据
app.get('/api/date-range', async (req, res) => {
    try {
        const { start_date, end_date } = req.query;
        
        if (!start_date || !end_date) {
            return res.status(400).json({
                success: false,
                error: '请提供开始日期和结束日期'
            });
        }
        
        const docs = await collection
            .find({
                date: {
                    $gte: start_date,
                    $lte: end_date
                }
            })
            .sort({ timestamp: -1 })
            .toArray();
        
        const data = docs.map(formatData);
        
        res.json({
            success: true,
            data: data,
            count: data.length
        });
        
    } catch (error) {
        console.error('❌ 查询失败:', error.message);
        res.status(500).json({ 
            success: false,
            error: '查询失败' 
        });
    }
});

// 添加新数据
app.post('/api/data', async (req, res) => {
    try {
        const { issue, numbers, date, time } = req.body;
        
        if (!issue || !numbers) {
            return res.status(400).json({
                success: false,
                error: '期号和号码不能为空'
            });
        }
        
        const now = new Date();
        const data = {
            issue: issue,
            numbers: numbers,
            date: date || now.toISOString().split('T')[0],
            time: time || now.toTimeString().split(' ')[0],
            timestamp: now,
            created_at: now
        };
        
        // 使用upsert操作（如果存在则更新，不存在则插入）
        const result = await collection.replaceOne(
            { issue: issue },
            data,
            { upsert: true }
        );
        
        res.json({
            success: true,
            message: result.upsertedCount > 0 ? '数据添加成功' : '数据更新成功',
            issue: issue
        });
        
    } catch (error) {
        console.error('❌ 插入失败:', error.message);
        res.status(500).json({
            success: false,
            error: '插入失败'
        });
    }
});

// 批量添加数据
app.post('/api/batch', async (req, res) => {
    try {
        const { data_list } = req.body;
        
        if (!Array.isArray(data_list) || data_list.length === 0) {
            return res.status(400).json({
                success: false,
                error: '请提供有效的数据列表'
            });
        }
        
        const now = new Date();
        const operations = data_list.map(item => ({
            replaceOne: {
                filter: { issue: item.issue },
                replacement: {
                    issue: item.issue,
                    numbers: item.numbers,
                    date: item.date || now.toISOString().split('T')[0],
                    time: item.time || now.toTimeString().split(' ')[0],
                    timestamp: item.timestamp ? new Date(item.timestamp) : now,
                    created_at: now
                },
                upsert: true
            }
        }));
        
        const result = await collection.bulkWrite(operations);
        
        res.json({
            success: true,
            message: '批量操作完成',
            inserted: result.upsertedCount,
            modified: result.modifiedCount
        });
        
    } catch (error) {
        console.error('❌ 批量插入失败:', error.message);
        res.status(500).json({
            success: false,
            error: '批量插入失败'
        });
    }
});

// 获取数据统计
app.get('/api/stats', async (req, res) => {
    try {
        const totalCount = await collection.countDocuments();
        
        const latestDoc = await collection
            .findOne({}, { sort: { timestamp: -1 } });
        
        const oldestDoc = await collection
            .findOne({}, { sort: { timestamp: 1 } });
        
        const stats = {
            total_count: totalCount,
            latest_issue: latestDoc ? latestDoc.issue : null,
            earliest_issue: oldestDoc ? oldestDoc.issue : null,
            last_update: latestDoc ? latestDoc.created_at : null,
            database_name: DB_NAME,
            collection_name: COLLECTION_NAME
        };
        
        res.json({
            success: true,
            stats: stats
        });
        
    } catch (error) {
        console.error('❌ 统计查询失败:', error.message);
        res.status(500).json({ 
            success: false,
            error: '统计查询失败' 
        });
    }
});

// 删除旧数据
app.delete('/api/cleanup', async (req, res) => {
    try {
        const days = parseInt(req.query.days) || 30;
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - days);
        
        const result = await collection.deleteMany({
            created_at: { $lt: cutoffDate }
        });
        
        res.json({
            success: true,
            message: `清理完成，删除了 ${result.deletedCount} 条记录`
        });
        
    } catch (error) {
        console.error('❌ 清理失败:', error.message);
        res.status(500).json({
            success: false,
            error: '清理失败'
        });
    }
});

// 数据备份
app.get('/api/backup', async (req, res) => {
    try {
        const docs = await collection
            .find({})
            .sort({ timestamp: -1 })
            .toArray();
        
        const data = docs.map(formatData);
        
        const filename = `backup_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        res.setHeader('Content-Disposition', `attachment; filename=${filename}`);
        res.setHeader('Content-Type', 'application/json');
        
        res.json({
            backup_time: new Date().toISOString(),
            total_records: data.length,
            database: DB_NAME,
            collection: COLLECTION_NAME,
            data: data
        });
        
    } catch (error) {
        console.error('❌ 备份查询失败:', error.message);
        res.status(500).json({ 
            success: false,
            error: '备份查询失败' 
        });
    }
});

// 恢复数据
app.post('/api/restore', async (req, res) => {
    try {
        const { data } = req.body;
        
        if (!Array.isArray(data) || data.length === 0) {
            return res.status(400).json({
                success: false,
                error: '请提供有效的备份数据'
            });
        }
        
        const now = new Date();
        const operations = data.map(item => ({
            replaceOne: {
                filter: { issue: item.issue },
                replacement: {
                    ...item,
                    timestamp: item.timestamp ? new Date(item.timestamp) : now,
                    created_at: item.created_at ? new Date(item.created_at) : now
                },
                upsert: true
            }
        }));
        
        const result = await collection.bulkWrite(operations);
        
        res.json({
            success: true,
            message: '数据恢复完成',
            inserted: result.upsertedCount,
            modified: result.modifiedCount
        });
        
    } catch (error) {
        console.error('❌ 数据恢复失败:', error.message);
        res.status(500).json({
            success: false,
            error: '数据恢复失败'
        });
    }
});

// 健康检查
app.get('/api/health', async (req, res) => {
    try {
        // 测试数据库连接
        await client.db('admin').command({ ping: 1 });
        
        res.json({
            status: 'ok',
            timestamp: new Date().toISOString(),
            database: 'connected',
            mongodb_uri: MONGODB_URI.replace(/\/\/([^:]+):([^@]+)@/, '//***:***@'), // 隐藏密码
            database_name: DB_NAME,
            collection_name: COLLECTION_NAME
        });
        
    } catch (error) {
        res.status(500).json({
            status: 'error',
            timestamp: new Date().toISOString(),
            database: 'disconnected',
            error: error.message
        });
    }
});

// 错误处理中间件
app.use((err, req, res, next) => {
    console.error('❌ 服务器错误:', err.stack);
    res.status(500).json({
        success: false,
        error: '服务器内部错误'
    });
});

// 404处理
app.use((req, res) => {
    res.status(404).json({
        success: false,
        error: '接口不存在'
    });
});

// 启动服务器
async function startServer() {
    try {
        // 先连接数据库
        await connectMongoDB();
        
        // 启动HTTP服务器
        app.listen(PORT, () => {
            console.log('🚀 API服务器启动成功');
            console.log(`📍 服务地址: http://localhost:${PORT}`);
            console.log('📋 可用接口:');
            console.log('  GET  /api/latest           - 获取最新数据');
            console.log('  GET  /api/period/:issue    - 根据期号获取数据');
            console.log('  GET  /api/date-range       - 根据日期范围获取数据');
            console.log('  POST /api/data             - 添加新数据');
            console.log('  POST /api/batch            - 批量添加数据');
            console.log('  GET  /api/stats            - 获取统计信息');
            console.log('  DELETE /api/cleanup        - 清理旧数据');
            console.log('  GET  /api/backup           - 数据备份');
            console.log('  POST /api/restore          - 数据恢复');
            console.log('  GET  /api/health           - 健康检查');
        });
        
    } catch (error) {
        console.error('❌ 服务器启动失败:', error.message);
        process.exit(1);
    }
}

// 优雅关闭
process.on('SIGINT', async () => {
    console.log('\n🛑 正在关闭API服务器...');
    try {
        if (client) {
            await client.close();
            console.log('✅ MongoDB连接已关闭');
        }
        process.exit(0);
    } catch (error) {
        console.error('❌ 关闭时出错:', error.message);
        process.exit(1);
    }
});

process.on('SIGTERM', async () => {
    console.log('\n🛑 收到终止信号，正在关闭服务器...');
    try {
        if (client) {
            await client.close();
            console.log('✅ MongoDB连接已关闭');
        }
        process.exit(0);
    } catch (error) {
        console.error('❌ 关闭时出错:', error.message);
        process.exit(1);
    }
});

// 启动服务器
startServer();