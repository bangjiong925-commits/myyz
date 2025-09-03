#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日数据库清理脚本 - 自动保留最近7天的数据
"""

import os
import sys
import subprocess
from datetime import datetime

def run_daily_cleanup():
    """
    执行每日数据库清理，保留最近7天的数据
    """
    print(f"开始执行每日数据库清理 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cleanup_script = os.path.join(script_dir, 'cleanup_database.py')
        
        # 检查cleanup_database.py是否存在
        if not os.path.exists(cleanup_script):
            print(f"错误: 找不到清理脚本 {cleanup_script}")
            return False
        
        # 执行清理命令
        cmd = [
            'python3', cleanup_script,
            '--keep-days', '7',
            '--confirm'
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        print("-" * 40)
        
        # 使用subprocess执行命令，自动输入YES确认
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=script_dir
        )
        
        # 发送YES确认
        stdout, stderr = process.communicate(input='YES\n')
        
        # 输出结果
        if stdout:
            print(stdout)
        
        if stderr:
            print(f"错误输出: {stderr}")
        
        # 检查执行结果
        if process.returncode == 0:
            print("\n✓ 每日数据库清理成功完成！")
            return True
        else:
            print(f"\n✗ 清理失败，退出码: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"✗ 执行清理时发生错误: {e}")
        return False

def main():
    """
    主函数
    """
    success = run_daily_cleanup()
    
    if success:
        print(f"\n每日清理任务完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sys.exit(0)
    else:
        print(f"\n每日清理任务失败 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sys.exit(1)

if __name__ == '__main__':
    main()