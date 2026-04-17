# -*- coding: utf-8 -*-
"""
Simplify main menu - remove product_overview intermediate layer
"""

def simplify_main_menu():
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Remove show_product_overview callback handling
    content = content.replace(
        '''        if data == "show_product_overview":
            await self._show_product_overview(query)
        elif data == "show_categories":''',
        '''        if data == "show_categories":'''
    )
    
    # 2. Find and replace main menu button layout
    # Original: btn_products button that goes to product_overview
    # New: Three category buttons directly
    
    old_menu = '''        keyboard = [
            [InlineKeyboardButton(get_text('btn_products', lang), callback_data='show_product_overview')],'''
    
    new_menu = '''        keyboard = [
            [InlineKeyboardButton('TG Tdada|session|api', callback_data='cat_tdata+session+api')],
            [InlineKeyboardButton('TG session only', callback_data='cat_session')],
            [InlineKeyboardButton('TG Tdada only', callback_data='cat_tdata')],'''
    
    content = content.replace(old_menu, new_menu)
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Simplified main menu")

if __name__ == '__main__':
    simplify_main_menu()
