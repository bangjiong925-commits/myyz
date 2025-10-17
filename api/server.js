// 台湾PK10 API服务器
// 使用API接口获取数据，替代爬虫方案

import express from 'express';
import cors from 'cors';

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(cors());
app.use(express.json());

// 台湾PK10数据获取端点
app.get('/api/taiwan-pk10', async (req, res) => {
  try {
    // 获取查询参数
    const { date } = req.query;
    
    // 如果没有指定日期，使用今天的日期
    const targetDate = date || new Date().toISOString().split('T')[0];
    
    console.log(`获取 ${targetDate} 的数据`);
    
    // 调用API获取数据
    const apiUrl = `https://api.api68.com/pks/getPksHistoryList.do?lotCode=10057&date=${targetDate}`;
    
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
    });
    
    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // 检查API响应
    if (data.errorCode !== 0) {
      throw new Error(`API返回错误: ${data.message}`);
    }
    
    const result = data.result;
    if (result.businessCode !== 0) {
      throw new Error(`业务逻辑错误: ${result.message}`);
    }
    
    const historyList = result.data;
    if (!historyList || !Array.isArray(historyList)) {
      throw new Error('API返回的数据格式不正确');
    }
    
    console.log(`成功获取 ${historyList.length} 条记录`);
    
    // 转换数据格式
    const formattedData = historyList.map(item => {
      // 解析开奖号码
      const numbers = item.preDrawCode ? item.preDrawCode.split(',').map(num => parseInt(num)) : [];
      
      return {
        period: item.preDrawIssue,
        draw_time: item.preDrawTime,
        numbers: numbers,
        sum: numbers.reduce((a, b) => a + b, 0),
        big_small: numbers.reduce((a, b) => a + b, 0) >= 11 ? '大' : '小',
        odd_even: numbers.reduce((a, b) => a + b, 0) % 2 === 0 ? '双' : '单',
        dragon_tiger: numbers[0] > numbers[1] ? '龙' : numbers[0] < numbers[1] ? '虎' : '和'
      };
    });
    
    // 按期号排序（最新的在前）
    formattedData.sort((a, b) => parseInt(b.period) - parseInt(a.period));
    
    // 返回数据
    res.json({
      success: true,
      date: targetDate,
      count: formattedData.length,
      data: formattedData,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('获取数据失败:', error.message);
    
    // 返回错误信息
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'Taiwan PK10 API Server'
  });
});

// 根路径
app.get('/', (req, res) => {
  res.json({
    message: 'Taiwan PK10 API Server',
    endpoints: {
      '/api/taiwan-pk10': 'GET - 获取台湾PK10数据 (可选参数: date=YYYY-MM-DD)',
      '/health': 'GET - 健康检查'
    },
    timestamp: new Date().toISOString()
  });
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`台湾PK10 API服务器启动成功`);
  console.log(`服务器地址: http://localhost:${PORT}`);
  console.log(`API端点: http://localhost:${PORT}/api/taiwan-pk10`);
  console.log(`健康检查: http://localhost:${PORT}/health`);
});

// 优雅关闭
process.on('SIGTERM', () => {
  console.log('收到SIGTERM信号，正在关闭服务器...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('收到SIGINT信号，正在关闭服务器...');
  process.exit(0);
});