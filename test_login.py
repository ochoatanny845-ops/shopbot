"""
测试登录并发送消息
"""
import asyncio
import sys
from telethon import TelegramClient

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')

# 配置
API_ID = 2040
API_HASH = 'b18441a1ff607e10a989891a5462e627'
SESSION_FILE = 'sessions/447308244502'
YOUR_USER_ID = 5991190607  # 洛神的用户ID

async def test_login():
    """测试登录并发送消息"""
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        await client.start()
        print('✅ 登录成功！')
        
        # 获取当前账号信息
        me = await client.get_me()
        print(f'📱 当前账号: {me.first_name} (@{me.username}) - ID: {me.id}')
        
        # 给你发送测试消息
        # 先获取对话列表，确保实体存在
        dialogs = await client.get_dialogs(limit=100)
        print(f'📋 找到 {len(dialogs)} 个对话')
        
        # 查找你的对话
        target = None
        for dialog in dialogs:
            if dialog.entity.id == YOUR_USER_ID:
                target = dialog.entity
                break
        
        if target:
            await client.send_message(target, '🤖 **测试消息**\n\n海棠已成功登录代购账号！\n\n📱 账号信息：\n- 名称：Truda Turner\n- ID：8660382480\n\n✅ 可以开始访问源机器人了！')
            print(f'✅ 已发送测试消息给你！')
        else:
            print(f'⚠️ 未找到你的对话，尝试直接发送...')
            await client.send_message(YOUR_USER_ID, '🤖 测试消息：海棠已登录代购账号！')
            print(f'✅ 已发送测试消息！')
        
    except Exception as e:
        print(f'❌ 登录失败: {e}')
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(test_login())
