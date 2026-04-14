"""
测试新的 session 并监听消息
"""
import asyncio
import sys
from telethon import TelegramClient, events

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')

# 配置
API_ID = 2040
API_HASH = 'b18441a1ff607e10a989891a5462e627'
SESSION_FILE = 'sessions/new/573165897374'

async def test_and_listen():
    """测试登录并监听消息"""
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    await client.start()
    me = await client.get_me()
    print(f'✅ 登录成功！')
    print(f'📱 当前账号: {me.first_name} (@{me.username}) - ID: {me.id}')
    
    # 尝试给你发消息
    try:
        await client.send_message(5991190607, '你好我来了 ✅\n\n我已经成功登录这个账号了！')
        print(f'✅ 已发送测试消息给你！')
    except Exception as e:
        print(f'⚠️ 发送消息失败: {e}')
        print(f'👂 切换到监听模式，等你先发消息给我...')
    
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
    
    print(f'\n👂 开始监听消息...')
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(test_and_listen())
