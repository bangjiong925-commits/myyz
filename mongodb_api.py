#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB API服务器 - 直接从MongoDB数据库获取数据
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, date
import threading
import time

try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("警告: pymongo未安装，MongoDB功能将不可用")
    print("请运行: pip install pymongo")

class MongoDBAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, mongodb_uri=None, db_name="taiwan_pk10", **kwargs):
        self.mongodb_uri = mongodb_uri
        self.db_name = db_name
        self.mongo_client = None
        self.db = None
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """处理GET请求"""
        try:
            # 解析请求路径
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/api/today-data':
                # 设置JSON响应头
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # 获取今天的数据
                result = self.get_today_data()
                response = json.dumps(result, ensure_ascii=False)
                self.wfile.write(response.encode('utf-8'))
            elif parsed_path.path == '/api/latest-data':
                # 设置JSON响应头
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # 获取最新数据
                result = self.get_latest_data()
                response = json.dumps(result, ensure_ascii=False)
                self.wfile.write(response.encode('utf-8'))
            elif parsed_path.path == '/api/health' or parsed_path.path == '/health':
                # 设置JSON响应头
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # 健康检查 (支持 /health 和 /api/health 两个路径)
                result = self.health_check()
                response = json.dumps(result, ensure_ascii=False)
                self.wfile.write(response.encode('utf-8'))
            elif parsed_path.path == '/api/cleanup-history':
                # 设置JSON响应头
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # 清理历史数据
                result = self.cleanup_history_data()
                response = json.dumps(result, ensure_ascii=False)
                self.wfile.write(response.encode('utf-8'))
            elif parsed_path.path == '/api/taiwan-pk10-data':
                # 设置JSON响应头
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # 获取台湾PK10数据（兼容前端调用）
                query_params = parse_qs(parsed_path.query)
                limit = int(query_params.get('limit', [100])[0])
                result = self.get_taiwan_pk10_data(limit)
                response = json.dumps(result, ensure_ascii=False)
                self.wfile.write(response.encode('utf-8'))
            elif parsed_path.path == '/':
                # 根路径 - 返回index.html文件
                try:
                    # 读取index.html文件
                    index_path = os.path.join(os.path.dirname(__file__), 'index.html')
                    with open(index_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # 设置HTML响应头
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    self.wfile.write(html_content.encode('utf-8'))
                    return
                    
                except FileNotFoundError:
                    # 如果index.html不存在，返回备用HTML内容
                    backup_html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Taiwan PK10</title>
</head>
<body>
    <h1>Taiwan PK10 系统</h1>
    <p>正在加载...</p>
    <script>
        // 自动跳转到TWPK.html
        setTimeout(function() {
            window.location.href = 'TWPK.html';
        }, 1000);
    </script>
</body>
</html>
                    '''
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    self.wfile.write(backup_html.encode('utf-8'))
                    return
                    
                except Exception as e:
                    # 如果读取文件出错，返回错误页面
                    error_html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>错误 - Taiwan PK10</title>
</head>
<body>
    <h1>页面加载错误</h1>
    <p>无法加载主页: {str(e)}</p>
    <p><a href="/api/health">检查API状态</a></p>
</body>
</html>
                    '''
                    
                    self.send_response(500)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    self.wfile.write(error_html.encode('utf-8'))
                    return
            else:
                # 404错误
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {
                    'success': False,
                    'error': 'API端点未找到',
                    'timestamp': datetime.now().isoformat()
                }
                response = json.dumps(error_response, ensure_ascii=False)
                self.wfile.write(response.encode('utf-8'))
                
        except Exception as e:
            # 500错误
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # 确保错误信息能正确编码
                error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
                error_response = {
                    'success': False,
                    'error': f'服务器内部错误: {error_msg}',
                    'timestamp': datetime.now().isoformat()
                }
                response = json.dumps(error_response, ensure_ascii=False)
                self.wfile.write(response.encode('utf-8'))
            except Exception as inner_e:
                # 如果连错误响应都失败了，发送最基本的错误
                try:
                    self.send_response(500)
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(b'Internal Server Error')
                except:
                    pass
    
    def connect_mongodb(self):
        """连接MongoDB数据库"""
        if not MONGODB_AVAILABLE:
            return False
        
        try:
            self.mongo_client = MongoClient(self.mongodb_uri)
            self.db = self.mongo_client[self.db_name]
            # 测试连接
            self.mongo_client.admin.command('ping')
            return True
        except Exception as e:
            print(f"连接MongoDB失败: {e}")
            return False
    
    def get_today_data(self):
        """获取今天的数据"""
        if not self.connect_mongodb():
            return {
                'success': False,
                'error': 'MongoDB连接失败',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # 首先尝试从web_formatted_data集合获取最新的完整数据
            web_collection = self.db['web_formatted_data']
            latest_web_data = web_collection.find().sort([('created_at', -1)]).limit(1)
            
            for doc in latest_web_data:
                if 'data' in doc and doc['data']:
                    return {
                        'success': True,
                        'data': doc['data'],
                        'total_records': doc.get('total_records', len(doc['data'])),
                        'date': date.today().isoformat(),
                        'timestamp': datetime.now().isoformat(),
                        'message': f'成功获取今日数据 {len(doc["data"])} 条'
                    }
            
            # 如果web_formatted_data没有数据，则从lottery_data集合获取
            collection = self.db['lottery_data']
            today_str = date.today().isoformat()
            
            # 查询今天的数据（不限制条数）
            cursor = collection.find(
                {
                    'is_valid': True,
                    'draw_date': {'$regex': f'^{today_str}'}
                },
                sort=[('scraped_at', -1)]
            )
            
            data = []
            for doc in cursor:
                # 转换为前端需要的格式
                formatted_data = f"{doc['period']} {','.join(map(str, doc['draw_numbers']))}"
                data.append(formatted_data)
            
            if data:
                return {
                    'success': True,
                    'data': data,
                    'total_records': len(data),
                    'date': today_str,
                    'timestamp': datetime.now().isoformat(),
                    'message': f'成功获取今日数据 {len(data)} 条'
                }
            else:
                return {
                    'success': False,
                    'error': '今日暂无数据',
                    'date': today_str,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'获取数据失败: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
        finally:
            if self.mongo_client:
                self.mongo_client.close()
    
    def get_latest_data(self):
        """获取最新数据"""
        if not self.connect_mongodb():
            return {
                'success': False,
                'error': 'MongoDB连接失败',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # 获取最新的原始数据
            collection = self.db['lottery_data']
            
            # 获取最新100条数据
            cursor = collection.find(
                {'is_valid': True},
                sort=[('scraped_at', -1)]
            ).limit(100)
            
            data = []
            for doc in cursor:
                # 转换为前端需要的格式
                formatted_data = f"{doc['period']} {','.join(map(str, doc['draw_numbers']))}"
                data.append(formatted_data)
            
            if data:
                return {
                    'success': True,
                    'data': data,
                    'total_records': len(data),
                    'timestamp': datetime.now().isoformat(),
                    'message': f'成功获取最新数据 {len(data)} 条'
                }
            else:
                return {
                    'success': False,
                    'error': '暂无数据',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'获取数据失败: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
        finally:
            if self.mongo_client:
                self.mongo_client.close()
    
    def get_taiwan_pk10_data(self, limit=100):
        """获取台湾PK10数据（兼容前端调用）"""
        if not self.connect_mongodb():
            return {
                'success': False,
                'error': 'MongoDB连接失败',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # 首先尝试从web_formatted_data集合获取最新的完整数据
            web_collection = self.db['web_formatted_data']
            latest_web_data = web_collection.find().sort([('created_at', -1)]).limit(1)
            
            for doc in latest_web_data:
                if 'data' in doc and doc['data']:
                    # 限制返回的数据条数
                    limited_data = doc['data'][:limit] if limit > 0 else doc['data']
                    return limited_data
            
            # 如果web_formatted_data没有数据，则从lottery_data集合获取
            collection = self.db['lottery_data']
            
            # 查询最新数据
            cursor = collection.find(
                {'is_valid': True},
                sort=[('scraped_at', -1)]
            ).limit(limit)
            
            data = []
            for doc in cursor:
                # 转换为前端需要的格式
                formatted_data = f"{doc['period']} {','.join(map(str, doc['draw_numbers']))}"
                data.append(formatted_data)
            
            return data
                
        except Exception as e:
            return {
                'success': False,
                'error': f'获取数据失败: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
        finally:
            if self.mongo_client:
                self.mongo_client.close()
    
    def cleanup_history_data(self):
        """清理历史数据，只保留今天(2025-09-03)的数据"""
        if not self.connect_mongodb():
            return {
                'success': False,
                'error': 'MongoDB连接失败',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            today_str = '2025-09-03'  # 固定为9月3号
            
            # 清理lottery_data集合中的历史数据
            lottery_collection = self.db['lottery_data']
            
            # 删除不是今天的数据
            delete_result_lottery = lottery_collection.delete_many({
                'draw_date': {'$not': {'$regex': f'^{today_str}'}}
            })
            
            # 清理web_formatted_data集合中的历史数据
            web_collection = self.db['web_formatted_data']
            
            # 删除不是今天创建的数据
            delete_result_web = web_collection.delete_many({
                'created_at': {'$not': {'$regex': f'^{today_str}'}}
            })
            
            # 统计剩余数据
            remaining_lottery = lottery_collection.count_documents({})
            remaining_web = web_collection.count_documents({})
            
            return {
                'success': True,
                'deleted_lottery_records': delete_result_lottery.deleted_count,
                'deleted_web_records': delete_result_web.deleted_count,
                'remaining_lottery_records': remaining_lottery,
                'remaining_web_records': remaining_web,
                'target_date': today_str,
                'timestamp': datetime.now().isoformat(),
                'message': f'历史数据清理完成，删除了 {delete_result_lottery.deleted_count + delete_result_web.deleted_count} 条记录，保留了 {remaining_lottery + remaining_web} 条今日数据'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'清理数据失败: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
        finally:
            if self.mongo_client:
                self.mongo_client.close()
    
    def health_check(self):
        """健康检查"""
        mongodb_status = self.connect_mongodb()
        if self.mongo_client:
            self.mongo_client.close()
        
        return {
            'success': True,
            'mongodb_available': MONGODB_AVAILABLE,
            'mongodb_connected': mongodb_status,
            'timestamp': datetime.now().isoformat(),
            'message': 'API服务正常运行'
        }
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def create_handler_class(mongodb_uri, db_name):
    """创建带有MongoDB配置的处理器类"""
    class ConfiguredHandler(MongoDBAPIHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, mongodb_uri=mongodb_uri, db_name=db_name, **kwargs)
    return ConfiguredHandler

def run_mongodb_server(port=3002, mongodb_uri=None, db_name="taiwan_pk10"):
    """运行MongoDB API服务器"""
    handler_class = create_handler_class(mongodb_uri, db_name)
    server = HTTPServer(('', port), handler_class)
    
    print(f"MongoDB API服务器启动在端口 {port}")
    print(f"MongoDB URI: {mongodb_uri}")
    print(f"数据库名: {db_name}")
    print(f"访问地址: http://localhost:{port}")
    print("可用端点:")
    print(f"  - GET http://localhost:{port}/api/today-data (获取今日数据)")
    print(f"  - GET http://localhost:{port}/api/latest-data (获取最新数据)")
    print(f"  - GET http://localhost:{port}/api/health (健康检查)")
    print(f"  - GET http://localhost:{port}/api/cleanup-history (清理历史数据，只保留今日数据)")
    print("按 Ctrl+C 停止服务器")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        server.shutdown()
        print("服务器已停止")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='MongoDB API服务器')
    parser.add_argument('--port', type=int, help='服务器端口')
    parser.add_argument('--mongodb-uri', help='MongoDB连接URI')
    parser.add_argument('--db-name', default='taiwan_pk10', help='数据库名称')

    args = parser.parse_args()
    
    # 从环境变量或命令行参数获取配置
    port = args.port or int(os.environ.get('PORT', 3002))
    mongodb_uri = args.mongodb_uri or os.environ.get('MONGODB_URI')
    db_name = args.db_name or os.environ.get('MONGODB_DB_NAME', 'taiwan_pk10')
    
    print(f"启动配置:")
    print(f"  端口: {port}")
    print(f"  数据库: {db_name}")
    print(f"  MongoDB URI: {mongodb_uri[:20]}..." if len(mongodb_uri) > 20 else f"  MongoDB URI: {mongodb_uri}")
    
    # 检查MongoDB是否可用
    if not MONGODB_AVAILABLE:
        print("错误: pymongo未安装，无法启动MongoDB API服务器")
        print("请运行: pip install pymongo")
        sys.exit(1)

    run_mongodb_server(port, mongodb_uri, db_name)