# 台湾宾果开奖数据抓取工具

这是一个用于抓取台湾宾果开奖数据的工具集，包含数据抓取、定时调度和API接口功能。

## 功能特性

- 🎯 **数据抓取**: 从官方网站抓取最新开奖数据
- ⏰ **定时调度**: 支持定时自动抓取数据
- 📊 **数据存储**: 自动保存历史开奖记录
- 🔌 **API接口**: 提供RESTful API获取数据
- 📱 **跨平台**: 支持Windows、macOS、Linux

## 安装依赖

```bash
npm install puppeteer
```

## 使用方法

### 1. 单次数据抓取

```bash
# 抓取一次最新开奖数据
npm run scrape

# 或者直接运行
node lottery_scraper.js
```

### 2. 定时数据抓取

```bash
# 每5分钟抓取一次（默认）
npm run schedule

# 每5分钟抓取一次
npm run schedule-5min

# 每10分钟抓取一次
npm run schedule-10min

# 自定义间隔（分钟）
node scheduler.js 3
```

### 3. API接口使用

数据抓取后，可以通过API接口获取数据：

```bash
# 获取最新一期数据
GET /api/lottery-data?latest=true

# 获取最近10期数据（默认）
GET /api/lottery-data

# 获取最近20期数据
GET /api/lottery-data?limit=20
```

## 数据格式

### 开奖数据结构

```json
{
  "time": "13:40",           // 开奖时间
  "period": "114046973",     // 期号
  "numbers": "14",           // 开奖号码
  "timestamp": "2025-08-20T05:43:08.033Z", // 抓取时间戳
  "source": "taiwan_bingo"   // 数据来源
}
```

### API响应格式

```json
{
  "success": true,
  "message": "获取数据成功",
  "data": [...],             // 开奖数据数组
  "total": 1,                // 总记录数
  "timestamp": "2025-08-20T05:43:08.033Z"
}
```

## 文件说明

- `lottery_scraper.js` - 核心抓取脚本
- `scheduler.js` - 定时调度器
- `api/lottery-data.js` - API接口
- `lottery_data.json` - 数据存储文件
- `package.json` - 项目配置和依赖

## 注意事项

1. **网络要求**: 需要稳定的网络连接访问台湾宾果官网
2. **数据更新**: 开奖数据每5分钟更新一次
3. **存储限制**: 默认保留最近100期数据
4. **浏览器依赖**: 使用Puppeteer需要Chrome/Chromium浏览器

## 故障排除

### 常见问题

1. **Puppeteer安装失败**
   ```bash
   # 使用国内镜像
   npm config set puppeteer_download_host=https://npm.taobao.org/mirrors
   npm install puppeteer
   ```

2. **抓取失败**
   - 检查网络连接
   - 确认目标网站可访问
   - 查看控制台错误信息

3. **数据格式异常**
   - 网站结构可能发生变化
   - 需要更新解析逻辑

## 开发说明

### 自定义抓取逻辑

如需修改抓取逻辑，编辑 `lottery_scraper.js` 中的 `parseLatestData` 方法：

```javascript
parseLatestData(text) {
    // 在这里添加自定义解析逻辑
    // ...
}
```

### 扩展API功能

在 `api/lottery-data.js` 中添加新的接口功能：

```javascript
// 添加新的查询参数处理
const { limit, latest, period } = req.query;
```

## 许可证

MIT License