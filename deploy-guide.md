# 密钥管理系统部署指南

## 📋 概述

本指南将帮助您将密钥管理系统部署到生产环境。密钥管理系统提供了一个安全的Web界面来管理API密钥。

## 🚀 部署选项

### 1. Railway 部署

#### 前置条件
- Railway 账户
- GitHub 仓库连接到 Railway

#### 部署步骤
1. 在 Railway 中创建新项目
2. 连接您的 GitHub 仓库
3. 配置环境变量（见下方配置部分）
4. Railway 将自动检测并部署多个服务：
   - `web`: 静态文件服务器 (Python)
   - `api`: MongoDB API 服务器 (Node.js)
   - `keys`: 密钥管理服务器 (Node.js)

### 2. Vercel 部署

#### 前置条件
- Vercel 账户
- 外部 MongoDB 数据库（如 MongoDB Atlas）

#### 部署步骤
1. 在 Vercel 中导入项目
2. 配置环境变量
3. 部署静态文件和 API 函数

## ⚙️ 环境变量配置

### 必需的环境变量

```bash
# MongoDB 配置
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/myyz_db

# 密钥管理服务器
KEY_MANAGEMENT_PORT=3002

# 安全配置
SESSION_SECRET=your_strong_session_secret_here
JWT_SECRET=your_strong_jwt_secret_here

# CORS 配置
ALLOWED_ORIGINS=https://yourdomain.com

# 密钥管理安全
KEY_MANAGEMENT_ADMIN_PASSWORD=your_secure_admin_password
KEY_MANAGEMENT_ENCRYPTION_KEY=your_32_character_encryption_key
```

### 可选的环境变量

```bash
# 生产环境标识
NODE_ENV=production

# Redis 配置（如果使用）
KV_REST_API_URL=your_vercel_kv_url
KV_REST_API_TOKEN=your_vercel_kv_token
```

## 🔒 安全注意事项

1. **强密码**: 确保所有密码和密钥都足够强
2. **HTTPS**: 生产环境必须使用 HTTPS
3. **CORS**: 正确配置允许的域名
4. **环境变量**: 永远不要在代码中硬编码敏感信息
5. **访问控制**: 考虑添加IP白名单或其他访问限制

## 📁 文件结构

```
/
├── key_management_server.js    # 密钥管理后端服务
├── key_management.html         # 密钥管理Web界面
├── Procfile                   # Railway部署配置
├── railway.toml               # Railway详细配置
├── package.json               # Node.js依赖
└── .env.example              # 环境变量模板
```

## 🌐 访问地址

部署成功后，您可以通过以下地址访问：

- **主站**: `https://your-domain.com`
- **API服务**: `https://your-domain.com:3001` (如果单独部署)
- **密钥管理**: `https://your-domain.com:3002` (如果单独部署)

## 🔧 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 MONGODB_URI 是否正确
   - 确认数据库服务器可访问
   - 验证用户名和密码

2. **CORS 错误**
   - 检查 ALLOWED_ORIGINS 配置
   - 确认域名格式正确（包含协议）

3. **服务启动失败**
   - 检查所有必需的环境变量
   - 查看服务日志获取详细错误信息

### 日志查看

- **Railway**: 在项目仪表板中查看部署日志
- **Vercel**: 在函数日志中查看运行时错误

## 📞 支持

如果遇到部署问题，请检查：
1. 环境变量配置
2. 数据库连接
3. 服务日志
4. 网络和防火墙设置

## 🔄 更新部署

1. 推送代码到 GitHub
2. 平台将自动重新部署
3. 验证所有服务正常运行
4. 测试密钥管理功能

---

**注意**: 首次部署后，建议立即更改所有默认密码和密钥。