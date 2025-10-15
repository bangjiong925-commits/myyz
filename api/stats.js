// Vercel Serverless Function - 统计API代理
// 将统计请求转发到阿里云服务器

export default async function handler(req, res) {
  // 只允许GET请求
  if (req.method !== 'GET') {
    return res.status(405).json({ 
      success: false, 
      error: 'Method not allowed' 
    });
  }

  try {
    // 转发请求到阿里云服务器
    const response = await fetch('http://47.242.214.89/api/keys/stats/summary', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();
    
    return res.status(response.ok ? 200 : response.status).json(data);
  } catch (error) {
    console.error('统计API代理错误:', error);
    return res.status(500).json({ 
      success: false, 
      error: '获取统计数据失败',
      message: error.message
    });
  }
}
