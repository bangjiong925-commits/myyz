/**
 * Vercel Serverless Function - 台湾PK10历史数据代理
 * 代理请求到阿里云服务器，避免CORS和Mixed Content问题
 */

const http = require('http');

module.exports = async (req, res) => {
    // 只允许 GET 请求
    if (req.method !== 'GET') {
        return res.status(405).json({ 
            success: false, 
            error: '只支持GET请求' 
        });
    }

    // 获取日期参数
    const { date } = req.query;
    
    if (!date) {
        return res.status(400).json({ 
            success: false, 
            error: '缺少date参数' 
        });
    }

    // 阿里云API地址
    const aliyunHost = '47.242.214.89';
    const aliyunPath = `/api/latest?date=${date}&limit=200`;

    console.log(`代理请求: http://${aliyunHost}${aliyunPath}`);

    // 代理请求到阿里云
    const options = {
        hostname: aliyunHost,
        port: 80,
        path: aliyunPath,
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        timeout: 10000
    };

    return new Promise((resolve) => {
        const proxyReq = http.request(options, (proxyRes) => {
            let data = '';

            proxyRes.on('data', (chunk) => {
                data += chunk;
            });

            proxyRes.on('end', () => {
                try {
                    // 解析阿里云返回的数据
                    const aliyunData = JSON.parse(data);
                    
                    console.log(`阿里云返回数据条数: ${Array.isArray(aliyunData) ? aliyunData.length : '非数组'}`);

                    // 返回数据给前端
                    res.status(200).json({
                        success: true,
                        data: aliyunData,
                        date: date,
                        count: Array.isArray(aliyunData) ? aliyunData.length : 0
                    });
                    resolve();
                } catch (error) {
                    console.error('解析阿里云响应失败:', error);
                    res.status(500).json({ 
                        success: false, 
                        error: '解析数据失败',
                        details: error.message 
                    });
                    resolve();
                }
            });
        });

        proxyReq.on('error', (error) => {
            console.error('代理请求失败:', error);
            res.status(500).json({ 
                success: false, 
                error: '连接阿里云服务器失败',
                details: error.message 
            });
            resolve();
        });

        proxyReq.on('timeout', () => {
            console.error('请求超时');
            proxyReq.destroy();
            res.status(504).json({ 
                success: false, 
                error: '请求超时' 
            });
            resolve();
        });

        proxyReq.end();
    });
};

