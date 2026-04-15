"""
添加 OKPay 订单表
"""
import sqlite3

def upgrade_database():
    """升级数据库：添加 OKPay 订单表"""
    conn = sqlite3.connect('shopbot.db')
    c = conn.cursor()
    
    # 创建 OKPay 订单表
    c.execute('''
        CREATE TABLE IF NOT EXISTS okpay_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            unique_id TEXT UNIQUE NOT NULL,
            okpay_order_id TEXT,
            amount REAL NOT NULL,
            actual_amount REAL,
            coin TEXT DEFAULT 'USDT',
            pay_user_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # 创建索引
    c.execute('CREATE INDEX IF NOT EXISTS idx_okpay_user ON okpay_orders(user_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_okpay_unique ON okpay_orders(unique_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_okpay_status ON okpay_orders(status)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_okpay_order_id ON okpay_orders(okpay_order_id)')
    
    conn.commit()
    conn.close()
    
    print('✅ 数据库升级完成：已添加 OKPay 订单表')

if __name__ == '__main__':
    upgrade_database()
