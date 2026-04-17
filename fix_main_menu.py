# -*- coding: utf-8 -*-
"""
Fix main menu: show single button with stock count
"""

def fix_main_menu():
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Restore original main menu layout with stock count
    old_menu = '''        keyboard = [
            [InlineKeyboardButton('TG Tdada|session|api', callback_data='cat_tdata+session+api')],
            [InlineKeyboardButton('TG session only', callback_data='cat_session')],
            [InlineKeyboardButton('TG Tdada only', callback_data='cat_tdata')],'''
    
    new_menu = '''        # Get total stock count
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute('SELECT SUM(stock) FROM products WHERE is_active = 1')
        total_stock = c.fetchone()[0] or 0
        conn.close()
        
        keyboard = [
            [InlineKeyboardButton(f'TG✈️ Tdada｜session｜api ({total_stock})', callback_data='show_product_overview')],'''
    
    content = content.replace(old_menu, new_menu)
    
    # Restore show_product_overview callback
    old_callback = '''        if data == "show_categories":'''
    
    new_callback = '''        if data == "show_product_overview":
            await self._show_product_overview(query)
        elif data == "show_categories":'''
    
    content = content.replace(old_callback, new_callback)
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed main menu")

if __name__ == '__main__':
    fix_main_menu()
