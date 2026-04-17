# -*- coding: utf-8 -*-
"""
优化用户可见文案 + 添加排队提示功能
"""

def optimize_user_messages():
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 修改处理中消息（"正在打包账号检查中"）
    old_processing = 'f"{get_text(\'checking_accounts\', lang)}"'
    new_processing = '"正在打包账号检查中...\\n请稍候，最多2分钟"'
    content = content.replace(old_processing, new_processing)
    
    # 2. 修改成功消息（"账号文件已打包完成"）
    # Find the success message section
    old_success_1 = 'f"{get_text(\'purchase_success\', lang)}\\n\\n"'
    new_success_1 = '"✅ 购买成功！\\n\\n📦 账号文件已打包完成\\n正在为您整理交付...\\n\\n"'
    content = content.replace(old_success_1, new_success_1)
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Optimized user-facing messages in bot.py")

def add_queue_notification():
    """添加排队提示到purchaser.py"""
    with open('purchaser.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the purchase function and add queue check
    insert_idx = None
    for i, line in enumerate(lines):
        if 'async with AutoPurchaser._purchase_lock:' in line:
            insert_idx = i
            break
    
    if not insert_idx:
        print("Could not find insertion point")
        return
    
    # Insert queue notification before acquiring lock
    queue_check = [
        '        # Check if someone is purchasing (queue notification)\n',
        '        if AutoPurchaser._purchase_lock.locked():\n',
        '            print(f"[QUEUE] Order #{order_id} is waiting (another order in progress)")\n',
        '            # Note: In a full implementation, send Telegram message to user here\n',
        '            # For now, just log it\n',
        '        \n',
    ]
    
    lines = lines[:insert_idx] + queue_check + lines[insert_idx:]
    
    with open('purchaser.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("Added queue notification to purchaser.py")

if __name__ == '__main__':
    optimize_user_messages()
    add_queue_notification()
    print("Done!")
