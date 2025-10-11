#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB数据库管理器
专门用于连接和管理Vercel MongoDB数据库
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import certifi

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MongoDBManager:
    """MongoDB数据库管理器"""
    
    def __init__(self, connection_string: str = None, database_name: str = "taiwan_pk10"):
        """
        初始化MongoDB连接
        
        Args:
            connection_string: MongoDB连接字符串
            database_name: 数据库名称
        """
        self.connection_string = connection_string or os.getenv('MONGODB_URI')
        self.database_name = database_name or os.getenv('MONGODB_DB_NAME', 'taiwan_pk10')
        self.client = None
        self.db = None
        self.collection_name = "pk10_results"
        
        if not self.connection_string:
            raise ValueError("MongoDB连接字符串未提供，请设置MONGODB_URI环境变量")
        
        self._connect()
    
    def _connect(self):
        """建立MongoDB连接"""
        try:
            # 使用certifi提供的CA证书
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                tlsCAFile=certifi.where()
            )
            
            # 测试连接
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            
            # 创建索引
            self._create_indexes()
            
            logger.info(f"成功连接到MongoDB数据库: {self.database_name}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB连接失败: {e}")
            raise
        except Exception as e:
            logger.error(f"MongoDB初始化失败: {e}")
            raise
    
    def _create_indexes(self):
        """创建数据库索引"""
        try:
            collection = self.db[self.collection_name]
            
            # 为期号创建唯一索引
            collection.create_index("issue", unique=True)
            
            # 为时间戳创建索引
            collection.create_index("timestamp", background=True)
            
            # 为日期创建索引
            collection.create_index("date", background=True)
            
            logger.info("数据库索引创建完成")
            
        except Exception as e:
            logger.warning(f"创建索引时出现警告: {e}")
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            if self.client:
                self.client.admin.command('ping')
                logger.info("MongoDB连接测试成功")
                return True
            return False
        except Exception as e:
            logger.error(f"MongoDB连接测试失败: {e}")
            return False
    
    def insert_data(self, data: Dict[str, Any]) -> bool:
        """
        插入单条数据
        
        Args:
            data: 要插入的数据
            
        Returns:
            bool: 插入是否成功
        """
        try:
            collection = self.db[self.collection_name]
            
            # 添加时间戳
            data['created_at'] = datetime.utcnow()
            data['updated_at'] = datetime.utcnow()
            
            # 使用upsert避免重复插入
            result = collection.update_one(
                {"issue": data["issue"]},
                {"$set": data},
                upsert=True
            )
            
            if result.upserted_id or result.modified_count > 0:
                logger.info(f"数据插入/更新成功: 期号 {data.get('issue')}")
                return True
            else:
                logger.warning(f"数据未发生变化: 期号 {data.get('issue')}")
                return False
                
        except Exception as e:
            logger.error(f"插入数据失败: {e}")
            return False
    
    def insert_batch_data(self, data_list: List[Dict[str, Any]]) -> int:
        """
        批量插入数据
        
        Args:
            data_list: 要插入的数据列表
            
        Returns:
            int: 成功插入的数据条数
        """
        if not data_list:
            return 0
        
        try:
            collection = self.db[self.collection_name]
            success_count = 0
            
            for data in data_list:
                try:
                    # 添加时间戳
                    data['created_at'] = datetime.utcnow()
                    data['updated_at'] = datetime.utcnow()
                    
                    # 使用upsert避免重复插入
                    result = collection.update_one(
                        {"issue": data["issue"]},
                        {"$set": data},
                        upsert=True
                    )
                    
                    if result.upserted_id or result.modified_count > 0:
                        success_count += 1
                        
                except Exception as e:
                    logger.error(f"插入单条数据失败: {e}")
                    continue
            
            logger.info(f"批量插入完成: {success_count}/{len(data_list)} 条数据成功")
            return success_count
            
        except Exception as e:
            logger.error(f"批量插入数据失败: {e}")
            return 0
    
    def get_latest_data(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取最新数据
        
        Args:
            limit: 返回数据条数
            
        Returns:
            List[Dict]: 最新数据列表
        """
        try:
            collection = self.db[self.collection_name]
            
            cursor = collection.find().sort("issue", DESCENDING).limit(limit)
            data = list(cursor)
            
            # 转换ObjectId为字符串
            for item in data:
                if '_id' in item:
                    item['_id'] = str(item['_id'])
                # 转换datetime为字符串
                for key, value in item.items():
                    if isinstance(value, datetime):
                        item[key] = value.isoformat()
            
            logger.info(f"获取最新数据成功: {len(data)} 条")
            return data
            
        except Exception as e:
            logger.error(f"获取最新数据失败: {e}")
            return []
    
    def get_data_by_issue(self, issue: str) -> Optional[Dict[str, Any]]:
        """
        根据期号获取数据
        
        Args:
            issue: 期号
            
        Returns:
            Dict: 数据记录，如果不存在返回None
        """
        try:
            collection = self.db[self.collection_name]
            
            data = collection.find_one({"issue": issue})
            
            if data:
                # 转换ObjectId为字符串
                if '_id' in data:
                    data['_id'] = str(data['_id'])
                # 转换datetime为字符串
                for key, value in data.items():
                    if isinstance(value, datetime):
                        data[key] = value.isoformat()
                
                logger.info(f"根据期号获取数据成功: {issue}")
                return data
            else:
                logger.warning(f"未找到期号为 {issue} 的数据")
                return None
                
        except Exception as e:
            logger.error(f"根据期号获取数据失败: {e}")
            return None
    
    def get_data_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        根据日期范围获取数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            List[Dict]: 数据列表
        """
        try:
            collection = self.db[self.collection_name]
            
            cursor = collection.find({
                "date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }).sort("issue", DESCENDING)
            
            data = list(cursor)
            
            # 转换ObjectId为字符串
            for item in data:
                if '_id' in item:
                    item['_id'] = str(item['_id'])
                # 转换datetime为字符串
                for key, value in item.items():
                    if isinstance(value, datetime):
                        item[key] = value.isoformat()
            
            logger.info(f"根据日期范围获取数据成功: {len(data)} 条")
            return data
            
        except Exception as e:
            logger.error(f"根据日期范围获取数据失败: {e}")
            return []
    
    def get_data_count(self) -> int:
        """
        获取数据总数
        
        Returns:
            int: 数据总数
        """
        try:
            collection = self.db[self.collection_name]
            count = collection.count_documents({})
            logger.info(f"数据总数: {count}")
            return count
            
        except Exception as e:
            logger.error(f"获取数据总数失败: {e}")
            return 0
    
    def delete_old_data(self, days: int = 30) -> int:
        """
        删除指定天数之前的旧数据
        
        Args:
            days: 保留天数
            
        Returns:
            int: 删除的数据条数
        """
        try:
            collection = self.db[self.collection_name]
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = collection.delete_many({
                "created_at": {"$lt": cutoff_date}
            })
            
            deleted_count = result.deleted_count
            logger.info(f"删除 {days} 天前的旧数据: {deleted_count} 条")
            return deleted_count
            
        except Exception as e:
            logger.error(f"删除旧数据失败: {e}")
            return 0
    
    def backup_to_json(self, file_path: str) -> bool:
        """
        备份数据到JSON文件
        
        Args:
            file_path: 备份文件路径
            
        Returns:
            bool: 备份是否成功
        """
        try:
            data = self.get_latest_data(limit=0)  # 获取所有数据
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据备份成功: {file_path}, 共 {len(data)} 条数据")
            return True
            
        except Exception as e:
            logger.error(f"数据备份失败: {e}")
            return False
    
    def restore_from_json(self, file_path: str) -> int:
        """
        从JSON文件恢复数据
        
        Args:
            file_path: 备份文件路径
            
        Returns:
            int: 恢复的数据条数
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                logger.error("备份文件格式错误，应为数组格式")
                return 0
            
            success_count = self.insert_batch_data(data)
            logger.info(f"数据恢复完成: {success_count}/{len(data)} 条数据成功")
            return success_count
            
        except Exception as e:
            logger.error(f"数据恢复失败: {e}")
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            collection = self.db[self.collection_name]
            
            stats = {
                "total_documents": collection.count_documents({}),
                "database_name": self.database_name,
                "collection_name": self.collection_name,
                "indexes": list(collection.list_indexes()),
                "latest_issue": None,
                "oldest_issue": None
            }
            
            # 获取最新和最旧的期号
            latest = collection.find_one(sort=[("issue", DESCENDING)])
            if latest:
                stats["latest_issue"] = latest.get("issue")
            
            oldest = collection.find_one(sort=[("issue", ASCENDING)])
            if oldest:
                stats["oldest_issue"] = oldest.get("issue")
            
            logger.info("获取数据库统计信息成功")
            return stats
            
        except Exception as e:
            logger.error(f"获取数据库统计信息失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        try:
            if self.client:
                self.client.close()
                logger.info("MongoDB连接已关闭")
        except Exception as e:
            logger.error(f"关闭MongoDB连接失败: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


def main():
    """测试MongoDB连接和基本操作"""
    try:
        # 从环境变量加载配置
        from dotenv import load_dotenv
        load_dotenv()
        
        # 创建数据库管理器
        with MongoDBManager() as db_manager:
            # 测试连接
            if db_manager.test_connection():
                print("✅ MongoDB连接测试成功")
                
                # 获取统计信息
                stats = db_manager.get_database_stats()
                print(f"📊 数据库统计信息:")
                print(f"   - 数据库名: {stats.get('database_name')}")
                print(f"   - 集合名: {stats.get('collection_name')}")
                print(f"   - 文档总数: {stats.get('total_documents')}")
                print(f"   - 最新期号: {stats.get('latest_issue')}")
                print(f"   - 最旧期号: {stats.get('oldest_issue')}")
                
                # 测试插入数据
                test_data = {
                    "issue": "test_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
                    "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "timestamp": datetime.now().isoformat()
                }
                
                if db_manager.insert_data(test_data):
                    print("✅ 测试数据插入成功")
                else:
                    print("❌ 测试数据插入失败")
                
                # 获取最新数据
                latest_data = db_manager.get_latest_data(limit=5)
                print(f"📋 最新5条数据:")
                for i, data in enumerate(latest_data, 1):
                    print(f"   {i}. 期号: {data.get('issue')}, 号码: {data.get('numbers')}")
            
            else:
                print("❌ MongoDB连接测试失败")
                
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")


if __name__ == "__main__":
    main()