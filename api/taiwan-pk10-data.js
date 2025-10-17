// 台湾PK10数据API端点
// 获取指定日期或最新的台湾PK10开奖数据

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
    const { date, latest } = req.query;
    
    let targetDate;
    
    if (latest === 'true') {
      // 获取最新数据（今天的数据）
      targetDate = new Date().toISOString().split('T')[0];
    } else if (date) {
      // 使用指定日期
      targetDate = date;
    } else {
      // 默认获取今天的数据
      targetDate = new Date().toISOString().split('T')[0];
    }
    
    console.log(`获取 ${targetDate} 的台湾PK10数据`);
    
    // 调用API获取数据
    const apiUrl = `https://api.api68.com/pks/getPksHistoryList.do?lotCode=10057&date=${targetDate}`;
    
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json'
      },
      timeout: 30000
    });
    
    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
    }
    
    const parseResponse = async (resp, context) => {
      const contentType = resp.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        return resp.json();
      }
      const text = await resp.text();
      throw new Error(`${context} 返回非JSON响应: ${text.slice(0, 200)}`);
    };

    const data = await parseResponse(response, '台湾PK10主数据接口');
    
    // 检查API响应
    if (data.errorCode !== 0) {
      throw new Error(`API返回错误: ${data.message}`);
    }
    
    const result = data.result;
    if (result.businessCode !== 0) {
      throw new Error(`业务逻辑错误: ${result.message}`);
    }
    
    let lotteryData = result.data;
    
    if (!lotteryData || lotteryData.length === 0) {
      // 如果当天没有数据，尝试获取前一天的数据
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      const yesterdayStr = yesterday.toISOString().split('T')[0];
      
      console.log(`${targetDate} 没有数据，尝试获取 ${yesterdayStr} 的数据`);
      
      const yesterdayUrl = `https://api.api68.com/pks/getPksHistoryList.do?lotCode=10057&date=${yesterdayStr}`;
      const yesterdayResponse = await fetch(yesterdayUrl, {
        method: 'GET',
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
          'Accept': 'application/json'
        },
        timeout: 30000
      });
      
      if (yesterdayResponse.ok) {
        const yesterdayData = await parseResponse(yesterdayResponse, '台湾PK10备用数据接口');
        if (yesterdayData.errorCode === 0 && yesterdayData.result.businessCode === 0 && yesterdayData.result.data.length > 0) {
          targetDate = yesterdayStr;
          lotteryData = yesterdayData.result.data;
        }
      }
      
      if (!lotteryData || lotteryData.length === 0) {
        throw new Error('没有获取到有效数据');
      }
    }
    
    // 转换数据格式
    const formattedData = lotteryData.map(item => {
      const numbers = item.preDrawCode.split(',').map(num => parseInt(num));
      
      return {
        issue: item.preDrawIssue.toString(),
        period: item.preDrawIssue.toString(),
        drawTime: item.preDrawTime,
        time: item.preDrawTime,
        numbers: numbers,
        numbersString: item.preDrawCode,
        // 统计信息
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
    
    // 按时间排序（最新的在前）
    formattedData.sort((a, b) => new Date(b.drawTime) - new Date(a.drawTime));
    
    // 构建响应数据
    const responseData = {
      success: true,
      date: targetDate,
      count: formattedData.length,
      data: formattedData,
      latest: formattedData[0] || null, // 最新一期数据
      timestamp: Date.now(),
      source: 'api.api68.com',
      type: 'taiwan-pk10'
    };
    
    console.log(`成功获取 ${targetDate} 的数据，共 ${formattedData.length} 条记录`);
    
    return res.status(200).json(responseData);
    
  } catch (error) {
    console.error('获取台湾PK10数据失败:', error.message);
    
    // 返回错误信息
    return res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now(),
      type: 'taiwan-pk10',
      data: []
    });
  }
}
