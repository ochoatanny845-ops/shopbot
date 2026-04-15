"""
添加充值订单表
"""
import sqlite3

def upgrade_database():
    """升级数据库：添加充值订单表"""
    conn = sqlite3.connect('shopbot.db')
    c = conn.cursor()
    
    # 创建充值订单表
    c.execute('''
        CREATE TABLE IF NOT EXISTS recharge_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            actual_amount REAL,
            txid TEXT UNIQUE,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id)
        )
    ''')
    
    # 创建索引
    c.execute('CREATE INDEX IF NOT EXISTS idx_recharge_user ON recharge_orders(user_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_recharge_status ON recharge_orders(status)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_recharge_txid ON recharge_orders(txid)')
    
    conn.commit()
    conn.close()
    
    print('✅ 数据库升级完成：已添加充值订单表')

if __name__ == '__main__':
    upgrade_database()
