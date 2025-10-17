// Vercel Serverless Function - 管理API代理（需要管理员密钥）
// 将管理请求转发到阿里云服务器

export default async function handler(req, res) {
  try {
    // 从请求头或查询参数获取管理员密钥
    const adminKey = req.headers['x-admin-key'] || req.query.adminKey;
    
    // 构建转发URL
    let url = 'http://47.242.214.89/api/admin/keys';
    
    // 添加查询参数
    if (req.query && Object.keys(req.query).length > 0) {
      const params = new URLSearchParams();
      for (const [key, value] of Object.entries(req.query)) {
        if (key !== 'adminKey') { // 不转发adminKey参数
          params.append(key, value);
        }
      }
      const queryString = params.toString();
      if (queryString) {
        url += '?' + queryString;
      }
    }
    
    // 构建请求选项
    const options = {
      method: req.method,
      headers: {
        'Content-Type': 'application/json'
      }
    };
    
    // 转发管理员密钥
    if (adminKey) {
      options.headers['X-Admin-Key'] = adminKey;
    }
    
    // POST/PUT 请求需要传递body
    if (['POST', 'PUT', 'PATCH'].includes(req.method) && req.body) {
      options.body = JSON.stringify(req.body);
    }
    
    // 转发请求到阿里云
    const response = await fetch(url, options);
    const data = await response.json();
    
    // 返回响应（保持原始状态码）
    return res.status(response.status).json(data);
    
  } catch (error) {
    console.error('管理API代理错误:', error);
    return res.status(500).json({ 
      success: false, 
      error: '管理请求失败',
      message: error.message
    });
  }
}







