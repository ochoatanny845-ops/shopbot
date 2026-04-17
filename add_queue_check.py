# -*- coding: utf-8 -*-
"""
在bot.py中添加排队检测和通知
"""

def add_queue_check_in_bot():
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find where we call purchaser.purchase and add queue check before it
    old_call = '''        # 调用代购模块(传递 user_id 和 order_id 用于隔离)
        try:
            result = await self.purchaser.purchase('''
    
    new_call = '''        # 检查是否有人正在购买（排队提示）
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
    
    content = content.replace(old_call, new_call)
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Added queue check in bot.py")

if __name__ == '__main__':
    add_queue_check_in_bot()
