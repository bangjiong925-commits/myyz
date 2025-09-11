# Railway Procfile for Taiwan PK10 Scraper System

# Web service - Simple Static File Server (静态文件服务器)
web: python3 simple_server.py

# Worker service - Auto Scraper (定时爬虫)
worker: python3 auto_scraper.py

# Cron service - September 5 Data Reader (9月5日数据定时读取)
cron: python3 railway_cron.py

# Alternative: File-based API Server
# file_api: python3 api_server.py --port ${PORT:-3000}