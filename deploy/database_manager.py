#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理类 - 统一的数据库操作接口
支持SQLite、MySQL、PostgreSQL
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

class DatabaseManager:
    def __init__(self, db_type='sqlite', config=None):
        self.db_type = db_type
        self.config = config or self.get_default_config()
        self.connection = None
    
    def get_default_config(self):
        """获取默认配置"""
        configs = {
            'sqlite': {
                'database': 'data/taiwan_pk10.db'
            },
            'mysql': {
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': 'your_password',
                'database': 'taiwan_pk10'
            },
            'postgresql': {
                'host': 'localhost',
                'port': 5432,
                'user': 'postgres',
                'password': 'your_password',
                'database': 'taiwan_pk10'
            }
        }
        return configs.get(self.db_type, configs['sqlite'])
    
    def connect(self):
        """建立数据库连接"""
        try:
            if self.db_type == 'sqlite':
                self.connection = sqlite3.connect(self.config['database'])
                self.connection.row_factory = sqlite3.Row  # 返回字典格式
                
            elif self.db_type == 'mysql':
                import mysql.connector
                self.connection = mysql.connector.connect(**self.config)
                
            elif self.db_type == 'postgresql':
                import psycopg2
                from psycopg2.extras import RealDictCursor
                self.connection = psycopg2.connect(**self.config)
                
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """执行查询语句"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            if self.db_type == 'sqlite':
                cursor = self.connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # 转换为字典列表
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
                
            elif self.db_type in ['mysql', 'postgresql']:
                cursor = self.connection.cursor(dictionary=True if self.db_type == 'mysql' else None)
                if self.db_type == 'postgresql':
                    from psycopg2.extras import RealDictCursor
                    cursor = self.connection.cursor(cursor_factory=RealDictCursor)
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                return cursor.fetchall()
                
        except Exception as e:
            print(f"❌ 查询执行失败: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = None) -> bool:
        """执行更新语句"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"❌ 更新执行失败: {e}")
            self.connection.rollback()
            return False
    
    def insert_data(self, period: str, numbers: str, draw_time: str = None) -> bool:
        """插入新数据"""
        if not draw_time:
            draw_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        query = """
            INSERT OR REPLACE INTO taiwan_pk10_data (period, numbers, draw_time)
            VALUES (?, ?, ?)
        """ if self.db_type == 'sqlite' else """
            INSERT INTO taiwan_pk10_data (period, numbers, draw_time)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE numbers = VALUES(numbers), draw_time = VALUES(draw_time)
        """ if self.db_type == 'mysql' else """
            INSERT INTO taiwan_pk10_data (period, numbers, draw_time)
            VALUES (%s, %s, %s)
            ON CONFLICT (period) DO UPDATE SET numbers = EXCLUDED.numbers, draw_time = EXCLUDED.draw_time
        """
        
        return self.execute_update(query, (period, numbers, draw_time))
    
    def get_latest_data(self, limit: int = 100) -> List[Dict]:
        """获取最新数据"""
        query = f"""
            SELECT period, numbers, draw_time, created_at
            FROM taiwan_pk10_data
            ORDER BY period DESC
            LIMIT {limit}
        """
        return self.execute_query(query)
    
    def get_data_by_period(self, period: str) -> Optional[Dict]:
        """根据期号获取数据"""
        query = """
            SELECT period, numbers, draw_time, created_at
            FROM taiwan_pk10_data
            WHERE period = ?
        """ if self.db_type == 'sqlite' else """
            SELECT period, numbers, draw_time, created_at
            FROM taiwan_pk10_data
            WHERE period = %s
        """
        
        results = self.execute_query(query, (period,))
        return results[0] if results else None
    
    def get_data_count(self) -> int:
        """获取数据总数"""
        query = "SELECT COUNT(*) as count FROM taiwan_pk10_data"
        result = self.execute_query(query)
        return result[0]['count'] if result else 0
    
    def delete_old_data(self, keep_days: int = 30) -> bool:
        """删除旧数据，保留指定天数"""
        query = """
            DELETE FROM taiwan_pk10_data
            WHERE created_at < datetime('now', '-{} days')
        """.format(keep_days) if self.db_type == 'sqlite' else """
            DELETE FROM taiwan_pk10_data
            WHERE created_at < DATE_SUB(NOW(), INTERVAL {} DAY)
        """.format(keep_days) if self.db_type == 'mysql' else """
            DELETE FROM taiwan_pk10_data
            WHERE created_at < NOW() - INTERVAL '{} days'
        """.format(keep_days)
        
        return self.execute_update(query)
    
    def backup_to_json(self, filename: str = None) -> bool:
        """备份数据到JSON文件"""
        if not filename:
            filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            data = self.get_latest_data(limit=10000)  # 获取所有数据
            
            # 转换datetime对象为字符串
            for item in data:
                for key, value in item.items():
                    if isinstance(value, datetime):
                        item[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 数据备份成功: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ 数据备份失败: {e}")
            return False
    
    def restore_from_json(self, filename: str) -> bool:
        """从JSON文件恢复数据"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            success_count = 0
            for item in data:
                if self.insert_data(item['period'], item['numbers'], item.get('draw_time')):
                    success_count += 1
            
            print(f"✅ 数据恢复成功: {success_count}/{len(data)} 条记录")
            return True
            
        except Exception as e:
            print(f"❌ 数据恢复失败: {e}")
            return False

# 使用示例
def example_usage():
    """使用示例"""
    # 创建数据库管理器实例
    db = DatabaseManager('sqlite')
    
    # 插入测试数据
    db.insert_data('20241201001', '01,02,03,04,05,06,07,08,09,10')
    db.insert_data('20241201002', '02,03,04,05,06,07,08,09,10,01')
    
    # 获取最新数据
    latest_data = db.get_latest_data(10)
    print("最新10条数据:")
    for item in latest_data:
        print(f"期号: {item['period']}, 号码: {item['numbers']}")
    
    # 获取数据总数
    count = db.get_data_count()
    print(f"数据总数: {count}")
    
    # 备份数据
    db.backup_to_json('taiwan_pk10_backup.json')
    
    # 关闭连接
    db.disconnect()

if __name__ == "__main__":
    example_usage()