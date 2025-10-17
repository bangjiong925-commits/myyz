// Vercel API代理 - 转发密钥验证请求到阿里云服务器
// 使用http模块支持HTTP请求
import http from 'http';

function httpPost(url, data) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const postData = JSON.stringify(data);
    
    const options = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || 80,
      path: parsedUrl.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData),
      },
      timeout: 10000,
    };

    const req = http.request(options, (res) => {
      let responseData = '';
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      res.on('end', () => {
        try {
          resolve({
            status: res.statusCode,
            data: JSON.parse(responseData),
            ok: res.statusCode >= 200 && res.statusCode < 300,
          });
        } catch (err) {
          resolve({
            status: res.statusCode,
            data: responseData,
            ok: false,
          });
        }
      });
    });

    req.on('error', (err) => {
      reject(err);
    });

    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    req.write(postData);
    req.end();
  });
}

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
    console.log('[Vercel代理] 转发密钥验证请求:', req.body);
    
    const response = await httpPost('http://47.242.214.89/api/keys/validate-key', req.body);
    
    console.log('[Vercel代理] 阿里云响应状态:', response.status);
    
    if (typeof response.data === 'object') {
      return res.status(response.status).json(response.data);
    } else {
      console.error('[Vercel代理] 阿里云返回非JSON:', response.data.slice(0, 200));
      return res.status(502).json({ 
        success: false, 
        error: '密钥验证服务返回格式错误',
        details: response.data.slice(0, 100)
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
