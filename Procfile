# Railway Procfile for Taiwan PK10 Scraper System

# Web service - MongoDB API Server (直接连接MongoDB Atlas)
web: python3 mongodb_api.py --port ${PORT:-3000}

# Worker service - Auto Scraper (定时爬虫)
worker: python3 auto_scraper.py

# Alternative: File-based API Server
# file_api: python3 api_server.py --port ${PORT:-3000}