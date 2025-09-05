# 远程MongoDB连接配置指南

## 概述
根据您的要求，系统已配置为仅使用远程网络连接，不再使用本地MongoDB连接。

## 已完成的配置更改

### 1. 环境变量配置
- ✅ 更新了 `.env` 文件，移除了所有本地连接配置
- ✅ 配置了远程MongoDB连接字符串模板
- ✅ 设置了相关环境变量

### 2. 应用程序配置
- ✅ `api_server.py` 已配置为使用环境变量中的远程连接
- ✅ `auto_scraper.py` 已配置为使用环境变量中的远程连接
- ✅ 所有Python脚本都支持从环境变量读取远程连接信息

## 需要您完成的步骤

### 步骤1: 获取MongoDB Atlas连接字符串
1. 访问 [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. 创建免费账户（如果还没有）
3. 创建新的集群
4. 设置数据库用户和密码
5. 配置网络访问（添加您的IP地址或设置为0.0.0.0/0允许所有IP）
6. 获取连接字符串

### 步骤2: 更新.env文件
编辑 `.env` 文件，将以下行：
```
MONGODB_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/taiwan_pk10?retryWrites=true&w=majority
```

替换为您的实际连接信息：
```
MONGODB_URI=mongodb+srv://实际用户名:实际密码@实际集群地址.mongodb.net/taiwan_pk10?retryWrites=true&w=majority
```

### 步骤3: 测试连接
运行测试脚本验证连接：
```bash
python3 test_remote_connection.py
```

### 步骤4: 启动服务
```bash
# 启动API服务器
python3 api_server.py

# 启动自动爬虫（在另一个终端）
python3 auto_scraper.py
```

## 其他远程MongoDB选项

### 1. MongoDB Atlas（推荐）
- 免费层提供512MB存储
- 自动备份和监控
- 全球分布式

### 2. 其他云服务
- AWS DocumentDB
- Azure Cosmos DB
- Google Cloud Firestore

### 3. 自建远程服务器
如果您有自己的服务器，可以使用：
```
MONGODB_URI=mongodb://username:password@your-server-ip:27017/taiwan_pk10?authSource=admin
```

## 验证配置

### 检查环境变量
```bash
echo $MONGODB_URI
echo $MONGODB_DB_NAME
```

### 检查应用程序连接
- API服务器启动时会显示数据库连接状态
- 爬虫启动时会显示连接信息
- 可以通过日志查看连接状态

## 故障排除

### 常见问题
1. **DNS解析失败**: 检查网络连接和集群地址
2. **认证失败**: 验证用户名和密码
3. **网络访问被拒绝**: 检查MongoDB Atlas的网络访问设置
4. **连接超时**: 检查防火墙设置

### 测试命令
```bash
# 测试基本连接
python3 test_remote_connection.py

# 测试API服务器
curl http://localhost:3000/api/health

# 查看服务日志
tail -f logs/app.log
```

## 安全注意事项

1. **不要在代码中硬编码连接字符串**
2. **使用强密码**
3. **限制网络访问IP范围**
4. **定期轮换密码**
5. **启用MongoDB的安全功能**

## 支持

如果遇到问题，请检查：
1. MongoDB Atlas控制台的连接状态
2. 应用程序日志
3. 网络连接
4. 防火墙设置

---

**重要提醒**: 系统现在完全依赖远程MongoDB连接。请确保您的远程数据库服务稳定可靠，并做好数据备份。