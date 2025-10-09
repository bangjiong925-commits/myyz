# 台湾PK10项目 - Windows本地部署指南

## 📋 目录
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [详细步骤](#详细步骤)
- [数据库配置](#数据库配置)
- [服务管理](#服务管理)
- [常见问题](#常见问题)
- [高级配置](#高级配置)

## 🎯 环境要求

### 系统要求
- **操作系统**: Windows 10/11 (64位)
- **内存**: 最少 4GB RAM
- **硬盘**: 最少 2GB 可用空间
- **网络**: 稳定的互联网连接

### 软件要求
- **Python**: 3.8 或更高版本
- **Node.js**: 16.0 或更高版本
- **Git**: 最新版本 (可选)

## 🚀 快速开始

### 方法一: 一键部署 (推荐)

1. **下载项目**
   ```bash
   git clone https://github.com/bangjiong925-commits/myyz.git
   cd myyz
   ```

2. **运行部署脚本**
   ```bash
   # 双击运行或在命令行执行
   deploy\start_windows.bat
   ```

3. **访问应用**
   - 主页面: http://localhost:8000/TWPK.html
   - 管理页面: http://localhost:8000/index.html
   - API接口: http://localhost:3000/api

### 方法二: 手动部署

如果自动部署失败，请按照[详细步骤](#详细步骤)进行手动配置。

## 📝 详细步骤

### 步骤1: 安装基础环境

#### 1.1 安装Python
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载Python 3.8+版本
3. 安装时勾选 "Add Python to PATH"
4. 验证安装:
   ```cmd
   python --version
   pip --version
   ```

#### 1.2 安装Node.js
1. 访问 [Node.js官网](https://nodejs.org/)
2. 下载LTS版本
3. 按默认设置安装
4. 验证安装:
   ```cmd
   node --version
   npm --version
   ```

#### 1.3 安装Git (可选)
1. 访问 [Git官网](https://git-scm.com/)
2. 下载并安装
3. 验证安装:
   ```cmd
   git --version
   ```

### 步骤2: 下载项目

#### 使用Git (推荐)
```bash
git clone https://github.com/bangjiong925-commits/myyz.git
cd myyz
```

#### 直接下载
1. 访问项目GitHub页面
2. 点击 "Code" -> "Download ZIP"
3. 解压到本地目录

### 步骤3: 安装依赖

#### 3.1 安装Python依赖
```bash
cd deploy
pip install -r requirements.txt
```

#### 3.2 安装Node.js依赖
```bash
npm install
```

### 步骤4: 配置数据库

#### 4.1 运行数据库配置脚本
```bash
python windows_database_setup.py
```

#### 4.2 选择数据库类型
- **SQLite** (推荐): 无需额外配置，适合个人使用
- **MySQL**: 需要安装MySQL Server
- **PostgreSQL**: 需要安装PostgreSQL

### 步骤5: 启动服务

#### 5.1 启动Web服务器
```bash
python -m http.server 8000
```

#### 5.2 启动API服务器
```bash
node api_server.js
```

#### 5.3 启动数据抓取服务
```bash
python data_fetcher.py
```

## 🗄️ 数据库配置

### SQLite配置 (推荐)
```python
# 配置文件: database_manager.py
config = {
    'database': 'data/taiwan_pk10.db'
}
```

**优点**: 
- 无需额外安装
- 配置简单
- 适合个人使用

**缺点**: 
- 并发性能有限
- 不支持网络访问

### MySQL配置
```python
config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_password',
    'database': 'taiwan_pk10'
}
```

**安装MySQL**:
1. 下载 [MySQL Community Server](https://dev.mysql.com/downloads/mysql/)
2. 安装并设置root密码
3. 创建数据库用户

### PostgreSQL配置
```python
config = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'your_password',
    'database': 'taiwan_pk10'
}
```

**安装PostgreSQL**:
1. 下载 [PostgreSQL](https://www.postgresql.org/download/windows/)
2. 安装并设置密码
3. 创建数据库

## 🔧 服务管理

### 启动所有服务
```bash
# 使用批处理脚本
deploy\start_windows.bat

# 或手动启动
start "Web服务器" cmd /k "python -m http.server 8000"
start "API服务器" cmd /k "node deploy\api_server.js"
start "数据抓取" cmd /k "python deploy\data_fetcher.py"
```

### 停止所有服务
```bash
# 使用批处理脚本
deploy\stop_windows.bat

# 或手动停止 (Ctrl+C 在各个命令行窗口)
```

### 服务状态检查
- **Web服务器**: http://localhost:8000
- **API服务器**: http://localhost:3000/api/health
- **数据库**: 检查 `data/taiwan_pk10.db` 文件

## ❓ 常见问题

### Q1: Python命令不识别
**解决方案**:
1. 重新安装Python，勾选"Add to PATH"
2. 手动添加Python到环境变量
3. 使用 `py` 命令替代 `python`

### Q2: 端口被占用
**解决方案**:
```bash
# 查看端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 结束进程
taskkill /f /pid [进程ID]
```

### Q3: 数据库连接失败
**解决方案**:
1. 检查数据库服务是否启动
2. 验证连接配置
3. 检查防火墙设置
4. 查看错误日志

### Q4: 依赖安装失败
**解决方案**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 单独安装失败的包
pip install [包名] --force-reinstall
```

### Q5: 数据抓取失败
**解决方案**:
1. 检查网络连接
2. 验证数据源URL
3. 查看抓取日志
4. 调整抓取间隔

## ⚙️ 高级配置

### 自定义端口
```javascript
// api_server.js
const PORT = process.env.PORT || 3001;  // 修改API端口

// 启动Web服务器
python -m http.server 8001  // 修改Web端口
```

### 数据抓取配置
```python
# data_fetcher.py
class DataFetcher:
    def __init__(self):
        self.fetch_interval = 60  # 抓取间隔(秒)
        self.retry_count = 5      # 重试次数
        self.retry_delay = 10     # 重试延迟(秒)
```

### 日志配置
```python
# 日志级别: DEBUG, INFO, WARNING, ERROR
logging.basicConfig(level=logging.INFO)

# 日志文件位置
log_file = 'logs/app.log'
```

### 性能优化
1. **数据库索引**: 自动创建期号和时间索引
2. **数据清理**: 定期清理30天前的数据
3. **内存管理**: 限制查询结果数量
4. **缓存机制**: 使用内存缓存热点数据

### 安全配置
1. **API访问控制**: 添加API密钥验证
2. **数据库安全**: 使用强密码和专用用户
3. **防火墙**: 限制外部访问
4. **HTTPS**: 配置SSL证书

## 📊 监控和维护

### 日志文件位置
- **应用日志**: `logs/app.log`
- **数据抓取日志**: `logs/data_fetcher.log`
- **错误日志**: `logs/error.log`

### 数据备份
```bash
# 自动备份 (每6小时)
python deploy/database_manager.py backup

# 手动备份
curl http://localhost:3000/api/backup > backup.json
```

### 性能监控
- **CPU使用率**: 任务管理器查看
- **内存使用**: 监控Python和Node.js进程
- **磁盘空间**: 定期清理日志和备份文件
- **网络流量**: 监控数据抓取频率

## 🆘 技术支持

如果遇到问题，请按以下顺序排查:

1. **查看日志文件** - 检查错误信息
2. **重启服务** - 停止并重新启动所有服务
3. **检查配置** - 验证数据库和网络配置
4. **更新依赖** - 升级Python和Node.js包
5. **联系支持** - 提供详细的错误信息和日志

---

## 📞 联系方式

- **项目地址**: https://github.com/bangjiong925-commits/myyz
- **问题反馈**: 在GitHub上提交Issue
- **技术交流**: 欢迎提交Pull Request

---

*最后更新: 2024年12月*