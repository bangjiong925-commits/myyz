// 台湾PK10最新数据API代理端点
// 代理47.242.214.89/api/latest接口

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
    const { limit = 200 } = req.query;
    
    console.log(`获取最新 ${limit} 条台湾PK10数据`);
    
    // 调用原始API获取数据
    const apiUrl = `http://47.242.214.89/api/latest?limit=${limit}`;
    
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 30000
    });
    
    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    
    console.log(`成功获取 ${data.data ? data.data.length : 0} 条数据`);
    
    // 直接返回原始数据格式
    return res.status(200).json(data);
    
  } catch (error) {
    console.error('获取台湾PK10最新数据失败:', error);
    
    return res.status(500).json({
      success: false,
      error: error.message,
      message: '获取台湾PK10最新数据失败'
    });
  }
}