// Vercel API代理 - 转发密钥使用检查到阿里云服务器
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  try {
    const response = await fetch('http://47.242.214.89/api/sessions/check-usage', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
      timeout: 10000,
    });

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const data = await response.json();
      return res.status(response.status).json(data);
    } else {
      const text = await response.text();
      return res.status(502).json({ 
        error: '检查服务暂时不可用',
        details: '远程服务返回格式错误'
      });
    }
  } catch (error) {
    console.error('密钥检查代理错误:', error);
    return res.status(500).json({ 
      error: '检查服务暂时不可用',
      message: error.message 
    });
  }
}
