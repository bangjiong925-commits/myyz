// Vercel Serverless Function - 密钥验证API代理
// 将验证请求转发到阿里云服务器

export default async function handler(req, res) {
  // 只允许POST请求
  if (req.method !== 'POST') {
    return res.status(405).json({ 
      success: false, 
      error: 'Method not allowed' 
    });
  }

  try {
    // 转发请求到阿里云服务器
    const response = await fetch('http://47.242.214.89/api/keys/validate-key', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(req.body)
    });

    const contentType = response.headers.get('content-type') || '';
    let data;
    if (contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      console.error('密钥验证代理收到非JSON响应:', text.slice(0, 200));
      return res.status(502).json({
        success: false,
        valid: false,
        error: '验证请求失败',
        message: '远程服务返回异常响应',
        detail: text.slice(0, 200)
      });
    }
    
    return res.status(response.ok ? 200 : response.status).json(data);
  } catch (error) {
    console.error('密钥验证代理错误:', error);
    return res.status(500).json({ 
      success: false, 
      valid: false,
      error: '验证请求失败',
      message: error.message
    });
  }
}
