# -*- coding: utf-8 -*-
"""
Fix back button in categories page
"""

with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the back button in _show_categories
old_line = '''        keyboard.append([InlineKeyboardButton(get_text('btn_back', lang), callback_data="show_product_overview")])'''
new_line = '''        keyboard.append([InlineKeyboardButton(get_text('btn_back', lang), callback_data="back_main")])'''

content = content.replace(old_line, new_line)

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed back button in categories page")
