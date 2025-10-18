const axios = require('axios');

module.exports = async (req, res) => {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    const limit = req.query.limit || 200;
    
    console.log(`[taiwan-pk10-latest] 请求阿里云API，limit=${limit}`);
    
    // 调用阿里云的台湾PK10 API
    const response = await axios.get(`http://47.242.214.89/api/latest`, {
      params: { limit },
      timeout: 10000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });

    console.log(`[taiwan-pk10-latest] 阿里云API响应成功，数据条数: ${response.data?.data?.length || 0}`);

    // 直接返回阿里云API的原始响应
    return res.status(200).json(response.data);

  } catch (error) {
    console.error('[taiwan-pk10-latest] 请求失败:', error.message);
    console.error('[taiwan-pk10-latest] 错误详情:', error.response?.data || error);
    
    return res.status(500).json({
      success: false,
      error: '获取台湾PK10数据失败',
      message: error.message,
      details: error.response?.data || null
    });
  }
};

