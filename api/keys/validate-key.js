export default async function handler(req, res) {
  // 处理CORS预检请求
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('代理密钥验证请求到阿里云服务器...');
    
    // 代理到阿里云服务器
    const response = await fetch('http://47.242.214.89/keys-api/keys/validate-key', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Vercel-Proxy/1.0'
      },
      body: JSON.stringify(req.body),
      timeout: 10000 // 10秒超时
    });

    const data = await response.json();
    
    console.log('密钥验证响应:', {
      success: data.success,
      valid: data.valid,
      reason: data.reason
    });
    
    res.status(response.status).json(data);
  } catch (error) {
    console.error('API代理错误:', error);
    res.status(500).json({ 
      success: false,
      valid: false,
      reason: '服务器连接失败',
      error: error.message 
    });
  }
}
