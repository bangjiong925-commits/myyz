import pymongo
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

client = pymongo.MongoClient(os.getenv('MONGODB_URI'))
db = client['taiwan_pk10']
collection = db['lottery_data']

# 检查总记录数
total_count = collection.count_documents({})
print(f'数据库中总记录数: {total_count}')

# 检查最新记录
latest = list(collection.find().sort('_id', -1).limit(1))
print(f'最新记录: {latest}')

# 检查今天的数据
today = datetime.now().strftime('%Y-%m-%d')
print(f'今天日期: {today}')

# 查找今天的数据
today_data = list(collection.find({'draw_date': {'$regex': f'^{today}'}}))
print(f'今天的数据条数: {len(today_data)}')

if today_data:
    print(f'今天的数据: {today_data[:3]}')
else:
    print('今天没有数据')

# 检查最近几天的数据
recent_data = list(collection.find().sort('_id', -1).limit(10))
print(f'最近10条记录的日期:')
for record in recent_data:
    print(f"期号: {record.get('period')}, 日期: {record.get('draw_date')}, 时间: {record.get('draw_time')}")

client.close()