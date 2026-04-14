"""
通过 ID 发送消息
"""
import asyncio
import sys
from telethon import TelegramClient
from telethon.tl.types import InputPeerUser

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')

# 配置
API_ID = 2040
API_HASH = 'b18441a1ff607e10a989891a5462e627'
SESSION_FILE = 'sessions/447308244502'
YOUR_ID = 5991190607

async def send_hello():
    """通过 ID 发送消息"""
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        await client.start()
        print('✅ 登录成功！')
        
        # 获取当前账号信息
        me = await client.get_me()
        print(f'📱 当前账号: {me.first_name} - ID: {me.id}')
        
        # 直接用 ID 发送消息
        await client.send_message(YOUR_ID, '你好我来了')
        print(f'✅ 消息已发送给 ID: {YOUR_ID}')
        
    except Exception as e:
        print(f'❌ 错误: {e}')
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(send_hello())
