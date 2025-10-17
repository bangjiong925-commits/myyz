// Vercel API代理 - 使用axios转发到阿里云
const axios = require('axios');

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') {
    return res.status(405).json({ success: false, error: 'Method Not Allowed' });
  }

  try {
    console.log('[Vercel代理] 转发validate-and-register请求');
    
    const response = await axios.post(
      'http://47.242.214.89/api/keys/validate-and-register',
      req.body,
      { headers: { 'Content-Type': 'application/json' }, timeout: 10000 }
    );
    
    return res.status(response.status).json(response.data);
  } catch (error) {
    console.error('[Vercel代理] validate-and-register错误:', error.message);
    
    if (error.response) {
      return res.status(error.response.status).json(error.response.data);
    }
    return res.status(500).json({ 
      success: false,
      error: '无法连接到登记服务',
      message: error.message 
    });
  }
};
