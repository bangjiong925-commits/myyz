/**
 * Vercel Serverless Function - 台湾PK10历史数据代理
 * 代理请求到阿里云服务器，避免CORS和Mixed Content问题
 */

const axios = require('axios');

module.exports = async (req, res) => {
    // 只允许 GET 请求
    if (req.method !== 'GET') {
        return res.status(405).json({ 
            success: false, 
            error: '只支持GET请求' 
        });
    }

    try {
        // 获取日期参数（可选，因为阿里云API是200期循环，不支持日期过滤）
        const { date } = req.query;

        // 阿里云API地址 - 获取最新200条数据（循环数据）
        const aliyunUrl = 'http://47.242.214.89/api/latest?limit=200';

        console.log(`代理请求: ${aliyunUrl}`);
        if (date) {
            console.log(`前端请求日期: ${date} (阿里云API不支持日期过滤，返回最新200期)`);
        }

        // 使用axios代理请求到阿里云
        const response = await axios.get(aliyunUrl, {
            timeout: 10000,
            headers: {
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });

        const aliyunResponse = response.data;
        console.log(`阿里云API返回: success=${aliyunResponse.success}, count=${aliyunResponse.count}`);

        if (!aliyunResponse.success) {
            return res.status(500).json({ 
                success: false, 
                error: aliyunResponse.message || '阿里云API返回失败'
            });
        }

        // 转换阿里云数据格式到前端期望的格式
        const aliyunData = aliyunResponse.data || [];
        
        const transformedData = aliyunData.map(item => ({
            period: item.expect,           // expect -> period
            numbers: item.opencode,        // opencode -> numbers
            timestamp: item.opentime,      // opentime -> timestamp
            time: item.opentime           // 兼容字段
        }));

        console.log(`数据转换完成: ${transformedData.length} 条`);

        // 返回转换后的数据给前端
        return res.status(200).json({
            success: true,
            data: transformedData,
            count: transformedData.length,
            message: '成功获取最新200期数据（循环）'
        });

    } catch (error) {
        console.error('代理请求失败:', error.message);
        return res.status(500).json({ 
            success: false, 
            error: '连接阿里云服务器失败',
            details: error.message 
        });
    }
};

