# Railway Procfile for Taiwan PK10 Scraper System

# Web service - File-based API Server (更适合Railway部署)
web: python3 api_server.py --port $PORT

# Worker service - Auto Scraper (定时爬虫)
worker: python3 auto_scraper.py

# Alternative: MongoDB API Server (需要MongoDB服务)
# mongodb: python3 mongodb_api.py