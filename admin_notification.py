"""
管理员通知模块
用于在充值和购买时向管理员发送通知
"""
from telegram import Bot
from config import Config
from datetime import datetime

async def notify_admin_recharge(bot: Bot, user_id: int, username: str, amount: float, method: str, order_id: int):
    """
    通知管理员有用户充值
    
    Args:
        bot: Telegram Bot实例
        user_id: 用户ID
        username: 用户名
        amount: 充值金额
        method: 充值方式 (trc20/okpay)
        order_id: 订单ID
    """
    method_text = {
        'trc20': 'TRC20-USDT',
        'okpay': 'OKPay'
    }
    
    message = (
        f"💰 <b>充值通知</b>\n\n"
        f"用户: <code>{username}</code> @{username if username else 'N/A'}\n"
        f"用户ID: <code>{user_id}</code>\n"
        f"充值金额: <b>${amount:.2f}</b>\n"
        f"充值方式: {method_text.get(method, method)}\n"
        f"订单号: #{order_id}\n"
        f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    for admin_id in Config.ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"❌ 发送充值通知给管理员 {admin_id} 失败: {e}")

async def notify_admin_purchase(bot: Bot, user_id: int, username: str, product_name: str, quantity: int, total_price: float, order_id: int):
    """
    通知管理员有用户购买
    
    Args:
        bot: Telegram Bot实例
        user_id: 用户ID
        username: 用户名
        product_name: 商品名称
        quantity: 购买数量
        total_price: 总价
        order_id: 订单ID
    """
    message = (
        f"🛒 <b>购买订单</b>\n\n"
        f"用户: <code>{username}</code> @{username if username else 'N/A'}\n"
        f"用户ID: <code>{user_id}</code>\n"
        f"购买商品: {product_name}\n"
        f"购买数量: {quantity}\n"
        f"订单金额: <b>${total_price:.2f}</b>\n"
        f"订单号: #{order_id}\n"
        f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    for admin_id in Config.ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"❌ 发送购买通知给管理员 {admin_id} 失败: {e}")
