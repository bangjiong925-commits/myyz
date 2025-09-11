#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的静态文件服务器
用于Railway部署，提供TWPK页面服务
"""

import os
import sys
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StaticFileHandler(BaseHTTPRequestHandler):
    """静态文件处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        try:
            # 解析URL路径
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            # 根路径返回TWPK.html
            if path == '/' or path == '':
                self.serve_file('TWPK.html')
                return
            
            # 移除开头的斜杠
            if path.startswith('/'):
                path = path[1:]
            
            # 提供静态文件服务
            self.serve_file(path)
            
        except Exception as e:
            logger.error(f"处理请求时出错: {e}")
            self.send_error_response(500, "Internal Server Error")
    
    def serve_file(self, file_path):
        """提供文件服务"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.warning(f"文件不存在: {file_path}")
                self.send_error_response(404, "File Not Found")
                return
            
            # 读取文件内容
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 获取MIME类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', str(len(content)))
            self.add_cors_headers()
            self.end_headers()
            
            # 发送文件内容
            self.wfile.write(content)
            
            logger.info(f"成功提供文件: {file_path}")
            
        except Exception as e:
            logger.error(f"提供文件服务时出错: {e}")
            self.send_error_response(500, "Internal Server Error")
    
    def send_error_response(self, code, message):
        """发送错误响应"""
        try:
            self.send_response(code)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.add_cors_headers()
            self.end_headers()
            
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>错误 {code}</title>
                <meta charset="utf-8">
            </head>
            <body>
                <h1>错误 {code}</h1>
                <p>{message}</p>
            </body>
            </html>
            """
            
            self.wfile.write(error_html.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"发送错误响应时出错: {e}")
    
    def add_cors_headers(self):
        """添加CORS头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_response(200)
        self.add_cors_headers()
        self.end_headers()
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        logger.info(f"{self.address_string()} - {format % args}")

def main():
    """主函数"""
    try:
        # 获取端口号（Railway会设置PORT环境变量）
        port = int(os.environ.get('PORT', 8000))
        
        # 创建服务器
        server = HTTPServer(('0.0.0.0', port), StaticFileHandler)
        
        logger.info(f"静态文件服务器启动在端口 {port}")
        logger.info(f"访问 http://localhost:{port} 查看TWPK页面")
        
        # 启动服务器
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("服务器被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()