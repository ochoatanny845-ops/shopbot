"""
搜索用户并发送消息
"""
import asyncio
import sys
from telethon import TelegramClient
from telethon.tl.functions.contacts import SearchRequest

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')

# 配置
API_ID = 2040
API_HASH = 'b18441a1ff607e10a989891a5462e627'
SESSION_FILE = 'sessions/447308244502'

async def search_and_message():
    """搜索用户并发送消息"""
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        await client.start()
        print('✅ 登录成功！')
        
        # 获取当前账号信息
        me = await client.get_me()
        print(f'📱 当前账号: {me.first_name} - ID: {me.id}')
        
        # 搜索用户
        print('🔍 搜索 @luoshen00...')
        result = await client(SearchRequest(
            q='@luoshen00',
            limit=10
        ))
        
        print(f'搜索结果: {len(result.users)} 个用户, {len(result.chats)} 个群组')
        
        # 打印所有找到的用户
        for user in result.users:
            print(f'- {user.first_name} (@{user.username}) - ID: {user.id}')
            
            # 如果找到 luoshen00，发送消息
            if user.username and user.username.lower() == 'luoshen00':
                print(f'✅ 找到目标用户！发送消息...')
                await client.send_message(user, '你好我来了')
                print(f'✅ 消息已发送！')
                return
        
        print('❌ 未找到 @luoshen00')
        
    except Exception as e:
        print(f'❌ 错误: {e}')
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(search_and_message())
