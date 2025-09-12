// 台湾PK10 API数据获取端点
// 使用API接口获取数据，替代爬虫方案

export default async function handler(req, res) {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, User-Agent');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

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
    
    const lotteryData = result.data;
    
    if (!lotteryData || lotteryData.length === 0) {
      throw new Error('没有获取到数据');
    }
    
    // 转换数据格式
    const formattedData = lotteryData.map(item => {
      const numbers = item.preDrawCode.split(',').map(num => parseInt(num));
      
      return {
        period: item.preDrawIssue.toString(),
        time: item.preDrawTime,
        numbers: numbers,
        numbersString: item.preDrawCode,
        sumFS: item.sumFS,
        sumBigSmall: item.sumBigSamll,
        sumSingleDouble: item.sumSingleDouble,
        firstDT: item.firstDT,
        secondDT: item.secondDT,
        thirdDT: item.thirdDT,
        fourthDT: item.fourthDT,
        fifthDT: item.fifthDT,
        groupCode: item.groupCode
      };
    });
    
    // 返回数据
    const responseData = {
      success: true,
      date: targetDate,
      count: formattedData.length,
      data: formattedData,
      timestamp: Date.now(),
      source: 'api.api68.com',
      type: 'taiwan-pk10'
    };
    
    console.log(`成功获取 ${targetDate} 的数据，共 ${formattedData.length} 条记录`);
    
    return res.status(200).json(responseData);
    
  } catch (error) {
    console.error('API数据获取失败:', error.message);
    
    // 返回错误信息
    return res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now(),
      type: 'taiwan-pk10'
    });
  }
}