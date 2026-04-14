from database import Database

db = Database()
print('数据库初始化完成')

conn = db.get_connection()
c = conn.cursor()
c.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [r[0] for r in c.fetchall()]
print('表列表:', tables)

if 'users' in tables:
    c.execute('SELECT user_id, balance FROM users')
    users = c.fetchall()
    print('用户列表:')
    for u in users:
        print(f'  ID: {u[0]}, 余额: ${u[1]:.2f}')

conn.close()
