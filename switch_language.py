"""
自动切换源机器人语言为简体中文
"""
import asyncio
from telethon import TelegramClient
from config import Config

async def switch_to_chinese():
    """切换语言为简体中文"""
    client = TelegramClient('sessions/buyer_account', Config.API_ID, Config.API_HASH)
    await client.start()
    
    print("=" * 60)
    print("🌐 自动切换语言为简体中文")
    print("=" * 60)
    
    try:
        # 1. 发送主菜单
        print("\n📱 发送主菜单命令...")
        await client.send_message(Config.SOURCE_BOT, '🏠Main Menu')
        await asyncio.sleep(2)
        
        # 2. 获取最新消息
        msgs = await client.get_messages(Config.SOURCE_BOT, limit=1)
        
        if msgs and msgs[0].buttons:
            print(f"✅ 找到 {len(msgs[0].buttons)} 行按钮")
            
            # 3. 查找并点击语言按钮
            language_clicked = False
            for row in msgs[0].buttons:
                for btn in row:
                    if '🌐' in btn.text or 'Language' in btn.text or '我的语言' in btn.text:
                        print(f"✅ 找到语言按钮: '{btn.text}'")
                        await btn.click()
                        await asyncio.sleep(2)
                        language_clicked = True
                        break
                if language_clicked:
                    break
            
            if language_clicked:
                # 4. 获取语言选择按钮
                msgs2 = await client.get_messages(Config.SOURCE_BOT, limit=1)
                
                if msgs2 and msgs2[0].buttons:
                    print(f"\n📋 语言选择菜单（{len(msgs2[0].buttons)} 行按钮）：")
                    
                    # 5. 查找并点击中文按钮（简体或繁体）
                    chinese_clicked = False
                    for i, row in enumerate(msgs2[0].buttons):
                        for j, btn in enumerate(row):
                            print(f"  第{i+1}行按钮{j+1}: '{btn.text}'")
                            # 匹配简体中文、繁体中文、中文
                            if ('简体中文' in btn.text or '繁体中文' in btn.text or 
                                '中文' in btn.text or 'Chinese' in btn.text):
                                print(f"\n✅ 找到中文按钮: '{btn.text}'")
                                await btn.click()
                                await asyncio.sleep(2)
                                chinese_clicked = True
                                break
                        if chinese_clicked:
                            break
                    
                    if chinese_clicked:
                        print("\n✅ 语言切换成功！")
                        
                        # 6. 验证切换结果
                        await asyncio.sleep(2)
                        msgs3 = await client.get_messages(Config.SOURCE_BOT, limit=1)
                        if msgs3 and msgs3[0].buttons:
                            print("\n🔍 切换后的按钮（验证）：")
                            for row in msgs3[0].buttons:
                                for btn in row:
                                    print(f"  - {btn.text}")
                    else:
                        print("\n❌ 未找到中文按钮")
                        print("尝试直接发送文本'简体中文'...")
                        await client.send_message(Config.SOURCE_BOT, '简体中文')
                        await asyncio.sleep(2)
                        print("✅ 已发送文本")
            else:
                print("\n❌ 未找到语言按钮")
        else:
            print("❌ 没有找到按钮")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    
    finally:
        await client.disconnect()
        print("\n" + "=" * 60)
        print("✅ 完成")
        print("=" * 60)

if __name__ == '__main__':
    asyncio.run(switch_to_chinese())
