# -*- coding: utf-8 -*-
"""
Add smart stock check to purchaser.py
"""

import re

def add_stock_check():
    with open('purchaser.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the purchase flow section (after click_product)
    insert_idx = None
    for i, line in enumerate(lines):
        if '# 2. 查找并点击商品' in line:
            # Insert after: await self._click_product(name)
            # Find next line after _click_product call
            for j in range(i, min(i+5, len(lines))):
                if 'await self._click_product(name)' in lines[j]:
                    insert_idx = j + 1
                    break
            break
    
    if not insert_idx:
        print("Could not find insertion point")
        return
    
    # Stock check code to insert
    stock_check_lines = [
        '                \n',
        '                # 2.5. Check actual stock on product page\n',
        '                available_stock = await self._check_available_stock()\n',
        '                original_quantity = quantity\n',
        '                \n',
        '                if available_stock == 0:\n',
        '                    raise Exception(f"Source bot out of stock: {name}")\n',
        '                \n',
        '                if available_stock < quantity:\n',
        '                    print(f"[WARN] Insufficient stock: requested {quantity}, actual {available_stock}, auto-adjusted")\n',
        '                    quantity = available_stock\n',
        '                \n',
    ]
    
    # Insert stock check
    lines = lines[:insert_idx] + stock_check_lines + lines[insert_idx:]
    
    # Update return value to include quantity info
    for i, line in enumerate(lines):
        if "return files" in line and "订单 #{order_id} 代购成功" in lines[i-2]:
            lines[i] = '                return {"files": files, "requested_quantity": original_quantity, "actual_quantity": quantity}\n'
            break
    
    # Add _check_available_stock function before _input_quantity
    func_insert_idx = None
    for i, line in enumerate(lines):
        if 'async def _input_quantity(self, quantity):' in line:
            func_insert_idx = i
            break
    
    if func_insert_idx:
        stock_func = '''    async def _check_available_stock(self):
        """Check actual stock from source bot product page"""
        msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
        
        if msgs and msgs[0].text:
            text = msgs[0].text
            
            # Match stock patterns
            stock_patterns = [
                r'当前库存[：:]\s*(\d+)',
                r'库存[：:]\s*(\d+)',
                r'[Ss]tock[：:]\s*(\d+)',
            ]
            
            for pattern in stock_patterns:
                match = re.search(pattern, text)
                if match:
                    stock = int(match.group(1))
                    print(f'[INFO] Stock detected: {stock}')
                    return stock
        
        # If not found, assume sufficient
        print('[WARN] Stock info not found, assuming sufficient')
        return 9999
    
'''
        lines.insert(func_insert_idx, stock_func)
    
    with open('purchaser.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("Added smart stock check to purchaser.py")

if __name__ == '__main__':
    add_stock_check()
