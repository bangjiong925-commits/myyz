// Vercel API代理 - 转发密钥验证并登记到阿里云服务器
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
    const response = await fetch('http://47.242.214.89/api/keys/validate-and-register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
    });

    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      const data = await response.json();
      return res.status(response.status).json(data);
    } else {
      const text = await response.text();
      return res.status(502).json({ 
        success: false,
        error: '登记服务返回格式错误',
        details: text.slice(0, 100)
      });
    }
  } catch (error) {
    return res.status(500).json({ 
      success: false,
      error: '无法连接到登记服务',
      message: error.message 
    });
  }
}
