"""
数据库升级：支持多商品来源
"""
import sqlite3
from config import Config

def upgrade():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    c = conn.cursor()
    
    print('🔄 升级数据库...')
    
    # 检查字段是否存在
    c.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in c.fetchall()]
    
    # 添加 source_name 字段
    if 'source_name' not in columns:
        print('  添加 source_name 字段')
        c.execute('ALTER TABLE products ADD COLUMN source_name TEXT DEFAULT "TG💎直登+协议+api 百万库存"')
    
    # 添加 source_bot 字段
    if 'source_bot' not in columns:
        print('  添加 source_bot 字段')
        c.execute('ALTER TABLE products ADD COLUMN source_bot TEXT DEFAULT "@hao24bot"')
    
    # 添加 buyer_session 字段
    if 'buyer_session' not in columns:
        print('  添加 buyer_session 字段')
        c.execute('ALTER TABLE products ADD COLUMN buyer_session TEXT DEFAULT "sessions/buyer_account"')
    
    conn.commit()
    conn.close()
    
    print('✅ 数据库升级完成')

if __name__ == '__main__':
    upgrade()
