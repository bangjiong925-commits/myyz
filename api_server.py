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
import threading
import time
from datetime import datetime

class APIHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
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
        """处理GET请求 - 提供静态文件服务"""
        try:
            parsed_path = urlparse(self.path)
            file_path = parsed_path.path.lstrip('/')
            
            # 安全检查 - 防止目录遍历攻击
            if '..' in file_path or file_path.startswith('/'):
                self.send_error(403, 'Forbidden')
                return
            
            # 如果是根路径，返回TWPK.html
            if file_path == '' or file_path == '/':
                file_path = 'TWPK.html'
            
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

def run_server(port=3001):
    """启动API服务器"""
    server_address = ('', port)
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
    port = args.port or int(os.environ.get('PORT', 3000))
    
    print(f"启动API服务器，端口: {port}")
    
    # 检查必要文件是否存在
    required_files = ['python_scraper.py', 'TWPK.html']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"错误: 缺少必要文件: {', '.join(missing_files)}")
        sys.exit(1)
    
    run_server(port)