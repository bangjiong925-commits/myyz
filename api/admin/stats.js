// Vercel Serverless Function - 管理统计API代理（需要管理员密钥）

export default async function handler(req, res) {
  // 只允许GET请求
  if (req.method !== 'GET') {
    return res.status(405).json({ 
      success: false, 
      error: 'Method not allowed' 
    });
  }

  try {
    // 从请求头或查询参数获取管理员密钥
    const adminKey = req.headers['x-admin-key'] || req.query.adminKey;
    
    // 构建请求头
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (adminKey) {
      headers['X-Admin-Key'] = adminKey;
    }
    
    // 转发请求到阿里云
    const response = await fetch('http://47.242.214.89/api/admin/stats', {
      method: 'GET',
      headers
    });

    const data = await response.json();
    
    return res.status(response.status).json(data);
    
  } catch (error) {
    console.error('统计API代理错误:', error);
    return res.status(500).json({ 
      success: false, 
      error: '获取统计数据失败',
      message: error.message
    });
  }
}







