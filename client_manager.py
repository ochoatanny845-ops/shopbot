"""
客户端管理器 - 统一管理代购账号登录
"""
import os
from telethon import TelegramClient
from config import Config

class ClientManager:
    """客户端管理器（单例）"""
    
    _client = None
    
    @classmethod
    async def get_client(cls):
        """获取或创建客户端"""
        if cls._client is None:
            await cls.login()
        return cls._client
    
    @classmethod
    async def login(cls):
        """登录代购账号"""
        cls._client = TelegramClient(
            Config.BUYER_SESSION,
            Config.API_ID,
            Config.API_HASH
        )
        
        # 智能登录逻辑
        session_file = Config.BUYER_SESSION + '.session'
        if os.path.exists(session_file):
            print('🔍 检测到 Session 文件，尝试自动登录...')
            try:
                await cls._client.start(password=lambda: Config.BUYER_2FA or None)
                me = await cls._client.get_me()
                print(f'✅ 代购账号登录成功: {me.first_name} ({me.phone})')
                return
            except Exception as e:
                print(f'⚠️ Session 失效: {e}')
                print('📞 需要重新登录...\n')
        
        # 首次登录
        print('='*60)
        print('📱 首次登录 - 需要手机号和验证码')
        print('='*60)
        
        phone = input('请输入手机号（带国家代码，如 +8613800138000）: ').strip()
        
        def get_password():
            if Config.BUYER_2FA:
                return Config.BUYER_2FA
            return input('请输入两步验证密码（如果没有请直接回车）: ').strip() or None
        
        await cls._client.start(
            phone=phone,
            password=get_password
        )
        
        me = await cls._client.get_me()
        print(f'\n✅ 登录成功！')
        print(f'   账号: {me.first_name}')
        print(f'   手机: {me.phone}')
        print(f'   Session 已保存到: {session_file}')
        print('='*60 + '\n')
    
    @classmethod
    async def disconnect(cls):
        """断开连接"""
        if cls._client:
            await cls._client.disconnect()
            cls._client = None
