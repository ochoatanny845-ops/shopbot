"""
Database upgrade script: Add multi-source support
"""
import sys
import sqlite3
from config import Config

# Fix Windows console encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def upgrade():
    """Upgrade database"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    c = conn.cursor()
    
    print('Upgrading database...')
    
    # Check if columns exist
    c.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in c.fetchall()]
    
    if 'source_name' not in columns:
        print('  Adding source_name column...')
        c.execute('ALTER TABLE products ADD COLUMN source_name TEXT DEFAULT "TG Direct Login+Protocol+API"')
    else:
        print('  source_name column exists, skipping')
    
    if 'source_bot' not in columns:
        print('  Adding source_bot column...')
        c.execute('ALTER TABLE products ADD COLUMN source_bot TEXT')
    else:
        print('  source_bot column exists, skipping')
    
    if 'buyer_session' not in columns:
        print('  Adding buyer_session column...')
        c.execute('ALTER TABLE products ADD COLUMN buyer_session TEXT')
    else:
        print('  buyer_session column exists, skipping')
    
    if 'source_product_id' not in columns:
        print('  Adding source_product_id column...')
        c.execute('ALTER TABLE products ADD COLUMN source_product_id TEXT UNIQUE')
    else:
        print('  source_product_id column exists, skipping')
    
    conn.commit()
    conn.close()
    
    print('Database upgrade complete!')

if __name__ == '__main__':
    upgrade()
