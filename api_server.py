#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API服务器 - 为TWPK.html提供数据抓取服务
"""

import os
import sys
import json
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient

class APIHandler(BaseHTTPRequestHandler):
    """API请求处理器"""
    
    def __init__(self, *args, **kwargs):
        # MongoDB连接配置
        self.mongo_uri = os.environ.get('MONGODB_URI')
        self.db_name = 'taiwan_pk10'
        self.collection_name = 'lottery_data'
        super().__init__(*args, **kwargs)
    
    def get_today_data_from_db(self):
        """从MongoDB获取今天的数据"""
        try:
            # 连接MongoDB
            client = MongoClient(self.mongo_uri)
            db = client[self.db_name]
            collection = db[self.collection_name]
            
            # 获取今天的日期范围（台湾时区）
            taiwan_tz = timezone(timedelta(hours=8))
            now_taiwan = datetime.now(taiwan_tz)
            today_start = now_taiwan.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            # 查询今天的数据 - 基于draw_date字段
            today_date_str = now_taiwan.strftime('%Y-%m-%d')
            query = {
                'draw_date': {
                    '$regex': f'^{today_date_str}'
                }
            }
            
            # 按期号降序排序
            cursor = collection.find(query).sort('period', -1)
            
            # 转换为列表
            today_data = []
            for doc in cursor:
                # 移除MongoDB的_id字段
                if '_id' in doc:
                    del doc['_id']
                # 转换datetime对象为字符串
                for key, value in doc.items():
                    if isinstance(value, datetime):
                        doc[key] = value.isoformat()
                today_data.append(doc)
            
            client.close()
            
            return {
                'success': True,
                'data': today_data,
                'count': len(today_data),
                'date': now_taiwan.strftime('%Y-%m-%d'),
                'timestamp': now_taiwan.isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'数据库查询失败: {str(e)}',
                'data': [],
                'count': 0
            }
    
    def get_latest_data_from_db(self, limit=100):
        """从MongoDB获取最新数据"""
        try:
            # 连接MongoDB
            client = MongoClient(self.mongo_uri)
            db = client[self.db_name]
            collection = db[self.collection_name]
            
            # 按期号降序排序，获取最新数据
            cursor = collection.find().sort('issue_number', -1).limit(limit)
            
            # 转换为列表
            latest_data = []
            for doc in cursor:
                # 移除MongoDB的_id字段
                if '_id' in doc:
                    del doc['_id']
                # 转换datetime对象为字符串
                for key, value in doc.items():
                    if isinstance(value, datetime):
                        doc[key] = value.isoformat()
                latest_data.append(doc)
            
            client.close()
            
            return latest_data
            
        except Exception as e:
            print(f"获取最新数据失败: {str(e)}")
            return []
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_HEAD(self):
        """处理HEAD请求 - 只返回头部信息，不返回内容"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            # 健康检查端点
            if path == '/health':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                return
            
            # 根路径或TWPK.html
            if path == '/' or path == '' or path == '/TWPK.html':
                if os.path.exists('TWPK.html'):
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                else:
                    self.send_error(404, 'File Not Found')
                return
            
            # 其他文件
            file_path = path.lstrip('/')
            if os.path.exists(file_path):
                self.send_response(200)
                if file_path.endswith('.html'):
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                elif file_path.endswith('.json'):
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                elif file_path.endswith('.js'):
                    self.send_header('Content-Type', 'application/javascript; charset=utf-8')
                elif file_path.endswith('.css'):
                    self.send_header('Content-Type', 'text/css; charset=utf-8')
                else:
                    self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
            else:
                self.send_error(404, 'File Not Found')
                
        except Exception as e:
            print(f"HEAD请求处理错误: {e}")
            self.send_error(500, 'Internal Server Error')
    
    def do_POST(self):
        """处理POST请求"""
        try:
            # 设置CORS头
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 解析请求路径
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/api/scrape':
                # 读取请求体
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                # 执行爬虫脚本
                result = self.run_scraper(request_data)
                
                # 返回结果
                response = json.dumps(result, ensure_ascii=False)
                self.wfile.write(response.encode('utf-8'))
            else:
                # 404错误
                self.send_error(404, 'Not Found')
                
        except Exception as e:
            print(f"API请求处理错误: {e}")
            error_response = {
                'success': False,
                'error': str(e)
            }
            response = json.dumps(error_response, ensure_ascii=False)
            self.wfile.write(response.encode('utf-8'))
    
    def do_GET(self):
        """处理GET请求 - 提供静态文件服务和API端点"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            # 健康检查端点
            if path == '/health':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = json.dumps({"status": "ok", "timestamp": datetime.now().isoformat()})
                self.wfile.write(response.encode('utf-8'))
                return
            
            # API数据端点 - 从远程MongoDB获取数据
            if path == '/api/taiwan-pk10-data':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                try:
                    # 从MongoDB获取最新数据
                    latest_data = self.get_latest_data_from_db()
                    response = json.dumps(latest_data, ensure_ascii=False)
                    self.wfile.write(response.encode('utf-8'))
                except Exception as e:
                    error_response = json.dumps({"error": f"获取数据失败: {str(e)}"}, ensure_ascii=False)
                    self.wfile.write(error_response.encode('utf-8'))
                return
            
            # 今天数据端点
            if path == '/api/today-data':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                try:
                    # 从MongoDB获取今天的数据
                    today_data = self.get_today_data_from_db()
                    response = json.dumps(today_data, ensure_ascii=False)
                    self.wfile.write(response.encode('utf-8'))
                except Exception as e:
                    error_response = json.dumps({"error": f"获取今天数据失败: {str(e)}"}, ensure_ascii=False)
                    self.wfile.write(error_response.encode('utf-8'))
                return
            
            file_path = path.lstrip('/')
            
            # 安全检查 - 防止目录遍历攻击
            if '..' in file_path or file_path.startswith('/'):
                self.send_error(403, 'Forbidden')
                return
            
            # 如果是根路径，返回API信息
            if file_path == '' or file_path == '/':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                api_info = {
                    'success': True,
                    'message': 'Taiwan PK10 API服务',
                    'version': '1.0.0',
                    'endpoints': [
                        '/api/today-data',
                        '/api/taiwan-pk10-data',
                        '/health'
                    ],
                    'timestamp': datetime.now().isoformat()
                }
                response = json.dumps(api_info, ensure_ascii=False)
                self.wfile.write(response.encode('utf-8'))
                return
            
            # 检查文件是否存在
            if os.path.exists(file_path):
                # 设置CORS头
                self.send_response(200)
                
                # 根据文件扩展名设置Content-Type
                if file_path.endswith('.html'):
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                elif file_path.endswith('.json'):
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                elif file_path.endswith('.js'):
                    self.send_header('Content-Type', 'application/javascript; charset=utf-8')
                elif file_path.endswith('.css'):
                    self.send_header('Content-Type', 'text/css; charset=utf-8')
                else:
                    self.send_header('Content-Type', 'application/octet-stream')
                
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # 读取并返回文件内容
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, 'File Not Found')
                
        except Exception as e:
            print(f"GET请求处理错误: {e}")
            self.send_error(500, 'Internal Server Error')
    
    def run_scraper(self, request_data):
        """执行Python爬虫脚本"""
        try:
            action = request_data.get('action', 'scrape_data')
            max_pages = request_data.get('max_pages', 5)
            
            if action == 'scrape_data':
                # 执行爬虫脚本
                cmd = [sys.executable, 'python_scraper.py', '--max-pages', str(max_pages)]
                
                print(f"执行命令: {' '.join(cmd)}")
                
                # 运行爬虫脚本
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )
                
                if result.returncode == 0:
                    # 爬虫执行成功，读取最新数据
                    try:
                        with open('latest_taiwan_pk10_data.json', 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        return {
                            'success': True,
                            'data': data,
                            'message': f'成功抓取 {len(data)} 条数据',
                            'timestamp': datetime.now().isoformat()
                        }
                    except FileNotFoundError:
                        return {
                            'success': False,
                            'error': '数据文件未找到'
                        }
                else:
                    # 爬虫执行失败
                    error_msg = result.stderr or result.stdout or '未知错误'
                    return {
                        'success': False,
                        'error': f'爬虫执行失败: {error_msg}'
                    }
            else:
                return {
                    'success': False,
                    'error': f'不支持的操作: {action}'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '爬虫执行超时'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'执行错误: {str(e)}'
            }
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def run_server(port=3000):
    """启动API服务器"""
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, APIHandler)
    
    print(f"API服务器启动在端口 {port}")
    print(f"访问地址: http://localhost:{port}")
    print("按 Ctrl+C 停止服务器")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        httpd.shutdown()
        httpd.server_close()
        print("服务器已停止")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='API服务器')
    parser.add_argument('--port', type=int, help='服务器端口')
    
    args = parser.parse_args()
    
    # 从命令行参数或环境变量获取端口号
    # Railway会设置PORT环境变量，如果没有则尝试RAILWAY_TCP_PROXY_PORT，最后使用3000
    if args.port:
        port = args.port
    else:
        port = int(os.environ.get('PORT', 
                   os.environ.get('RAILWAY_TCP_PROXY_PORT', 3000)))
    
    # 确保端口在有效范围内
    if port < 1 or port > 65535:
        port = 3000
    
    print(f"启动API服务器，端口: {port}")
    
    # 检查必要文件是否存在（仅警告，不退出）
    required_files = ['python_scraper.py', 'TWPK.html']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"警告: 缺少必要文件: {', '.join(missing_files)}")
        print("服务器将继续启动，但某些功能可能不可用")
    
    run_server(port)