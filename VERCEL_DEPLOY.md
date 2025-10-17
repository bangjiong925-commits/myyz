# Vercel 部署指南 - 心跳功能

## 问题说明

**问题**：阿里云测试可以显示在线，Vercel测试不显示在线

**原因**：
1. 心跳数据保存在阿里云服务器的MongoDB数据库中
2. Vercel 是无状态的 serverless 环境，没有直接连接数据库
3. 密钥管理系统需要多个API来显示在线状态，但Vercel上缺少这些API代理

## 解决方案

创建 Vercel API 代理层，将所有请求转发到阿里云服务器。

### 已创建的API代理文件

```
api/
├── keys.js                    # 密钥列表API (GET/POST)
├── stats.js                   # 统计API (GET)
└── keys/
    ├── heartbeat.js          # 心跳API (POST) ✅
    ├── validate-key.js       # 密钥验证API (POST)
    └── check-usage.js        # 检查使用API (POST)
```

## 部署到 Vercel

### 方法1：通过 Git 自动部署（推荐）

1. **提交代码到 Git**
```bash
cd /Users/a1234/Documents/GitHub/myyz
git add api/ vercel.json
git commit -m "添加Vercel API代理支持在线状态显示"
git push origin main
```

2. **Vercel 自动部署**
   - Vercel 会自动检测到更新并重新部署
   - 等待 1-2 分钟部署完成

### 方法2：使用 Vercel CLI

```bash
# 安装 Vercel CLI（如果还没安装）
npm install -g vercel

# 部署
cd /Users/a1234/Documents/GitHub/myyz
vercel --prod
```

## 测试步骤

### 1. 测试心跳API

打开浏览器控制台，执行：

```javascript
// 替换为您的Vercel域名
const VERCEL_URL = 'https://your-app.vercel.app';

fetch(`${VERCEL_URL}/api/keys/heartbeat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ key: 'your-test-key' })
})
.then(r => r.json())
.then(data => console.log('心跳响应:', data));
```

### 2. 测试密钥列表API（获取在线状态）

```javascript
fetch(`${VERCEL_URL}/api/keys?limit=100`)
.then(r => r.json())
.then(data => {
  console.log('密钥列表:', data);
  
  // 检查在线状态
  const now = Date.now();
  const onlineKeys = data.data.filter(key => {
    if (key.lastHeartbeat) {
      const diff = now - new Date(key.lastHeartbeat).getTime();
      return diff < 90000; // 90秒内
    }
    return false;
  });
  
  console.log('在线数量:', onlineKeys.length);
});
```

### 3. 测试统计API

```javascript
fetch(`${VERCEL_URL}/api/stats`)
.then(r => r.json())
.then(data => console.log('统计数据:', data));
```

## 在密钥管理系统中测试

### 步骤1：打开密钥管理系统

访问：`https://your-app.vercel.app/key_management.html`

### 步骤2：查看控制台日志

打开浏览器开发者工具（F12），查看Console标签：

```
应该看到：
✅ API Base: /api
✅ 🔍 检查在线状态，当前时间: xx:xx:xx
✅ 💚 当前在线数量: X
```

### 步骤3：发送测试心跳

使用测试文件 `test_heartbeat_directly.html`：

1. 修改文件中的 API 地址：
```javascript
// 将这行：
const apiUrl = window.location.hostname.includes('vercel.app')
    ? '/api/keys/heartbeat'
    : 'http://47.242.214.89/api/keys/heartbeat';

// 改为：
const apiUrl = '/api/keys/heartbeat';  // 使用相对路径
```

2. 访问：`https://your-app.vercel.app/test_heartbeat_directly.html`

3. 输入测试密钥，点击"开始测试"

4. 回到密钥管理系统，应该能看到在线状态

## 工作原理

```
用户设备 (TWPK.html)
    ↓
每30秒发送心跳
    ↓
Vercel API (/api/keys/heartbeat)
    ↓
转发到阿里云服务器 (47.242.214.89)
    ↓
保存到 MongoDB (lastHeartbeat字段)
    ↓
密钥管理系统查询
    ↓
Vercel API (/api/keys)
    ↓
转发到阿里云服务器
    ↓
返回密钥列表（包含lastHeartbeat）
    ↓
前端计算在线状态
```

## 在线状态判断逻辑

密钥被认为"在线"的条件：
- `lastHeartbeat` 存在
- `当前时间 - lastHeartbeat < 90秒`

```javascript
const now = Date.now();
const ONLINE_THRESHOLD = 90 * 1000; // 90秒

const isOnline = key.lastHeartbeat && 
                 (now - new Date(key.lastHeartbeat).getTime()) < ONLINE_THRESHOLD;
```

## 故障排查

### 问题1：Vercel上仍然不显示在线

**检查**：
```bash
# 确认文件已部署
curl https://your-app.vercel.app/api/keys?limit=1

# 应该返回JSON数据，不是404
```

**解决**：
- 确认已提交并推送所有文件到Git
- 等待Vercel部署完成
- 检查Vercel部署日志

### 问题2：心跳发送失败

**检查浏览器控制台**：
- 查看是否有CORS错误
- 查看网络请求状态码

**解决**：
- 检查 `vercel.json` 的 CORS 配置
- 确认阿里云服务器可以访问

### 问题3：API返回404

**原因**：Vercel的路由规则问题

**解决**：
```bash
# 检查文件结构
ls -la api/
ls -la api/keys/

# 确保文件存在：
# api/keys.js
# api/stats.js
# api/keys/heartbeat.js
# api/keys/validate-key.js
# api/keys/check-usage.js
```

### 问题4：数据延迟

**正常现象**：
- 心跳间隔：30秒
- 在线状态更新：30秒
- 最大延迟：最多60秒

**如果超过60秒还未显示**：
- 检查阿里云服务器状态
- 检查数据库连接
- 查看服务器日志

## 验证清单

部署完成后，逐项检查：

- [ ] Git 提交包含所有新文件
- [ ] Vercel 部署成功（没有错误）
- [ ] `/api/keys/heartbeat` 返回200
- [ ] `/api/keys?limit=100` 返回密钥列表
- [ ] `/api/stats` 返回统计数据
- [ ] `test_heartbeat_directly.html` 能发送心跳
- [ ] 密钥管理系统显示在线数量
- [ ] 点击"当前在线"能看到在线密钥列表

## 重要提示

⚠️ **所有数据仍然保存在阿里云服务器**

- Vercel 只是代理层
- 实际数据库在阿里云
- 如果阿里云服务器停止，Vercel也无法工作

✅ **优势**：
- 单一数据源（阿里云MongoDB）
- Vercel提供全球CDN加速
- 自动HTTPS支持
- 无需额外数据库费用

## 下一步

如果需要更好的性能，可以考虑：

1. **使用Vercel KV或MongoDB Atlas**
   - 让Vercel直接连接数据库
   - 减少网络延迟

2. **使用WebSocket**
   - 实时推送在线状态
   - 减少轮询请求

3. **添加缓存层**
   - Redis缓存在线状态
   - 减少数据库查询







