# MongoDB Atlas 使用指南

本指南将帮助您直接使用MongoDB官方云服务(MongoDB Atlas)，而不需要通过Railway或其他中间平台。

## 步骤1: 创建MongoDB Atlas账户

1. 访问 [MongoDB Atlas官网](https://www.mongodb.com/cloud/atlas/register)
2. 注册一个新账户或使用现有账户登录

## 步骤2: 创建新集群

1. 登录后，点击「Build a Database」
2. 选择免费套餐(Free Tier)，它提供512MB存储空间，足够测试和小型应用使用
3. 选择云服务提供商(AWS, Google Cloud或Azure)和地区(建议选择离您或您的用户最近的地区)
4. 点击「Create Cluster」，等待集群创建完成(可能需要1-3分钟)

## 步骤3: 设置数据库访问

1. 在左侧导航栏中，点击「Database Access」
2. 点击「Add New Database User」
3. 创建一个用户名和密码(请使用强密码并保存好)
4. 选择适当的权限(对于简单应用，可以选择「Atlas admin」)
5. 点击「Add User」

## 步骤4: 设置网络访问

1. 在左侧导航栏中，点击「Network Access」
2. 点击「Add IP Address」
3. 您可以选择:
   - 添加您当前的IP地址(适合开发测试)
   - 添加`0.0.0.0/0`允许所有IP访问(不推荐用于生产环境，但便于测试)
4. 点击「Confirm」

## 步骤5: 获取连接字符串

1. 返回「Database」页面，点击「Connect」
2. 选择「Connect your application」
3. 选择「Python」作为驱动程序，版本选择3.6或更高
4. 复制显示的连接字符串，它看起来类似:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/<dbname>?retryWrites=true&w=majority
   ```
5. 将`<username>`和`<password>`替换为您之前创建的数据库用户凭据
6. 将`<dbname>`替换为`taiwan_pk10`

## 步骤6: 更新应用程序配置

### 方法1: 直接设置环境变量

```bash
# 设置MongoDB连接字符串
export MONGODB_URI="mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/taiwan_pk10?retryWrites=true&w=majority"

# 设置数据库名称
export MONGODB_DB_NAME="taiwan_pk10"

# 然后运行脚本
python check_today_data.py
```

### 方法2: 创建.env文件

创建一个名为`.env`的文件，内容如下:

```
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/taiwan_pk10?retryWrites=true&w=majority
MONGODB_DB_NAME=taiwan_pk10
```

然后修改您的Python脚本以加载这个.env文件(如果尚未实现):

```python
from dotenv import load_dotenv
load_dotenv()
```

## 步骤7: 测试连接

运行以下命令测试连接:

```bash
python check_today_data.py
```

如果一切设置正确，您应该能看到成功连接到MongoDB Atlas的信息。

## 数据迁移

如果您之前在本地或Railway上有数据，需要迁移到MongoDB Atlas:

1. 从原始MongoDB导出数据:
   ```bash
   mongodump --uri="原始MongoDB连接字符串" --db=taiwan_pk10
   ```

2. 导入数据到MongoDB Atlas:
   ```bash
   mongorestore --uri="MongoDB Atlas连接字符串" --db=taiwan_pk10 dump/taiwan_pk10
   ```

## 常见问题

### 连接超时

如果遇到连接超时问题:
1. 确认网络连接正常
2. 检查IP白名单设置
3. 验证用户名和密码正确

### 认证失败

如果遇到认证失败:
1. 确认用户名和密码正确
2. 检查用户是否有权限访问该数据库

### 数据库不存在

首次连接时，如果数据库不存在，MongoDB Atlas会自动创建它。您不需要预先创建数据库。

## 优势

使用MongoDB Atlas相比Railway或本地部署有以下优势:

1. 官方支持和可靠性
2. 自动备份和恢复
3. 性能监控和优化建议
4. 可扩展性，随着应用增长轻松升级
5. 全球分布式部署选项
6. 高级安全功能

## 注意事项

1. 免费套餐有一定限制，包括存储空间和连接数
2. 如果应用需要更高性能，可能需要升级到付费套餐
3. 定期备份重要数据，即使MongoDB Atlas提供自动备份