"""
添加好友并发送消息
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
YOUR_USERNAME = 'luoshen00'

async def send_hello():
    """添加好友并发送消息"""
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        await client.start()
        print('✅ 登录成功！')
        
        # 获取当前账号信息
        me = await client.get_me()
        print(f'📱 当前账号: {me.first_name} - ID: {me.id}')
        
        # 通过用户名查找你
        try:
            user = await client.get_entity(YOUR_USERNAME)
            print(f'✅ 找到用户: {user.first_name} (@{user.username})')
            
            # 发送消息
            await client.send_message(user, '你好我来了')
            print(f'✅ 消息已发送！')
            
        except Exception as e:
            print(f'❌ 查找用户失败: {e}')
            print(f'尝试搜索用户...')
            
            # 尝试搜索
            result = await client(functions.contacts.SearchRequest(
                q=YOUR_USERNAME,
                limit=10
            ))
            print(f'搜索结果: {result}')
        
    except Exception as e:
        print(f'❌ 错误: {e}')
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(send_hello())
