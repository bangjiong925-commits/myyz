const express = require('express');
const cors = require('cors');
const axios = require('axios');
const app = express();
const PORT = 3001;

// 启用CORS
app.use(cors());
app.use(express.json());

// 代理API请求
app.get('/api/taiwan-pk10-proxy', async (req, res) => {
    try {
        console.log('收到代理请求');
        
        // 目标API地址
        const targetUrl = 'https://api.api68.com/pks/getLotteryPksInfo.do?lotCode=10057';
        
        // 设置请求头，模拟浏览器请求
        const headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://api.api68.com/',
            'Origin': 'https://api.api68.com'
        };
        
        console.log('正在请求:', targetUrl);
        
        // 发送请求到目标API
        const response = await axios.get(targetUrl, {
            headers: headers,
            timeout: 10000
        });
        
        console.log('API响应状态:', response.status);
        console.log('API响应数据:', JSON.stringify(response.data, null, 2));
        
        // 返回数据
        res.json({
            success: true,
            data: response.data
        });
        
    } catch (error) {
        console.error('代理请求失败:', error.message);
        
        if (error.response) {
            console.error('错误状态码:', error.response.status);
            console.error('错误响应:', error.response.data);
            
            res.status(error.response.status).json({
                success: false,
                error: `API返回错误: ${error.response.status}`,
                details: error.response.data
            });
        } else if (error.request) {
            console.error('网络请求失败:', error.request);
            res.status(500).json({
                success: false,
                error: '网络请求失败',
                details: error.message
            });
        } else {
            console.error('其他错误:', error.message);
            res.status(500).json({
                success: false,
                error: '服务器内部错误',
                details: error.message
            });
        }
    }
});

// 健康检查端点
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
    console.log(`代理服务器运行在 http://localhost:${PORT}`);
    console.log(`代理API端点: http://localhost:${PORT}/api/taiwan-pk10-proxy`);
});

// 优雅关闭
process.on('SIGINT', () => {
    console.log('\n正在关闭代理服务器...');
    process.exit(0);
});