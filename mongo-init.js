// MongoDB初始化脚本
// 创建台湾PK10数据库和用户

// 切换到taiwan_pk10数据库
db = db.getSiblingDB('taiwan_pk10');

// 创建应用用户
db.createUser({
  user: 'pk10_user',
  pwd: 'pk10pass123',  // 在生产环境中应该使用环境变量
  roles: [
    {
      role: 'readWrite',
      db: 'taiwan_pk10'
    }
  ]
});

// 创建集合和索引
db.createCollection('taiwan_pk10_data');

// 创建索引以优化查询性能
db.taiwan_pk10_data.createIndex({ "period": -1 });
db.taiwan_pk10_data.createIndex({ "drawDate": -1 });
db.taiwan_pk10_data.createIndex({ "drawTime": -1 });
db.taiwan_pk10_data.createIndex({ "scrapedAt": -1 });
db.taiwan_pk10_data.createIndex({ "drawDate": -1, "period": -1 });

// 创建TTL索引，自动清理90天前的数据（可选）
// db.taiwan_pk10_data.createIndex({ "scrapedAt": 1 }, { expireAfterSeconds: 7776000 });

print('MongoDB初始化完成：');
print('- 数据库: taiwan_pk10');
print('- 用户: pk10_user');
print('- 集合: taiwan_pk10_data');
print('- 索引: 已创建性能优化索引');
print('初始化脚本执行成功！');