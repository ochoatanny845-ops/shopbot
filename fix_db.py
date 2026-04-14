import sqlite3
import sys

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('shopbot.db')
c = conn.cursor()

# 创建用户表
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        balance REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# 检查是否有用户 5991190607
c.execute('SELECT user_id, balance FROM users WHERE user_id = 5991190607')
user = c.fetchone()

if user:
    print(f'用户已存在 - ID: {user[0]}, 余额: ${user[1]:.2f}')
else:
    print('用户不存在，正在创建...')
    c.execute('''
        INSERT INTO users (user_id, username, first_name, balance)
        VALUES (5991190607, 'luoshen00', '洛神', 600.00)
    ''')
    print('用户创建成功，余额: $600.00')

conn.commit()
conn.close()
print('数据库初始化完成')
