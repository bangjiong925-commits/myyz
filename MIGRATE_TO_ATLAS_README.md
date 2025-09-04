# 迁移到MongoDB Atlas指南

本指南将帮助您将现有的MongoDB数据（无论是本地MongoDB还是Railway上的MongoDB）迁移到MongoDB Atlas云服务。

## 准备工作

1. 按照 `MONGODB_ATLAS_GUIDE.md` 文件中的步骤创建MongoDB Atlas账户和集群
2. 获取MongoDB Atlas的连接字符串
3. 确保您的源MongoDB数据库可以正常访问

## 迁移步骤

### 1. 设置环境变量

```bash
# 源MongoDB连接信息（本地或Railway）
export SOURCE_MONGODB_URI="mongodb://localhost:27017/"
export SOURCE_DB_NAME="taiwan_pk10"

# 目标MongoDB Atlas连接信息
export TARGET_MONGODB_URI="mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/taiwan_pk10?retryWrites=true&w=majority"
export TARGET_DB_NAME="taiwan_pk10"
```

注意：
- 如果源数据库是本地MongoDB，使用默认值即可
- 如果源数据库是Railway上的MongoDB，请使用Railway提供的连接字符串
- 请将目标连接字符串中的`username`、`password`和`cluster0.xxxxx`替换为您的实际值

### 2. 运行迁移脚本

```bash
python migrate_to_atlas.py
```

或者

```bash
./migrate_to_atlas.py
```

### 3. 确认迁移结果

迁移完成后，脚本会显示迁移的数据条数。您可以通过以下命令检查MongoDB Atlas中的数据：

```bash
# 设置环境变量指向MongoDB Atlas
export MONGODB_URI="mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/taiwan_pk10?retryWrites=true&w=majority"
export MONGODB_DB_NAME="taiwan_pk10"

# 运行检查脚本
python check_today_data.py
```

## 更新应用程序配置

迁移完成后，您需要更新应用程序的配置，使其连接到MongoDB Atlas而不是原来的数据库：

### 1. 更新环境变量

对于本地开发环境，您可以创建一个`.env`文件：

```
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/taiwan_pk10?retryWrites=true&w=majority
MONGODB_DB_NAME=taiwan_pk10
```

### 2. 更新Docker配置

如果您使用Docker部署，更新`docker-compose.yml`文件中的环境变量：

```yaml
services:
  api:
    environment:
      - MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/taiwan_pk10?retryWrites=true&w=majority
      - MONGODB_DB_NAME=taiwan_pk10
```

## 常见问题

### 迁移过程中断

如果迁移过程中断，您可以重新运行迁移脚本。脚本会询问您是否要继续迁移并添加到现有数据中。

### 数据重复

如果您多次运行迁移脚本，可能会导致数据重复。建议在迁移前清空目标集合，或者使用MongoDB Atlas的界面删除集合后重新迁移。

### 连接问题

如果遇到连接问题，请参考`MONGODB_ATLAS_GUIDE.md`文件中的"常见问题"部分。

## 迁移后的优势

使用MongoDB Atlas相比本地MongoDB或Railway有以下优势：

1. 官方支持和可靠性
2. 自动备份和恢复
3. 性能监控和优化建议
4. 可扩展性，随着应用增长轻松升级
5. 全球分布式部署选项
6. 高级安全功能

## 后续步骤

成功迁移到MongoDB Atlas后，您可以：

1. 探索MongoDB Atlas的监控和性能优化功能
2. 设置自动备份策略
3. 配置警报和通知
4. 考虑使用MongoDB Atlas的其他功能，如全文搜索、数据湖等