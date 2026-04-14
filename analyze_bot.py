"""
访问 @HaoweiShopBot 分析商品结构
"""
import asyncio
import sys
import json
from telethon import TelegramClient

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')

# 配置 - 使用第一个 session
API_ID = 2040
API_HASH = 'b18441a1ff607e10a989891a5462e627'
SESSION_FILE = 'sessions/new/573166025225'
BOT_USERNAME = 'hao24bot'  # 正确的用户名

async def analyze_bot():
    """分析源机器人"""
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        # 登录时可能需要2FA密码
        await client.start(password='600')  # 从JSON文件读取的2FA密码
        
        me = await client.get_me()
        print(f'✅ 登录成功！')
        print(f'📱 当前账号: {me.first_name} - ID: {me.id}')
        print(f'\n' + '='*60)
        
        # 访问机器人
        print(f'\n🤖 正在访问 @{BOT_USERNAME}...\n')
        
        # 发送 /start
        await client.send_message(BOT_USERNAME, '/start')
        await asyncio.sleep(3)
        
        # 获取最新消息
        messages = await client.get_messages(BOT_USERNAME, limit=5)
        
        for idx, msg in enumerate(messages):
            print(f'\n📨 消息 {idx + 1}:')
            print(f'  时间: {msg.date}')
            
            if msg.text:
                print(f'  文本: {msg.text[:200]}...' if len(msg.text) > 200 else f'  文本: {msg.text}')
            
            if msg.buttons:
                print(f'\n  🔘 按钮列表:')
                for row_idx, row in enumerate(msg.buttons):
                    print(f'    第{row_idx + 1}行:')
                    for btn in row:
                        btn_text = btn.text if hasattr(btn, 'text') else ''
                        btn_data = btn.data.decode() if hasattr(btn, 'data') and btn.data else 'URL按钮'
                        print(f'      - "{btn_text}" → {btn_data}')
            
            print(f'  {"-"*50}')
        
        # 如果有按钮，尝试点击第一个
        if messages[0].buttons:
            first_btn = messages[0].buttons[0][0]
            print(f'\n🖱️ 点击第一个按钮: "{first_btn.text}"')
            await first_btn.click()
            await asyncio.sleep(3)
            
            # 获取点击后的消息
            new_messages = await client.get_messages(BOT_USERNAME, limit=3)
            
            print(f'\n📨 点击后的消息:')
            for idx, msg in enumerate(new_messages):
                if msg.text:
                    print(f'\n  消息 {idx + 1}:')
                    print(f'    文本: {msg.text[:200]}...' if len(msg.text) > 200 else f'    文本: {msg.text}')
                
                if msg.buttons:
                    print(f'\n    🔘 按钮列表:')
                    for row_idx, row in enumerate(msg.buttons):
                        for btn in row:
                            btn_text = btn.text if hasattr(btn, 'text') else ''
                            btn_data = btn.data.decode() if hasattr(btn, 'data') and btn.data else 'URL'
                            print(f'      - "{btn_text}" → {btn_data}')
        
        print(f'\n' + '='*60)
        print(f'\n✅ 分析完成！')
        
    except Exception as e:
        print(f'\n❌ 错误: {e}')
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(analyze_bot())
