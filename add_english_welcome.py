#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复欢迎词翻译 - 支持中英文欢迎词
方案：在数据库中添加 start_message_en，代码中根据语言选择
"""

import sqlite3

# 中文欢迎词（当前数据库中的）
chinese_welcome = """🔥首次购买建议少量测试，避免造成不必要的误会！
⚠️购买须知： 所有账户发货之前都会检查存活，出现死号自动退款！
‼️如果出现冻结情况 以发货时间为准！
‼️请在30分钟内联系客服处理，超时则默认放弃售后！"""

# 英文翻译
english_welcome = """🔥 First-time buyers are advised to test with a small quantity to avoid unnecessary misunderstandings!
⚠️ Purchase Notice: All accounts are checked for validity before delivery. Dead accounts are automatically refunded!
‼️ In case of account freeze, the delivery time shall prevail!
‼️ Please contact customer service within 30 minutes, otherwise after-sales support will be forfeited!"""

# 连接数据库
conn = sqlite3.connect('shopbot.db')
c = conn.cursor()

# 检查是否已有英文欢迎词
c.execute("SELECT value FROM settings WHERE key = 'start_message_en'")
existing = c.fetchone()

if existing:
    print('[SKIP] 英文欢迎词已存在')
else:
    # 添加英文欢迎词
    c.execute('''
        INSERT INTO settings (key, value)
        VALUES ('start_message_en', ?)
    ''', (english_welcome,))
    
    conn.commit()
    print('[OK] 已添加英文欢迎词到数据库')

conn.close()

print('\n现在需要修改 bot.py 代码:')
print('将 Line 914 改为根据语言选择欢迎词')
