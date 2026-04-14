import sqlite3
import sys

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('shopbot.db')
c = conn.cursor()

# Check tables
print("===== Database Tables =====")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
for table in tables:
    print(f"Table: {table[0]}")

print("\n===== User 5991190607 Info =====")
c.execute("SELECT user_id, username, balance, created_at FROM users WHERE user_id = 5991190607")
user = c.fetchone()
if user:
    print(f"User ID: {user[0]}")
    print(f"Username: {user[1]}")
    print(f"Balance: ${user[2]}")
    print(f"Created: {user[3]}")
else:
    print("User not found")

conn.close()
