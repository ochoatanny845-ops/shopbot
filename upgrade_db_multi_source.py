"""
数据库升级脚本：添加多商品来源支持
"""
import sqlite3
from config import Config

def upgrade():
    """升级数据库"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    c = conn.cursor()
    
    print('🔄 开始升级数据库...')
    
    # 检查是否已存在 source_name 字段
    c.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in c.fetchall()]
    
    if 'source_name' not in columns:
        print('  添加 source_name 字段...')
        c.execute('ALTER TABLE products ADD COLUMN source_name TEXT DEFAULT "TG💎直登+协议+api 百万库存"')
    else:
        print('  source_name 字段已存在，跳过')
    
    if 'source_bot' not in columns:
        print('  添加 source_bot 字段...')
        c.execute('ALTER TABLE products ADD COLUMN source_bot TEXT')
    else:
        print('  source_bot 字段已存在，跳过')
    
    if 'buyer_session' not in columns:
        print('  添加 buyer_session 字段...')
        c.execute('ALTER TABLE products ADD COLUMN buyer_session TEXT')
    else:
        print('  buyer_session 字段已存在，跳过')
    
    # 更新现有商品的来源信息（使用默认配置）
    print('  更新现有商品的来源信息...')
    c.execute('''
        UPDATE products
        SET source_bot = ?,
            buyer_session = ?
        WHERE source_bot IS NULL
    ''', (Config.SOURCE_BOT, Config.BUYER_SESSION))
    
    conn.commit()
    conn.close()
    
    print('✅ 数据库升级完成！')

if __name__ == '__main__':
    upgrade()
