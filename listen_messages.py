"""
监听新消息并自动回复
"""
import asyncio
import sys
from telethon import TelegramClient, events

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')

# 配置
API_ID = 2040
API_HASH = 'b18441a1ff607e10a989891a5462e627'
SESSION_FILE = 'sessions/447308244502'

async def listen_and_reply():
    """监听新消息并自动回复"""
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    await client.start()
    me = await client.get_me()
    print(f'✅ 登录成功！')
    print(f'📱 当前账号: {me.first_name} - ID: {me.id}')
    print(f'👂 开始监听消息...')
    
    @client.on(events.NewMessage(incoming=True))
    async def handle_new_message(event):
        """处理新消息"""
        sender = await event.get_sender()
        print(f'\n📩 收到消息:')
        print(f'  发送者: {sender.first_name} (ID: {sender.id})')
        print(f'  内容: {event.text}')
        
        # 自动回复
        await event.reply('你好我来了 ✅')
        print(f'  ✅ 已回复！')
    
    print('\n等待消息中...')
    print('按 Ctrl+C 停止\n')
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(listen_and_reply())
