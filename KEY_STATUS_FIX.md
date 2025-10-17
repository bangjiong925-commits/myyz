# 密钥状态管理修复说明

## 问题
当前密钥状态管理有问题：
1. 新建密钥不会立即进入数据库
2. 第一次验证时直接设置 `usageCount: 1`
3. 用户期望：新建密钥时 `usageCount: 0`（未激活），第一次验证成功后 `usageCount: 1`（已激活）

## 修复方案

### 当前逻辑（错误）
```
创建密钥 → 不在数据库
第一次验证 → 插入数据库，usageCount=1
```

### 正确逻辑
```
创建密钥 → 插入数据库，status='inactive', usageCount=0, activatedAt=null
第一次验证 → 更新状态，status='active', usageCount=1, activatedAt=now
后续验证 → 检查设备绑定，更新lastUsed
```

## 修复步骤

### 1. 创建密钥时（已正确）
```javascript
// /api/keys POST
{
  usageCount: 0,         // ✅ 未激活
  status: 'active',      // 注意：这里status是'active'但usageCount=0表示未激活
  activatedAt: null      // ✅ 未激活时间
}
```

### 2. 修复validate-key API（需要修改）

**文件**: `/root/key_management_server.js`  
**位置**: 第552行 `app.post('/api/keys/validate-key')`  

**关键逻辑**:
```javascript
// 1. 密钥不存在
if (!existingKey) {
  // 验证格式后，插入数据库为未激活状态
  usageCount: 0,
  status: 'inactive',
  activatedAt: null
  // 返回: "密钥未激活，请先激活"
}

// 2. 密钥存在，usageCount=0（未激活）
if (existingKey.usageCount === 0) {
  // 第一次验证，激活密钥
  await keysCollection.updateOne({ key }, {
    $set: {
      status: 'active',
      activatedAt: now,
      usageCount: 1,
      lastUsed: now,
      deviceId: deviceId
    }
  });
  // 返回: "密钥激活成功"
}

// 3. 密钥存在，usageCount>=1（已激活）
if (existingKey.usageCount >= 1) {
  // 检查设备绑定
  if (deviceId && existingKey.deviceId !== deviceId) {
    // 返回: "密钥已绑定其他设备"
  }
  // 同一设备，允许使用
  // 返回: "密钥验证成功"
}
```

## 状态说明

| usageCount | status | activatedAt | 说明 |
|-----------|--------|-------------|------|
| 0 | inactive | null | 新建，未激活 |
| 1 | active | timestamp | 第一次验证，已激活 |
| >1 | active | timestamp | 多次使用（同一设备）|

## 实施

由于修改较大，已将修复后的完整代码保存在 `/tmp/validate_key_fix.js`

需要手动替换 `key_management_server.js` 第552-700行的内容。

