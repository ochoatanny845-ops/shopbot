# -*- coding: utf-8 -*-
"""
Remove product_overview layer - go directly to categories
"""

def remove_product_overview():
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Change main menu button to go directly to categories
    old_btn = "callback_data='show_product_overview'"
    new_btn = "callback_data='show_categories'"
    
    content = content.replace(old_btn, new_btn)
    
    # Remove show_product_overview callback handling
    old_callback = '''        if data == "show_product_overview":
            await self._show_product_overview(query)
        elif data == "show_categories":'''
    
    new_callback = '''        if data == "show_categories":'''
    
    content = content.replace(old_callback, new_callback)
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Removed product_overview layer")

if __name__ == '__main__':
    remove_product_overview()
