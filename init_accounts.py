"""
初始化刷新账号 - 让所有账号与源机器人建立对话
解决 "No user has 'hao24bot' as username" 问题
"""
import asyncio
import json
import os
from telethon import TelegramClient
from config import Config

async def init_account(account):
    """初始化单个账号"""
    print(f'\n🔄 初始化账号 #{account["id"]}: {account["phone"]}')
    
    client = TelegramClient(
        account['session'],
        Config.API_ID,
        Config.API_HASH
    )
    
    await client.start()
    
    try:
        # 1. 搜索并启动对话
        print(f'  📞 正在连接源机器人 @{Config.SOURCE_BOT}...')
        
        # 发送 /start 命令
        await client.send_message(Config.SOURCE_BOT, '/start')
        await asyncio.sleep(3)
        
        # 获取最新消息
        msgs = await client.get_messages(Config.SOURCE_BOT, limit=1)
        
        if msgs and msgs[0].buttons:
            # 检查是否是语言选择按钮
            buttons = msgs[0].buttons
            print(f'  🌐 检测到语言选择界面')
            
            # 查找简体中文按钮
            chinese_button = None
            for row in buttons:
                for btn in row:
                    if '简体中文' in btn.text or 'Chinese' in btn.text or '中文' in btn.text:
                        chinese_button = btn
                        break
                if chinese_button:
                    break
            
            if chinese_button:
                print(f'  ✅ 点击"简体中文"按钮...')
                await chinese_button.click()
                await asyncio.sleep(3)
                
                # 再次获取消息确认
                msgs = await client.get_messages(Config.SOURCE_BOT, limit=1)
                if msgs:
                    print(f'  ✅ 语言设置完成')
            else:
                print(f'  ⚠️ 未找到简体中文按钮，尝试发送文本"简体中文"')
                await client.send_message(Config.SOURCE_BOT, '简体中文')
                await asyncio.sleep(2)
        
        # 测试获取主菜单
        await client.send_message(Config.SOURCE_BOT, '🏠主菜单')
        await asyncio.sleep(2)
        
        msgs = await client.get_messages(Config.SOURCE_BOT, limit=1)
        if msgs:
            print(f'  ✅ 成功建立对话（主菜单可访问）')
        else:
            print(f'  ⚠️ 未收到回复，但连接成功')
        
    except Exception as e:
        print(f'  ❌ 初始化失败: {e}')
    
    await client.disconnect()

async def main():
    """主函数"""
    print('='*60)
    print('🔧 刷新账号初始化工具')
    print('='*60)
    print()
    print(f'目标机器人: @{Config.SOURCE_BOT}')
    print('='*60)
    
    config_file = 'accounts_pool.json'
    
    if not os.path.exists(config_file):
        print('❌ 配置文件不存在: accounts_pool.json')
        print('💡 请先使用账号管理Bot添加账号')
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        accounts = data.get('accounts', [])
    
    if not accounts:
        print('❌ 账号池为空')
        return
    
    print(f'\n📊 找到 {len(accounts)} 个账号')
    print('🔄 开始初始化...\n')
    
    for account in accounts:
        if account['status'] != 'active':
            print(f'⏭️ 跳过非活跃账号 #{account["id"]}')
            continue
        
        await init_account(account)
    
    print('\n' + '='*60)
    print('✅ 初始化完成！')
    print('='*60)
    print()
    print('下一步：启动刷新器')
    print('  python scraper_pool_manager.py')
    print()

if __name__ == '__main__':
    asyncio.run(main())
