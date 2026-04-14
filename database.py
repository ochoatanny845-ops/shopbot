"""
数据库模块
"""
import sqlite3
from datetime import datetime
from config import Config

class Database:
    """数据库管理类"""
    
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """初始化数据库"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # 检查数据库文件是否损坏
        try:
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in c.fetchall()]
        except Exception as e:
            print(f'⚠️ 数据库损坏，正在重建: {e}')
            conn.close()
            # 删除损坏的数据库
            import os
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            # 重新连接
            conn = self.get_connection()
            c = conn.cursor()
            tables = []
        
        # 用户表
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
        
        conn.commit()
        
        # 验证数据库
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]
        required_tables = ['users', 'products', 'orders', 'sync_logs', 'balance_logs']
        
        if all(t in tables for t in required_tables):
            print('✅ 数据库初始化完成')
        else:
            print(f'⚠️ 数据库表不完整，缺少: {set(required_tables) - set(tables)}')
        
        conn.close()
