# 台湾PK10自动爬虫系统 - Docker镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    cron \
    && rm -rf /var/lib/apt/lists/*

# 安装Chrome浏览器
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p data logs

# 设置执行权限
RUN chmod +x *.py *.sh

# 创建非root用户
RUN useradd -m -u 1000 scraper && chown -R scraper:scraper /app
USER scraper

# 暴露端口（如果需要API服务）
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=5m --timeout=30s --start-period=1m --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:3000/health', timeout=10)" || exit 1

# 默认命令
CMD ["python3", "auto_scraper.py", "--mode", "schedule"]