// Vercel API - 创建密钥（临时管理接口）
import { MongoClient } from 'mongodb';

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://Vercel-Admin-myyz-d:OyFOhcDOC2M6hGxp@myyz-d.amcwwek.mongodb.net/?retryWrites=true&w=majority';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  try {
    const { key, expirationDays, description, database = 'key_management', collection = 'keys' } = req.body || {};
    
    if (!key) {
      return res.status(400).json({ error: '密钥不能为空' });
    }

    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    
    const db = client.db(database);
    const keysCollection = db.collection(collection);

    // 检查密钥是否已存在
    const existing = await keysCollection.findOne({ key });
    if (existing) {
      await client.close();
      return res.status(400).json({ error: '密钥已存在' });
    }

    // 创建密钥
    const now = new Date();
    const days = expirationDays || 30;
    const expiresAt = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);

    const keyDoc = {
      key,
      description: description || `Created via API at ${now.toISOString()}`,
      createdAt: now,
      expiresAt,
      isActive: true,
      usageCount: 0,
      lastUsed: null,
    };

    await keysCollection.insertOne(keyDoc);
    await client.close();

    return res.status(201).json({
      success: true,
      message: '密钥创建成功',
      key: keyDoc,
      database,
      collection,
    });
  } catch (err) {
    console.error('创建密钥错误:', err);
    return res.status(500).json({ error: '服务器内部错误', details: err.message });
  }
}

