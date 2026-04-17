# -*- coding: utf-8 -*-
"""
Handle partial success in bot.py
"""

def handle_partial_success():
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the purchase success handling
    old_code = '''            files = await self.purchaser.purchase(
                product_id=state['product_id'],
                quantity=quantity,
                user_id=user_id,
                order_id=order_id
            )

            # 更新订单状态
            conn = self.db.get_connection()'''
    
    new_code = '''            result = await self.purchaser.purchase(
                product_id=state['product_id'],
                quantity=quantity,
                user_id=user_id,
                order_id=order_id
            )
            
            # Handle result (dict or list for backward compatibility)
            if isinstance(result, dict):
                files = result['files']
                requested_qty = result['requested_quantity']
                actual_qty = result['actual_quantity']
            else:
                files = result
                requested_qty = quantity
                actual_qty = quantity
            
            # Partial success: refund difference
            if actual_qty < requested_qty:
                refund_qty = requested_qty - actual_qty
                refund_amount = product_price * refund_qty
                
                conn = self.db.get_connection()
                c = conn.cursor()
                c.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (refund_amount, user_id))
                c.execute("INSERT INTO balance_logs (user_id, amount, type, order_id, notes) VALUES (?, ?, 'refund', ?, ?)",
                          (user_id, refund_amount, order_id, f'Partial refund: {refund_qty} items'))
                conn.commit()
                conn.close()
                
                print(f'[INFO] Partial success: refunded {refund_amount:.2f} USDT for {refund_qty} items')

            # 更新订单状态
            conn = self.db.get_connection()'''
    
    content = content.replace(old_code, new_code)
    
    # Update success message to show actual quantity
    old_msg = '''            await update.message.reply_text(
                f"{get_text('purchase_success', lang)}\\n\\n"'''
    
    new_msg = '''            # Success message (show partial info if applicable)
            success_msg = f"{get_text('purchase_success', lang)}\\n\\n"
            if actual_qty < requested_qty:
                success_msg += f"[WARN] Partial success: {actual_qty}/{requested_qty} items\\n"
                success_msg += f"Refunded: ${product_price * (requested_qty - actual_qty):.2f}\\n\\n"
            
            await update.message.reply_text(
                success_msg +'''
    
    content = content.replace(old_msg, new_msg)
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Added partial success handling to bot.py")

if __name__ == '__main__':
    handle_partial_success()
