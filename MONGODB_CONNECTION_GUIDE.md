# MongoDB连接问题解决指南

## 问题描述

当运行`check_today_data.py`或其他需要连接MongoDB的脚本时，如果出现以下情况：

```
正在连接数据库...
```

并且长时间没有响应，这通常表示MongoDB连接超时。这可能是因为：

1. MongoDB服务未启动
2. MongoDB连接配置不正确
3. 网络问题导致无法连接到MongoDB服务器

## 解决方案

### 1. 启动MongoDB服务

我们提供了一个简单的脚本来帮助您启动MongoDB服务：

```bash
# 给脚本添加执行权限（如果尚未添加）
chmod +x start_mongodb.sh

# 运行脚本启动MongoDB服务
./start_mongodb.sh
```

这个脚本会自动检测您的环境并尝试启动MongoDB服务：
- 如果您使用Docker，它会启动docker-compose中的MongoDB容器
- 如果您使用macOS和Homebrew，它会启动本地MongoDB服务
- 如果您使用Linux，它会使用systemd启动MongoDB服务

### 2. 配置MongoDB连接

您可以通过环境变量配置MongoDB连接：

```bash
# 设置MongoDB连接字符串
export MONGODB_URI="mongodb://username:password@hostname:port/database?options"

# 设置数据库名称
export MONGODB_DB_NAME="taiwan_pk10"

# 然后运行脚本
python check_today_data.py
```

如果您使用Docker Compose，请确保在`docker-compose.yml`文件中正确配置了MongoDB服务和连接信息。

### 3. 检查连接配置

如果您使用Docker部署，请检查以下文件中的MongoDB配置：

- `.env.docker` - Docker环境的MongoDB配置
- `docker-compose.yml` - Docker服务配置

如果您使用Railway部署，请检查：

- `.env.railway` - Railway环境的MongoDB配置

### 4. 验证连接

修改配置后，运行以下命令验证连接：

```bash
python check_today_data.py
```

如果连接成功，您应该会看到类似以下的输出：

```
正在连接数据库...
使用连接字符串: mongodb://localhost:27017/
数据库名称: taiwan_pk10
数据库连接成功！
数据库中的集合: [...]
```

## 常见问题

### MongoDB服务未启动

如果您看到以下错误：

```
连接MongoDB服务器超时: [Errno 61] Connection refused
```

这表示MongoDB服务未启动或无法访问。请使用`start_mongodb.sh`脚本启动服务。

### 认证失败

如果您看到认证相关的错误，请检查连接字符串中的用户名和密码是否正确。

### 网络问题

如果您尝试连接远程MongoDB服务器（如MongoDB Atlas），请确保：

1. 连接字符串格式正确
2. 网络连接正常
3. IP地址已添加到MongoDB Atlas的白名单中

## 需要更多帮助？

如果您仍然遇到问题，请检查：

1. MongoDB日志以获取更详细的错误信息
2. 确保MongoDB版本兼容
3. 检查防火墙设置是否阻止了MongoDB连接