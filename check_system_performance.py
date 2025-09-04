#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统性能检查脚本
检查CPU、内存、磁盘使用情况和相关进程状态
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime

def run_command(cmd):
    """执行系统命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "命令执行超时", 1
    except Exception as e:
        return "", str(e), 1

def check_cpu_usage():
    """检查CPU使用情况"""
    print("=== CPU 使用情况 ===")
    
    # 获取CPU使用率
    cmd = "top -l 1 -n 0 | grep 'CPU usage'"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and stdout:
        print(f"CPU使用率: {stdout}")
    else:
        print("无法获取CPU使用率")
    
    # 获取负载平均值
    cmd = "uptime"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and stdout:
        print(f"系统负载: {stdout}")
    else:
        print("无法获取系统负载")
    
    # 获取CPU核心数
    cmd = "sysctl -n hw.ncpu"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and stdout:
        print(f"CPU核心数: {stdout}")
    
    print()

def check_memory_usage():
    """检查内存使用情况"""
    print("=== 内存使用情况 ===")
    
    # 获取内存信息
    cmd = "vm_stat"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and stdout:
        lines = stdout.split('\n')
        page_size = 4096  # macOS页面大小通常是4KB
        
        memory_info = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().rstrip('.')
                if value.isdigit():
                    memory_info[key] = int(value) * page_size
        
        if 'Pages free' in memory_info and 'Pages active' in memory_info:
            free_memory = memory_info.get('Pages free', 0)
            active_memory = memory_info.get('Pages active', 0)
            inactive_memory = memory_info.get('Pages inactive', 0)
            wired_memory = memory_info.get('Pages wired down', 0)
            
            total_memory = free_memory + active_memory + inactive_memory + wired_memory
            used_memory = active_memory + wired_memory
            
            print(f"总内存: {format_bytes(total_memory)}")
            print(f"已使用: {format_bytes(used_memory)} ({used_memory/total_memory*100:.1f}%)")
            print(f"可用内存: {format_bytes(free_memory + inactive_memory)}")
            print(f"活跃内存: {format_bytes(active_memory)}")
            print(f"非活跃内存: {format_bytes(inactive_memory)}")
            print(f"系统内存: {format_bytes(wired_memory)}")
            
            # 内存使用率警告
            usage_percent = used_memory / total_memory * 100
            if usage_percent > 80:
                print("⚠️  内存使用率超过80%，建议关闭不必要的程序")
            elif usage_percent > 90:
                print("🚨 内存使用率超过90%，系统可能出现性能问题")
            else:
                print("✅ 内存使用率正常")
    else:
        print("无法获取内存信息")
    
    print()

def check_disk_usage():
    """检查磁盘使用情况"""
    print("=== 磁盘使用情况 ===")
    
    # 获取磁盘使用情况
    cmd = "df -h"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and stdout:
        lines = stdout.split('\n')
        print("磁盘分区使用情况:")
        for line in lines:
            if line.strip() and not line.startswith('Filesystem'):
                parts = line.split()
                if len(parts) >= 6:
                    filesystem = parts[0]
                    size = parts[1]
                    used = parts[2]
                    available = parts[3]
                    use_percent = parts[4]
                    mount_point = ' '.join(parts[5:])
                    
                    # 只显示主要分区
                    if mount_point in ['/', '/System/Volumes/Data', '/Users']:
                        print(f"  {mount_point}: {used}/{size} ({use_percent}) 可用: {available}")
                        
                        # 磁盘使用率警告
                        if use_percent.rstrip('%').isdigit():
                            usage = int(use_percent.rstrip('%'))
                            if usage > 90:
                                print(f"    🚨 {mount_point} 磁盘使用率超过90%")
                            elif usage > 80:
                                print(f"    ⚠️  {mount_point} 磁盘使用率超过80%")
    
    # 检查项目目录大小
    project_dir = "/Users/a1234/Documents/GitHub/myyz"
    cmd = f"du -sh {project_dir}"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and stdout:
        print(f"\n项目目录大小: {stdout}")
    
    print()

def check_network_connections():
    """检查网络连接"""
    print("=== 网络连接检查 ===")
    
    # 检查MongoDB连接
    cmd = "lsof -i :27017"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and stdout:
        print("MongoDB连接 (端口27017):")
        print(stdout)
    else:
        print("MongoDB服务未运行或无连接")
    
    # 检查HTTP服务
    for port in [3000, 8000, 5000]:
        cmd = f"lsof -i :{port}"
        stdout, stderr, code = run_command(cmd)
        
        if code == 0 and stdout:
            print(f"\n端口 {port} 使用情况:")
            print(stdout)
    
    print()

def check_python_processes():
    """检查Python相关进程"""
    print("=== Python 进程检查 ===")
    
    cmd = "ps aux | grep python | grep -v grep"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and stdout:
        lines = stdout.split('\n')
        python_processes = []
        
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 11:
                    pid = parts[1]
                    cpu = parts[2]
                    mem = parts[3]
                    command = ' '.join(parts[10:])
                    
                    # 过滤项目相关的进程
                    if 'myyz' in command or 'scraper' in command or 'api_server' in command:
                        python_processes.append({
                            'pid': pid,
                            'cpu': cpu,
                            'mem': mem,
                            'command': command
                        })
        
        if python_processes:
            print("项目相关的Python进程:")
            for proc in python_processes:
                print(f"  PID: {proc['pid']}, CPU: {proc['cpu']}%, 内存: {proc['mem']}%")
                print(f"    命令: {proc['command'][:80]}..." if len(proc['command']) > 80 else f"    命令: {proc['command']}")
        else:
            print("未发现项目相关的Python进程")
    else:
        print("无法获取Python进程信息")
    
    print()

def check_system_resources():
    """检查系统资源限制"""
    print("=== 系统资源限制 ===")
    
    # 检查文件描述符限制
    cmd = "ulimit -n"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and stdout:
        print(f"文件描述符限制: {stdout}")
    
    # 检查进程数限制
    cmd = "ulimit -u"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and stdout:
        print(f"进程数限制: {stdout}")
    
    # 检查当前打开的文件数
    cmd = "lsof | wc -l"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and stdout:
        print(f"当前打开的文件数: {stdout}")
    
    print()

def format_bytes(bytes_value):
    """格式化字节数"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f}{unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f}PB"

def generate_performance_summary():
    """生成性能摘要"""
    print("=== 性能摘要 ===")
    
    issues = []
    recommendations = []
    
    # 检查磁盘使用率
    cmd = "df -h / | tail -1 | awk '{print $5}' | sed 's/%//'"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and stdout.isdigit():
        disk_usage = int(stdout)
        if disk_usage > 90:
            issues.append(f"根分区磁盘使用率 {disk_usage}% 过高")
            recommendations.append("清理不必要的文件，释放磁盘空间")
        elif disk_usage > 80:
            issues.append(f"根分区磁盘使用率 {disk_usage}% 较高")
            recommendations.append("监控磁盘使用情况，考虑清理旧文件")
    
    # 检查负载平均值
    cmd = "uptime | awk '{print $(NF-2)}' | sed 's/,//'"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and stdout:
        try:
            load_avg = float(stdout)
            cpu_cores_cmd = "sysctl -n hw.ncpu"
            cpu_stdout, _, cpu_code = run_command(cpu_cores_cmd)
            
            if cpu_code == 0 and cpu_stdout.isdigit():
                cpu_cores = int(cpu_stdout)
                load_ratio = load_avg / cpu_cores
                
                if load_ratio > 1.0:
                    issues.append(f"系统负载过高 ({load_avg:.2f}, 核心数: {cpu_cores})")
                    recommendations.append("检查高CPU使用率的进程，优化或限制资源使用")
        except ValueError:
            pass
    
    if issues:
        print("发现的问题:")
        for issue in issues:
            print(f"  ⚠️  {issue}")
        
        print("\n建议措施:")
        for rec in recommendations:
            print(f"  💡 {rec}")
    else:
        print("✅ 系统性能状态良好")
    
    print()

def main():
    """主函数"""
    print("系统性能检查工具")
    print("=" * 50)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        check_cpu_usage()
        check_memory_usage()
        check_disk_usage()
        check_network_connections()
        check_python_processes()
        check_system_resources()
        generate_performance_summary()
        
    except KeyboardInterrupt:
        print("\n检查被用户中断")
    except Exception as e:
        print(f"检查过程中出现错误: {e}")

if __name__ == "__main__":
    main()