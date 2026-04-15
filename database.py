"""
数据库模块
"""
import sqlite3
import os
from datetime import datetime
from config import Config

class Database:
    """数据库管理类"""
    
    # 类变量：记录是否已初始化过
    _initialized = False
    
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
        
        # 系统配置表
        c.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 初始化默认配置
        c.execute('''
            INSERT OR IGNORE INTO settings (key, value, updated_at)
            VALUES 
                ('trc20_address', 'TV77o3KfH8DkQNNEsvDLNo765ABcqr3MnM', datetime('now')),
                ('start_message', '👋 欢迎使用账号购买系统！\n\n🛍 请选择服务：', datetime('now'))
        ''')
        
        conn.commit()
        conn.close()
        
        # 只在第一次初始化时打印
        if not Database._initialized:
            print('✅ 数据库初始化完成')
            Database._initialized = True
    
    def get_setting(self, key: str, default: str = None) -> str:
        """获取配置项"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = c.fetchone()
        conn.close()
        
        return result[0] if result else default
    
    def set_setting(self, key: str, value: str):
        """设置配置项"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, datetime('now'))
        ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> dict:
        """获取平台统计数据"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # 用户总数
        c.execute('SELECT COUNT(*) FROM users')
        total_users = c.fetchone()[0]
        
        # 平台余额
        c.execute('SELECT SUM(balance) FROM users')
        total_balance = c.fetchone()[0] or 0
        
        # 今日收入
        c.execute('''
            SELECT SUM(amount) FROM balance_logs
            WHERE type = 'recharge'
            AND date(created_at) = date('now')
        ''')
        today_income = c.fetchone()[0] or 0
        
        # 昨日收入
        c.execute('''
            SELECT SUM(amount) FROM balance_logs
            WHERE type = 'recharge'
            AND date(created_at) = date('now', '-1 day')
        ''')
        yesterday_income = c.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_balance': total_balance,
            'today_income': today_income,
            'yesterday_income': yesterday_income
        }
