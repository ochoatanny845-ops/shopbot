"""
购买器工厂：根据源机器人选择对应的购买器
"""
from purchasers.hao24bot import Hao24BotPurchaser
from purchasers.sanjianbot import SanJianbotPurchaser

class PurchaserFactory:
    """购买器工厂"""
    
    @staticmethod
    def create(source_bot, client):
        """
        创建对应的购买器
        
        Args:
            source_bot: 源机器人用户名（如 @hao24bot）
            client: Telegram客户端
        
        Returns:
            对应的购买器实例
        """
        if source_bot == '@hao24bot':
            return Hao24BotPurchaser(client)
        elif source_bot == '@SanJianbot':
            return SanJianbotPurchaser(client)
        else:
            raise Exception(f'未知的源机器人: {source_bot}')
