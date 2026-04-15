"""
创建第二个代购账号 session
用于 @SanJianbot
"""
from telethon import TelegramClient
from config import Config
import asyncio

async def main():
    """创建第二个代购账号 session"""
    
    # session 文件路径
    session_path = 'sessions/buyer_account_2'
    
    print('🔐 创建第二个代购账号 session...')
    print(f'📁 Session 文件：{session_path}.session')
    print()
    print('⚠️  请使用与第一个代购账号不同的手机号登录')
    print()
    
    # 创建客户端
    client = TelegramClient(session_path, Config.API_ID, Config.API_HASH)
    
    try:
        await client.start()
        
        me = await client.get_me()
        print()
        print('✅ 登录成功！')
        print(f'账号：{me.first_name} (@{me.username})')
        print(f'手机号：+{me.phone}')
        print()
        print(f'✅ Session 文件已创建：{session_path}.session')
        print()
        print('📝 下一步：')
        print('1. 用这个账号向 @SanJianbot 发送 /start')
        print('2. 确保账号有足够余额')
        print('3. 运行商品同步脚本')
        
    except Exception as e:
        print(f'❌ 登录失败：{e}')
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
