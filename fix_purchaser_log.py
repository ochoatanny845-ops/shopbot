# -*- coding: utf-8 -*-
"""
在purchaser.py中添加"订单开始处理"的打印
"""

with open('purchaser.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the lock acquisition message
old_msg = "print(f'🔒 订单 #{order_id} (用户 {user_id}) 开始处理...')"
new_msg = "print(f'[LOCK] Order #{order_id} (User {user_id}) processing...')"

content = content.replace(old_msg, new_msg)

with open('purchaser.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated purchaser.py log messages")
