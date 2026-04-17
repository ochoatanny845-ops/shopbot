"""
批量上传刷新账号工具
用于添加20个刷新账号到账号池
"""
import asyncio
import json
import os
from telethon import TelegramClient
from config import Config

async def add_account(index, phone):
    """添加一个账号"""
    session_file = f'sessions/scraper_{index}.session'
    
    print(f'\n{"="*60}')
    print(f'添加账号 #{index}')
    print(f'{"="*60}')
    
    client = TelegramClient(session_file, Config.API_ID, Config.API_HASH)
    
    # 登录
    await client.start(phone=phone)
    me = await client.get_me()
    
    print(f'✅ 账号 #{index} 添加成功')
    print(f'   姓名: {me.first_name}')
    print(f'   手机: {me.phone}')
    print(f'   Session: {session_file}')
    
    await client.disconnect()
    
    return {
        'id': index,
        'session': session_file,
        'phone': me.phone,
        'status': 'active',
        'last_used': 0,
        'success_count': 0,
        'fail_count': 0,
        'banned_at': None
    }

async def main():
    """交互式添加账号"""
    print('='*60)
    print('📱 批量上传刷新账号')
    print('='*60)
    print()
    print('请准备20个Telegram账号（手机号 + 验证码）')
    print('建议使用虚拟号码或备用手机号')
    print()
    print('输入 q 可随时退出')
    print('='*60)
    
    # 检查是否已有配置文件
    config_file = 'accounts_pool.json'
    existing_accounts = []
    
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            existing_accounts = data.get('accounts', [])
        
        if existing_accounts:
            print(f'\n⚠️ 检测到已有 {len(existing_accounts)} 个账号')
            choice = input('是否继续添加新账号？(y/n): ').strip().lower()
            if choice != 'y':
                print('已取消')
                return
    
    accounts = existing_accounts.copy()
    start_index = len(accounts) + 1
    
    while True:
        index = len(accounts) + 1
        
        print(f'\n【账号 #{index}】')
        phone = input(f'请输入手机号（带国家代码，如 +8613800138000，或输入 q 退出）: ').strip()
        
        if phone.lower() == 'q':
            break
        
        if not phone.startswith('+'):
            print('❌ 手机号必须以 + 开头（如 +8613800138000）')
            continue
        
        try:
            account = await add_account(index, phone)
            accounts.append(account)
            print(f'\n✅ 成功添加账号 #{index}')
            
            # 自动保存（防止中途退出丢失）
            save_accounts(accounts, config_file)
            
        except Exception as e:
            print(f'❌ 添加失败: {e}')
            retry = input('是否重试？(y/n): ').strip().lower()
            if retry != 'y':
                continue
    
    # 最终保存
    save_accounts(accounts, config_file)
    
    print('\n' + '='*60)
    print(f'✅ 账号上传完成！')
    print(f'   总账号数: {len(accounts)}')
    print(f'   新增账号: {len(accounts) - len(existing_accounts)}')
    print(f'   配置文件: {config_file}')
    print('='*60)
    print()
    print('下一步：运行刷新器')
    print('  python scraper_pool_manager.py')
    print()

def save_accounts(accounts, config_file):
    """保存账号配置"""
    data = {
        'accounts': accounts,
        'current_index': 0,
        'rotation_interval': 60  # 默认1分钟
    }
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f'  💾 已保存到 {config_file}')

if __name__ == '__main__':
    asyncio.run(main())
