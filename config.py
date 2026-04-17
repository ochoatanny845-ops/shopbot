"""
配置文件
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    """系统配置"""
    
    # ============================================
    # Telegram API 配置
    # ============================================
    API_ID = int(os.getenv('API_ID', '2040'))
    API_HASH = os.getenv('API_HASH', 'b18441a1ff607e10a989891a5462e627')
    
    # ============================================
    # 销售机器人配置
    # ============================================
    BOT_TOKEN = os.getenv('BOT_TOKEN', '8675984914:AAHG3RmeBBSNgUjYKwm0KrwklsFlElln8KY')
    BOT_USERNAME = os.getenv('BOT_USERNAME', 'TGaccbbbot')
    
    # 管理员用户ID（逗号分隔）
    ADMIN_IDS = [int(x.strip()) for x in os.getenv('ADMIN_IDS', '6919491196').split(',')]
    
    # 告警通知接收者（用于刷新器告警）
    ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '5991190607'))  # 默认为你的ID
    
    # ============================================
    # 源机器人配置
    # ============================================
    SOURCE_BOT = os.getenv('SOURCE_BOT', 'hao24bot')
    
    # 代购账号 session 文件路径（不含 .session 扩展名）
    BUYER_SESSION = os.getenv('BUYER_SESSION', 'sessions/buyer_account')
    
    # 两步验证密码（可选，留空则运行时输入）
    BUYER_2FA = os.getenv('BUYER_2FA', '')
    
    # ============================================
    # 定价配置
    # ============================================
    # 固定加价（美元）
    MARKUP_FIXED = float(os.getenv('MARKUP_FIXED', '0.05'))
    
    # 最低利润（美元）
    MIN_PROFIT = float(os.getenv('MIN_PROFIT', '0.05'))
    
    # ============================================
    # 同步配置
    # ============================================
    # 同步间隔（秒）
    SYNC_INTERVAL = int(os.getenv('SYNC_INTERVAL', '3600'))  # 1小时
    
    # 请求延迟（秒）
    REQUEST_DELAY = int(os.getenv('REQUEST_DELAY', '3'))
    
    # ============================================
    # 数据库配置
    # ============================================
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'shopbot.db')
    
    # ============================================
    # 文件存储配置
    # ============================================
    # 订单文件存储目录
    ORDER_FILES_DIR = os.getenv('ORDER_FILES_DIR', 'orders')
    
    # ============================================
    # 充值配置
    # ============================================
    # USDT TRC20 收款地址
    USDT_RECEIVER_ADDRESS = os.getenv('USDT_RECEIVER_ADDRESS', 'TV77o3KfH8DkQNNEsvDLNo765ABcqr3MnM')
    
    # 最低充值金额（USDT）
    MIN_RECHARGE_AMOUNT = float(os.getenv('MIN_RECHARGE_AMOUNT', '1.0'))
    
    # TronGrid API Key（可选，免费版留空）
    TRONGRID_API_KEY = os.getenv('TRONGRID_API_KEY', '')
    
    # ============================================
    # OKPay 配置
    # ============================================
    # OKPay 商户 ID
    OKPAY_SHOP_ID = os.getenv('OKPAY_SHOP_ID', '')
    
    # OKPay 商户 Token
    OKPAY_SHOP_TOKEN = os.getenv('OKPAY_SHOP_TOKEN', '')
    
    # OKPay 回调服务器端口
    OKPAY_CALLBACK_PORT = int(os.getenv('OKPAY_CALLBACK_PORT', '8888'))
    
    # OKPay Bot 用户名（用于返回链接）
    OKPAY_BOT_USERNAME = os.getenv('OKPAY_BOT_USERNAME', 'TGaccbbbot')
    
    # ============================================
    # 日志配置
    # ============================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
