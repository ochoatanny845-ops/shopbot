"""
添加用户语言字段
Add user language field
"""
import sqlite3

def upgrade_database():
    """添加 language 字段到 users 表"""
    conn = sqlite3.connect('shopbot.db')
    c = conn.cursor()
    
    # 检查字段是否已存在
    c.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in c.fetchall()]
    
    if 'language' not in columns:
        print('[INFO] Adding language field to users table...')
        c.execute('ALTER TABLE users ADD COLUMN language TEXT DEFAULT NULL')
        conn.commit()
        print('[OK] Language field added successfully!')
    else:
        print('[INFO] Language field already exists.')
    
    conn.close()

if __name__ == '__main__':
    upgrade_database()
