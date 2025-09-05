#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本：同时运行API服务器和自动爬虫
"""

import os
import sys
import subprocess
import threading
import time
import signal
from datetime import datetime

def log_message(service, message):
    """记录日志消息"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{service}] {message}")

def run_api_server():
    """运行API服务器"""
    try:
        log_message("API", "启动MongoDB API服务器...")
        port = os.environ.get('PORT', '3000')
        mongodb_uri = os.environ.get('MONGODB_URI')
        
        if not mongodb_uri:
            log_message("API", "错误: 未设置MONGODB_URI环境变量")
            sys.exit(1)
            
        cmd = [sys.executable, 'mongodb_api.py', '--port', port, '--mongodb-uri', mongodb_uri]
        subprocess.run(cmd, check=True)
    except Exception as e:
        log_message("API", f"API服务器错误: {e}")
        sys.exit(1)

def run_auto_scraper():
    """运行自动爬虫"""
    try:
        # 等待API服务器启动
        time.sleep(5)
        log_message("SCRAPER", "启动自动爬虫...")
        cmd = [sys.executable, 'auto_scraper.py']
        # 使用Popen启动非阻塞进程
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        log_message("SCRAPER", f"爬虫进程已启动，PID: {process.pid}")
        
        # 监控爬虫进程输出
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                log_message("SCRAPER", output.strip())
        
        # 检查进程退出状态
        return_code = process.poll()
        if return_code != 0:
            stderr_output = process.stderr.read()
            log_message("SCRAPER", f"爬虫进程异常退出，返回码: {return_code}")
            if stderr_output:
                log_message("SCRAPER", f"错误信息: {stderr_output}")
        else:
            log_message("SCRAPER", "爬虫进程正常退出")
            
    except Exception as e:
        log_message("SCRAPER", f"爬虫启动错误: {e}")
        # 爬虫出错不退出整个程序，继续提供API服务

def signal_handler(signum, frame):
    """信号处理器"""
    log_message("SYSTEM", "收到退出信号，正在关闭服务...")
    sys.exit(0)

def main():
    """主函数"""
    log_message("SYSTEM", "启动台湾PK10服务...")
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 检查环境变量
    mongodb_uri = os.environ.get('MONGODB_URI')
    if not mongodb_uri:
        log_message("SYSTEM", "警告: 未设置MONGODB_URI环境变量")
    
    # 创建线程运行爬虫
    scraper_thread = threading.Thread(target=run_auto_scraper, daemon=True)
    scraper_thread.start()
    
    # 主线程运行API服务器
    run_api_server()

if __name__ == "__main__":
    main()