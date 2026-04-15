"""
修复 OKPay 数据库表
"""
import sqlite3

def upgrade_okpay_table():
    """创建或修复 okpay_orders 表"""
    conn = sqlite3.connect('shopbot.db')
    c = conn.cursor()

    # 创建 okpay_orders 表
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
            tx_hash TEXT
        )
    ''')

    conn.commit()

    # 检查表是否存在所有必需的列
    c.execute("PRAGMA table_info(okpay_orders)")
    columns = [row[1] for row in c.fetchall()]

    print(f'[OK] okpay_orders table created/fixed')
    print(f'[INFO] Current columns: {", ".join(columns)}')
    
    # 如果缺少字段,添加它们
    required_columns = {
        'unique_id': 'TEXT UNIQUE',
        'coin': 'TEXT DEFAULT "USDT"',
        'tx_hash': 'TEXT',
        'completed_at': 'TIMESTAMP',
        'okpay_order_id': 'TEXT'
    }
    
    for col, col_type in required_columns.items():
        if col not in columns:
            try:
                c.execute(f'ALTER TABLE okpay_orders ADD COLUMN {col} {col_type}')
                print(f'[OK] Added column: {col}')
            except sqlite3.OperationalError as e:
                print(f'[WARN] Column {col} already exists or cannot be added: {e}')
    
    conn.commit()
    conn.close()
    
    print('[OK] OKPay database fix complete!')

if __name__ == '__main__':
    upgrade_okpay_table()
