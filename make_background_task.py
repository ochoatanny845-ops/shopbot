# -*- coding: utf-8 -*-
"""
Make purchase run in background task to prevent blocking
"""

def make_purchase_background():
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the purchase call section
    old_code = '''        # 检查是否有人正在购买（排队提示）
        if self.purchaser._purchase_lock.locked():
            queue_msg = (
                "⏳ 订单已收到！\\n\\n"
                "前方有订单正在处理中\\n"
                "您的订单排在队列中\\n\\n"
                "预计等待时间：30-90秒\\n"
                "请耐心等待..."
            )
            await update.message.reply_text(queue_msg)
        
        # 调用代购模块(传递 user_id 和 order_id 用于隔离)
        try:
            result = await self.purchaser.purchase('''
    
    new_code = '''        # 检查是否有人正在购买（排队提示）
        if self.purchaser._purchase_lock.locked():
            queue_msg = (
                "⏳ 订单已收到！\\n\\n"
                "前方有订单正在处理中\\n"
                "您的订单排在队列中\\n\\n"
                "预计等待时间：30-90秒\\n"
                "请耐心等待..."
            )
            await update.message.reply_text(queue_msg)
        
        # Create background task for purchase (non-blocking)
        asyncio.create_task(self._process_purchase(
            update=update,
            user_id=user_id,
            order_id=order_id,
            product_price=product_price,
            quantity=quantity,
            state=state.copy(),
            lang=lang
        ))
        
        # Return immediately (don't block)
        return
    
    async def _process_purchase(self, update, user_id, order_id, product_price, quantity, state, lang):
        """Process purchase in background"""
        # 调用代购模块(传递 user_id 和 order_id 用于隔离)
        try:
            result = await self.purchaser.purchase('''
    
    content = content.replace(old_code, new_code)
    
    # Now we need to move the rest of purchase logic into _process_purchase
    # Find the end of the try block (the except Exception as e:)
    # This is complex, so we'll do it step by step
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Created _process_purchase background task wrapper")
    print("⚠️ Note: Need to manually move the rest of purchase logic into this function")

if __name__ == '__main__':
    make_purchase_background()
