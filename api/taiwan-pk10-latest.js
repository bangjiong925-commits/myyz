export default async function handler(req, res) {
  // 处理CORS预检请求
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { limit = 200 } = req.query;
    
    console.log(`代理台湾PK10数据请求，限制: ${limit}`);
    
    const response = await fetch(`http://47.242.214.89/api/latest?limit=${limit}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 15000 // 15秒超时
    });

    if (!response.ok) {
      throw new Error(`HTTP错误! 状态: ${response.status}`);
    }

    const contentType = response.headers.get('content-type') || '';
    let data;
    if (contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      console.error('台湾PK10最新数据代理收到非JSON响应:', text.slice(0, 200));
      return res.status(502).json({
        error: '获取数据失败',
        message: '远程服务返回异常响应',
        detail: text.slice(0, 200),
        timestamp: new Date().toISOString()
      });
    }
    
    console.log(`成功获取台湾PK10数据，记录数: ${data.length || 0}`);
    
    res.status(200).json(data);
  } catch (error) {
    console.error('台湾PK10 API代理错误:', error);
    res.status(500).json({ 
      error: '获取数据失败',
      message: error.message,
      timestamp: new Date().toISOString()
    });
  }
}
