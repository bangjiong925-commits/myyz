// Vercel API代理 - 转发密钥验证请求到阿里云服务器
// 通过Nginx 80端口的 /api/sessions 路由访问密钥管理服务
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
    // 通过Nginx的 /api/sessions 路由访问密钥管理服务（端口3002）
    const response = await fetch('http://47.242.214.89/api/sessions/validate-key', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
      timeout: 10000,
    });

    // 检查响应类型
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const data = await response.json();
      return res.status(response.status).json(data);
    } else {
      const text = await response.text();
      console.error('阿里云返回非JSON:', text.slice(0, 200));
      return res.status(502).json({ 
        success: false, 
        error: '密钥验证服务暂时不可用',
        details: '远程服务返回格式错误'
      });
    }
  } catch (error) {
    console.error('密钥验证代理错误:', error);
    return res.status(500).json({ 
      success: false, 
      error: '验证服务暂时不可用',
      message: error.message 
    });
  }
}
