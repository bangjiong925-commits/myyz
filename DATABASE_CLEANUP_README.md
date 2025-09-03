# 数据库清理系统 - 7天循环保留

本系统提供了自动化的数据库清理功能，可以保留最近7天的数据，自动删除更早的历史数据。

## 功能特性

- **自动清理**: 每天凌晨2点自动执行清理任务
- **7天保留**: 默认保留最近7天的数据
- **安全确认**: 支持预览模式和二次确认
- **多种模式**: 支持按天数、按日期、按期号范围清理
- **日志记录**: 详细的执行日志和结果记录

## 文件说明

### 核心文件

- `cleanup_database.py` - 主要的数据库清理脚本
- `daily_cleanup.py` - 每日自动清理脚本
- `setup_daily_cleanup.sh` - 自动设置crontab任务的脚本

### 配置文件

- `daily_cleanup_crontab.txt` - crontab配置示例
- `DATABASE_CLEANUP_README.md` - 本说明文档

## 快速开始

### 1. 自动设置（推荐）

```bash
# 进入项目目录
cd /Users/a1234/Documents/GitHub/myyz

# 运行自动设置脚本
./setup_daily_cleanup.sh
```

这将自动:
- 检查必要文件和依赖
- 创建logs目录
- 添加crontab任务（每天凌晨2点执行）
- 显示设置结果

### 2. 手动设置

如果需要手动设置crontab任务:

```bash
# 编辑crontab
crontab -e

# 添加以下行（每天凌晨2点执行）
0 2 * * * cd /Users/a1234/Documents/GitHub/myyz && /usr/bin/python3 daily_cleanup.py >> logs/daily_cleanup.log 2>&1

# 保存并退出
```

## 使用方法

### 手动执行清理

#### 1. 按天数清理（默认7天）

```bash
# 预览模式（不实际删除）
python3 cleanup_database.py --keep-days 7

# 实际执行清理
python3 cleanup_database.py --keep-days 7 --confirm

# 自定义保留天数（例如保留3天）
python3 cleanup_database.py --keep-days 3 --confirm
```

#### 2. 按指定日期清理

```bash
# 只保留2025-09-03的数据
python3 cleanup_database.py --target-date 2025-09-03 --confirm
```

#### 3. 按期号范围清理

```bash
# 只保留期号114049736到114049884的数据
python3 cleanup_database.py --start-period 114049736 --end-period 114049884 --confirm
```

#### 4. 使用每日清理脚本

```bash
# 执行每日清理任务（保留7天）
python3 daily_cleanup.py
```

### 查看帮助

```bash
python3 cleanup_database.py --help
```

## 配置选项

### 环境变量

- `MONGODB_URI`: MongoDB连接URI（默认: mongodb://localhost:27017）
- `MONGODB_DB_NAME`: 数据库名称（默认: taiwan_pk10）

### 命令行参数

- `--mongodb-uri`: MongoDB连接URI
- `--db-name`: 数据库名称
- `--keep-days`: 保留天数（默认7天）
- `--target-date`: 指定保留日期（格式: YYYY-MM-DD）
- `--start-period`: 起始期号（与--end-period一起使用）
- `--end-period`: 结束期号（与--start-period一起使用）
- `--confirm`: 确认执行（不加此参数为预览模式）

## 日志和监控

### 查看日志

```bash
# 查看每日清理日志
tail -f logs/daily_cleanup.log

# 查看最近的日志
tail -20 logs/daily_cleanup.log
```

### 检查crontab任务

```bash
# 查看当前的crontab任务
crontab -l

# 检查cron服务状态（macOS）
sudo launchctl list | grep cron
```

## 安全注意事项

1. **数据备份**: 在首次使用前，建议备份重要数据
2. **预览模式**: 首次使用时建议先运行预览模式
3. **二次确认**: 脚本会要求输入'YES'进行二次确认
4. **权限检查**: 确保脚本有足够权限访问数据库

## 故障排除

### 常见问题

1. **MongoDB连接失败**
   - 检查MongoDB服务是否运行
   - 验证连接URI是否正确
   - 检查网络连接

2. **权限错误**
   - 确保脚本有执行权限: `chmod +x *.sh`
   - 检查数据库访问权限

3. **crontab不执行**
   - 检查cron服务是否运行
   - 验证脚本路径是否正确
   - 检查Python路径是否正确

4. **日志文件不生成**
   - 确保logs目录存在
   - 检查写入权限

### 调试命令

```bash
# 测试数据库连接
python3 -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); print('连接成功' if client.admin.command('ping') else '连接失败')"

# 检查Python模块
python3 -c "import pymongo; print('pymongo版本:', pymongo.version)"

# 手动测试清理脚本
python3 cleanup_database.py --keep-days 7
```

## 自定义配置

### 修改执行时间

编辑crontab任务，修改时间设置:

```bash
# 每天凌晨3点执行
0 3 * * * cd /Users/a1234/Documents/GitHub/myyz && /usr/bin/python3 daily_cleanup.py >> logs/daily_cleanup.log 2>&1

# 每12小时执行一次
0 */12 * * * cd /Users/a1234/Documents/GitHub/myyz && /usr/bin/python3 daily_cleanup.py >> logs/daily_cleanup.log 2>&1
```

### 修改保留天数

编辑 `daily_cleanup.py` 文件，修改 `--keep-days` 参数:

```python
cmd = [
    'python3', cleanup_script,
    '--keep-days', '3',  # 改为保留3天
    '--confirm'
]
```

## 版本历史

- v1.0: 初始版本，支持按期号范围清理
- v1.1: 添加按日期清理功能
- v1.2: 添加按天数清理和自动化功能

## 支持

如有问题或建议，请查看日志文件或联系系统管理员。