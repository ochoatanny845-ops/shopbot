"""
重新初始化数据库（不删除现有用户数据）
"""
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = 'shopbot.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 商品表
c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_product_id TEXT UNIQUE,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        country TEXT,
        original_price REAL NOT NULL,
        selling_price REAL NOT NULL,
        stock INTEGER DEFAULT 0,
        description TEXT,
        button_data TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1
    )
''')
print("Created table: products")

# 订单表
c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER DEFAULT 1,
        unit_price REAL NOT NULL,
        total_price REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        files_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        error_message TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
''')
print("Created table: orders")

# 同步日志表
c.execute('''
    CREATE TABLE IF NOT EXISTS sync_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sync_type TEXT NOT NULL,
        products_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'running',
        error_message TEXT,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )
''')
print("Created table: sync_logs")

# 余额变动记录表
c.execute('''
    CREATE TABLE IF NOT EXISTS balance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        type TEXT NOT NULL,
        order_id INTEGER,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (order_id) REFERENCES orders(id)
    )
''')
print("Created table: balance_logs")

conn.commit()
conn.close()

print("\nDatabase initialization complete!")
print("All tables created. User data preserved.")
