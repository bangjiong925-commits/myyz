// Vercel Serverless Function - 心跳请求代理
// 将心跳请求转发到阿里云服务器

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
    const response = await fetch('http://47.242.214.89/api/keys/heartbeat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(req.body)
    });

    const data = await response.json();
    
    // 返回阿里云服务器的响应
    return res.status(response.ok ? 200 : response.status).json(data);
  } catch (error) {
    console.error('心跳代理错误:', error);
    return res.status(500).json({ 
      success: false, 
      error: '心跳请求失败' 
    });
  }
}



