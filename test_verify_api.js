// 测试新的原子性验证API逻辑（模拟KV存储）

// 模拟KV存储
class MockKV {
  constructor() {
    this.store = new Map();
    this.locks = new Map();
  }
  
  async get(key) {
    return this.store.get(key) || null;
  }
  
  async set(key, value, options = {}) {
    // 模拟nx选项（只在键不存在时设置）
    if (options.nx && this.store.has(key)) {
      return null; // 设置失败
    }
    
    this.store.set(key, value);
    
    // 模拟过期时间
    if (options.ex || options.px) {
      const ttl = options.ex ? options.ex * 1000 : options.px;
      setTimeout(() => {
        this.store.delete(key);
      }, ttl);
    }
    
    return 'OK';
  }
  
  async del(key) {
    return this.store.delete(key) ? 1 : 0;
  }
}

const mockKv = new MockKV();

// 模拟API逻辑
async function testVerifyAPI(nonce) {
  console.log(`Testing nonce: ${nonce}`);
  
  const lockKey = `lock:${nonce}`;
  const lockTimeout = 1000; // 1秒锁超时（测试用）
  const lockValue = Date.now().toString();
  
  try {
    // 尝试获取锁
    const lockAcquired = await mockKv.set(lockKey, lockValue, {
      nx: true,
      px: lockTimeout
    });
    
    if (!lockAcquired) {
      console.log('❌ 并发冲突，无法获取锁');
      return { success: false, message: '系统繁忙，请稍后重试' };
    }
    
    console.log('✅ 成功获取锁');
    
    // 在锁保护下检查密钥是否已存在
    const [usedNonce, keyRecord] = await Promise.all([
      mockKv.get(`usedNonce:${nonce}`),
      mockKv.get(`keyRecord:${nonce}`)
    ]);
    
    if (usedNonce || keyRecord) {
      console.log('❌ 密钥已被使用');
      return { success: false, message: '密钥已被使用' };
    }
    
    // 保存密钥记录
    const timestamp = Date.now();
    await Promise.all([
      mockKv.set(`usedNonce:${nonce}`, timestamp, { ex: 7 * 24 * 60 * 60 }), // 7天过期
      mockKv.set(`keyRecord:${nonce}`, {
        timestamp,
        userAgent: 'Test-Agent',
        ip: '127.0.0.1'
      }, { ex: 7 * 24 * 60 * 60 })
    ]);
    
    console.log('✅ 密钥验证成功并已标记');
    return { success: true, message: '密钥验证成功' };
    
  } catch (error) {
    console.error('❌ API错误:', error.message);
    return { success: false, message: '验证失败' };
  } finally {
    // 释放锁
    try {
      await mockKv.del(lockKey);
      console.log('🔓 锁已释放');
    } catch (error) {
      console.error('释放锁失败:', error.message);
    }
  }
}

// 测试用例
async function runTests() {
  console.log('=== 开始测试原子性验证API（模拟环境）===\n');
  
  const testNonce = `test_${Date.now()}`;
  
  // 测试1: 首次验证应该成功
  console.log('测试1: 首次验证');
  const result1 = await testVerifyAPI(testNonce);
  console.log('结果:', result1);
  console.log();
  
  // 测试2: 重复验证应该失败
  console.log('测试2: 重复验证');
  const result2 = await testVerifyAPI(testNonce);
  console.log('结果:', result2);
  console.log();
  
  // 测试3: 并发测试
  console.log('测试3: 并发验证测试');
  const concurrentNonce = `concurrent_${Date.now()}`;
  const promises = [];
  for (let i = 0; i < 3; i++) {
    promises.push(testVerifyAPI(concurrentNonce));
  }
  
  const results = await Promise.all(promises);
  results.forEach((result, index) => {
    console.log(`并发请求${index + 1}:`, result);
  });
  
  // 测试4: 验证锁机制
  console.log('\n测试4: 锁机制验证');
  const lockTestNonce = `lock_test_${Date.now()}`;
  
  // 模拟获取锁但不释放的情况
  await mockKv.set(`lock:${lockTestNonce}`, 'test_lock', { nx: true, px: 500 });
  console.log('已设置测试锁');
  
  const lockTestResult = await testVerifyAPI(lockTestNonce);
  console.log('锁冲突测试结果:', lockTestResult);
  
  // 等待锁过期后重试
  console.log('等待锁过期...');
  await new Promise(resolve => setTimeout(resolve, 600));
  
  const retryResult = await testVerifyAPI(lockTestNonce);
  console.log('锁过期后重试结果:', retryResult);
  
  console.log('\n=== 测试完成 ===');
  
  // 显示存储状态
  console.log('\n当前存储状态:');
  for (const [key, value] of mockKv.store.entries()) {
    console.log(`  ${key}: ${JSON.stringify(value)}`);
  }
}

// 运行测试
if (require.main === module) {
  runTests().catch(console.error);
}

module.exports = { testVerifyAPI, MockKV };