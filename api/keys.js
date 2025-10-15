// Vercel Serverless Function - 密钥列表API代理
// 将请求转发到阿里云服务器

export default async function handler(req, res) {
  try {
    // 构建查询参数
    const queryParams = new URLSearchParams();
    if (req.query.limit) queryParams.append('limit', req.query.limit);
    if (req.query.page) queryParams.append('page', req.query.page);
    if (req.query.type) queryParams.append('type', req.query.type);
    if (req.query.status) queryParams.append('status', req.query.status);
    if (req.query.search) queryParams.append('search', req.query.search);
    
    const queryString = queryParams.toString();
    const url = `http://47.242.214.89/api/keys${queryString ? '?' + queryString : ''}`;
    
    // 根据请求方法转发
    const options = {
      method: req.method,
      headers: {
        'Content-Type': 'application/json'
      }
    };
    
    // POST请求需要传递body
    if (req.method === 'POST' && req.body) {
      options.body = JSON.stringify(req.body);
    }
    
    const response = await fetch(url, options);
    const data = await response.json();
    
    return res.status(response.ok ? 200 : response.status).json(data);
  } catch (error) {
    console.error('密钥API代理错误:', error);
    return res.status(500).json({ 
      success: false, 
      error: '请求失败',
      message: error.message
    });
  }
}
