// 简单的测试API，确认Vercel Serverless Function能正常工作
module.exports = async (req, res) => {
    return res.status(200).json({
        success: true,
        message: 'Vercel Serverless Function 正常工作',
        timestamp: new Date().toISOString(),
        method: req.method,
        query: req.query
    });
};

