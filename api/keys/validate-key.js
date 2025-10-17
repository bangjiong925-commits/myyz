// Vercel API代理 - 转发密钥验证请求到阿里云服务器
// 直接访问 http://47.242.214.89/api/keys/validate-key (Nginx会转发到3002端口)
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ success: false, error: 'Method Not Allowed' });
  }

  try {
    console.log('[Vercel代理] 转发密钥验证请求到阿里云:', req.body);
    
    const response = await fetch('http://47.242.214.89/api/keys/validate-key', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Forwarded-For': req.headers['x-forwarded-for'] || '',
        'User-Agent': req.headers['user-agent'] || 'Vercel-Proxy',
      },
      body: JSON.stringify(req.body),
    });

    const contentType = response.headers.get('content-type') || '';
    
    if (contentType.includes('application/json')) {
      const data = await response.json();
      console.log('[Vercel代理] 阿里云响应:', data);
      return res.status(response.status).json(data);
    } else {
      const text = await response.text();
      console.error('[Vercel代理] 阿里云返回非JSON:', text.slice(0, 200));
      return res.status(502).json({ 
        success: false, 
        error: '密钥验证服务返回格式错误',
        details: text.slice(0, 100)
      });
    }
  } catch (error) {
    console.error('[Vercel代理] 错误:', error);
    return res.status(500).json({ 
      success: false, 
      error: '无法连接到密钥验证服务',
      message: error.message 
    });
  }
}
