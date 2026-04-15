"""
完整修复所有充值相关的数据库表
"""
import sqlite3

def fix_all_recharge_tables():
    """创建/修复所有充值相关的表"""
    conn = sqlite3.connect('shopbot.db')
    c = conn.cursor()
    
    # 1. 创建 recharge_orders 表
    print('[INFO] Creating recharge_orders table...')
    c.execute('''
        CREATE TABLE IF NOT EXISTS recharge_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            address TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            tx_hash TEXT
        )
    ''')
    
    # 2. 创建 okpay_orders 表
    print('[INFO] Creating okpay_orders table...')
    c.execute('''
        CREATE TABLE IF NOT EXISTS okpay_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            unique_id TEXT UNIQUE NOT NULL,
            amount REAL NOT NULL,
            coin TEXT DEFAULT 'USDT',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            tx_hash TEXT,
            okpay_order_id TEXT
        )
    ''')
    
    # 3. 创建 balance_logs 表（如果不存在）
    print('[INFO] Creating balance_logs table...')
    c.execute('''
        CREATE TABLE IF NOT EXISTS balance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # 检查所有表
    tables = ['recharge_orders', 'okpay_orders', 'balance_logs']
    
    for table in tables:
        c.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in c.fetchall()]
        print(f'[OK] {table}: {", ".join(columns)}')
    
    conn.close()
    print('[OK] All recharge tables fixed!')

if __name__ == '__main__':
    fix_all_recharge_tables()
