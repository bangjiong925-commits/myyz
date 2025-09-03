#!/usr/bin/env python3
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['taiwan_pk10']
collection = db['lottery_data']

# 检查数据库总体情况
total_count = collection.count_documents({})
print(f'数据库总记录数: {total_count}')

# 获取最新10条记录
latest = list(collection.find().sort('period', -1).limit(10))
print('\n最新10条记录:')
for i, record in enumerate(latest):
    print(f'  {i+1}. 期号: {record["period"]}, 日期: {record.get("draw_date", "N/A")}')

# 获取最早10条记录
earliest = list(collection.find().sort('period', 1).limit(10))
print('\n最早10条记录:')
for i, record in enumerate(earliest):
    print(f'  {i+1}. 期号: {record["period"]}, 日期: {record.get("draw_date", "N/A")}')

# 检查指定期号范围的数据
start_period = 114049736
end_period = 114049883

count = collection.count_documents({
    'period': {'$gte': start_period, '$lte': end_period}
})

print(f'\n期号{start_period}-{end_period}范围内的记录数: {count}')

# 如果没有找到，检查最接近的记录
if count == 0:
    print('\n没有找到指定范围内的记录，检查最接近的记录:')
    
    # 找到小于起始期号的最大期号
    before_cursor = collection.find({'period': {'$lt': start_period}}).sort('period', -1).limit(1)
    before_list = list(before_cursor)
    if before_list:
        print(f'小于{start_period}的最大期号: {before_list[0]["period"]}')
    
    # 找到大于结束期号的最小期号
    after_cursor = collection.find({'period': {'$gt': end_period}}).sort('period', 1).limit(1)
    after_list = list(after_cursor)
    if after_list:
        print(f'大于{end_period}的最小期号: {after_list[0]["period"]}')
    
    # 检查今天最新的148条数据
    print('\n今天最新的148条数据:')
    latest_148 = list(collection.find().sort('period', -1).limit(148))
    if latest_148:
        print(f'最新148条数据期号范围: {latest_148[-1]["period"]} - {latest_148[0]["period"]}')
        print(f'实际条数: {len(latest_148)}')
else:
    # 获取这个范围内的所有记录
    records = list(collection.find({
        'period': {'$gte': start_period, '$lte': end_period}
    }).sort('period', 1))
    
    print(f'实际找到的记录数: {len(records)}')
    print('期号列表:')
    for i, record in enumerate(records):
        print(f'  {i+1}. {record["period"]}')

client.close()