// Vercel API代理 - 转发密钥验证请求到阿里云服务器
export default async function handler(req, res) {
  // CORS headers
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
    // 转发请求到阿里云密钥管理服务器
    const response = await fetch('http://47.242.214.89:3002/api/keys/validate-key', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
    });

    const data = await response.json();
    return res.status(response.status).json(data);
  } catch (error) {
    console.error('密钥验证代理错误:', error);
    return res.status(500).json({ 
      success: false, 
      error: '验证服务暂时不可用',
      message: error.message 
    });
  }
}

