"""
重新登录指定账号的工具
用于修复 session 损坏问题
"""
import asyncio
import json
import os
from telethon import TelegramClient
from config import Config

async def relogin_account(account_id):
    """重新登录指定账号"""
    config_file = 'accounts_pool.json'
    
    if not os.path.exists(config_file):
        print('❌ 配置文件不存在')
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        accounts = data.get('accounts', [])
    
    # 找到指定账号
    account = None
    for acc in accounts:
        if acc['id'] == account_id:
            account = acc
            break
    
    if not account:
        print(f'❌ 未找到账号 #{account_id}')
        return
    
    print(f'🔄 重新登录账号 #{account["id"]}: {account["phone"]}')
    print('='*60)
    
    # 删除旧的 session 文件
    if os.path.exists(account['session']):
        os.remove(account['session'])
        print(f'✅ 已删除旧 session: {account["session"]}')
    
    # 创建新客户端
    client = TelegramClient(
        account['session'],
        Config.API_ID,
        Config.API_HASH
    )
    
    # 重新登录
    print(f'\n📞 正在发送验证码到 {account["phone"]}...')
    await client.start(phone=account['phone'])
    
    me = await client.get_me()
    print(f'\n✅ 登录成功！')
    print(f'   姓名: {me.first_name}')
    print(f'   手机: {me.phone}')
    print(f'   ID: {me.id}')
    
    await client.disconnect()
    
    print(f'\n💾 Session 已更新')
    print(f'✅ 账号 #{account_id} 修复完成！')

async def main():
    """主函数"""
    print('='*60)
    print('🔧 账号重新登录工具')
    print('='*60)
    print()
    
    try:
        account_id = int(input('请输入要重新登录的账号ID（如 1）: ').strip())
    except ValueError:
        print('❌ 无效的账号ID')
        return
    
    await relogin_account(account_id)

if __name__ == '__main__':
    asyncio.run(main())
