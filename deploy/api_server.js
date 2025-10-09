#!/usr/bin/env node
/**
 * 台湾PK10 API服务器
 * 提供数据库接口和实时数据服务
 */

const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件配置
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '..')));

// 数据库配置
const DB_PATH = path.join(__dirname, '..', 'data', 'taiwan_pk10.db');

// 确保数据目录存在
const dataDir = path.dirname(DB_PATH);
if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
}

// 数据库连接
let db = new sqlite3.Database(DB_PATH, (err) => {
    if (err) {
        console.error('❌ 数据库连接失败:', err.message);
    } else {
        console.log('✅ 数据库连接成功');
        initDatabase();
    }
});

// 初始化数据库表
function initDatabase() {
    const createTableSQL = `
        CREATE TABLE IF NOT EXISTS taiwan_pk10_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period VARCHAR(20) UNIQUE NOT NULL,
            numbers TEXT NOT NULL,
            draw_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `;
    
    db.run(createTableSQL, (err) => {
        if (err) {
            console.error('❌ 创建表失败:', err.message);
        } else {
            console.log('✅ 数据表初始化完成');
        }
    });
    
    // 创建索引
    db.run('CREATE INDEX IF NOT EXISTS idx_period ON taiwan_pk10_data(period)');
    db.run('CREATE INDEX IF NOT EXISTS idx_draw_time ON taiwan_pk10_data(draw_time)');
}

// API路由

// 获取最新数据
app.get('/api/latest', (req, res) => {
    const limit = parseInt(req.query.limit) || 100;
    const sql = `
        SELECT period, numbers, draw_time, created_at
        FROM taiwan_pk10_data
        ORDER BY period DESC
        LIMIT ?
    `;
    
    db.all(sql, [limit], (err, rows) => {
        if (err) {
            console.error('❌ 查询失败:', err.message);
            res.status(500).json({ error: '查询失败' });
        } else {
            res.json({
                success: true,
                data: rows,
                count: rows.length
            });
        }
    });
});

// 根据期号获取数据
app.get('/api/period/:period', (req, res) => {
    const period = req.params.period;
    const sql = `
        SELECT period, numbers, draw_time, created_at
        FROM taiwan_pk10_data
        WHERE period = ?
    `;
    
    db.get(sql, [period], (err, row) => {
        if (err) {
            console.error('❌ 查询失败:', err.message);
            res.status(500).json({ error: '查询失败' });
        } else if (row) {
            res.json({
                success: true,
                data: row
            });
        } else {
            res.status(404).json({
                success: false,
                error: '未找到数据'
            });
        }
    });
});

// 添加新数据
app.post('/api/data', (req, res) => {
    const { period, numbers, draw_time } = req.body;
    
    if (!period || !numbers) {
        return res.status(400).json({
            success: false,
            error: '期号和号码不能为空'
        });
    }
    
    const sql = `
        INSERT OR REPLACE INTO taiwan_pk10_data (period, numbers, draw_time)
        VALUES (?, ?, ?)
    `;
    
    const drawTime = draw_time || new Date().toISOString();
    
    db.run(sql, [period, numbers, drawTime], function(err) {
        if (err) {
            console.error('❌ 插入失败:', err.message);
            res.status(500).json({
                success: false,
                error: '插入失败'
            });
        } else {
            res.json({
                success: true,
                message: '数据添加成功',
                id: this.lastID
            });
        }
    });
});

// 获取数据统计
app.get('/api/stats', (req, res) => {
    const sql = `
        SELECT 
            COUNT(*) as total_count,
            MAX(period) as latest_period,
            MIN(period) as earliest_period,
            MAX(created_at) as last_update
        FROM taiwan_pk10_data
    `;
    
    db.get(sql, [], (err, row) => {
        if (err) {
            console.error('❌ 统计查询失败:', err.message);
            res.status(500).json({ error: '统计查询失败' });
        } else {
            res.json({
                success: true,
                stats: row
            });
        }
    });
});

// 删除旧数据
app.delete('/api/cleanup', (req, res) => {
    const days = parseInt(req.query.days) || 30;
    const sql = `
        DELETE FROM taiwan_pk10_data
        WHERE created_at < datetime('now', '-${days} days')
    `;
    
    db.run(sql, function(err) {
        if (err) {
            console.error('❌ 清理失败:', err.message);
            res.status(500).json({
                success: false,
                error: '清理失败'
            });
        } else {
            res.json({
                success: true,
                message: `清理完成，删除了 ${this.changes} 条记录`
            });
        }
    });
});

// 数据备份
app.get('/api/backup', (req, res) => {
    const sql = `
        SELECT period, numbers, draw_time, created_at
        FROM taiwan_pk10_data
        ORDER BY period DESC
    `;
    
    db.all(sql, [], (err, rows) => {
        if (err) {
            console.error('❌ 备份查询失败:', err.message);
            res.status(500).json({ error: '备份查询失败' });
        } else {
            const filename = `backup_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
            res.setHeader('Content-Disposition', `attachment; filename=${filename}`);
            res.setHeader('Content-Type', 'application/json');
            res.json({
                backup_time: new Date().toISOString(),
                total_records: rows.length,
                data: rows
            });
        }
    });
});

// 健康检查
app.get('/api/health', (req, res) => {
    res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        database: 'connected'
    });
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
app.listen(PORT, () => {
    console.log('🚀 API服务器启动成功');
    console.log(`📍 服务地址: http://localhost:${PORT}`);
    console.log('📋 可用接口:');
    console.log('  GET  /api/latest        - 获取最新数据');
    console.log('  GET  /api/period/:id    - 根据期号获取数据');
    console.log('  POST /api/data          - 添加新数据');
    console.log('  GET  /api/stats         - 获取统计信息');
    console.log('  GET  /api/backup        - 数据备份');
    console.log('  GET  /api/health        - 健康检查');
});

// 优雅关闭
process.on('SIGINT', () => {
    console.log('\n🛑 正在关闭API服务器...');
    db.close((err) => {
        if (err) {
            console.error('❌ 数据库关闭失败:', err.message);
        } else {
            console.log('✅ 数据库连接已关闭');
        }
        process.exit(0);
    });
});

module.exports = app;