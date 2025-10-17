// Vercel API代理 - 使用axios转发到阿里云
import axios from 'axios';

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
    console.log('[Vercel代理] 转发请求:', req.body);
    
    const response = await axios.post(
      'http://47.242.214.89/api/keys/validate-key',
      req.body,
      {
        headers: { 'Content-Type': 'application/json' },
        timeout: 10000,
      }
    );
    
    console.log('[Vercel代理] 阿里云响应:', response.data);
    return res.status(response.status).json(response.data);
  } catch (error) {
    console.error('[Vercel代理] 错误:', error.message);
    
    if (error.response) {
      return res.status(error.response.status).json(error.response.data);
    }
    
    return res.status(500).json({ 
      success: false, 
      error: '无法连接到密钥验证服务',
      message: error.message 
    });
  }
}
