"""
充值功能模块
处理用户充值请求和验证
"""
import asyncio
import qrcode
import io
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from trc20_recharge import TRC20Recharge
from config import Config

class RechargeHandler:
    """充值处理器"""
    
    def __init__(self):
        self.db = Database()
        # 从 Config 中读取收款地址和 API Key
        self.recipient_address = Config.USDT_RECEIVER_ADDRESS if hasattr(Config, 'USDT_RECEIVER_ADDRESS') else 'TV77o3KfH8DkQNNEsvDLNo765ABcqr3MnM'
        self.api_key = Config.TRONGRID_API_KEY if hasattr(Config, 'TRONGRID_API_KEY') else None
        
        # 初始化验证器（传递 API Key）
        self.verifier = TRC20Recharge(self.recipient_address, self.api_key)
    
    async def handle_recharge_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理充值请求"""
        user_id = update.effective_user.id
        
        # 创建充值订单（待输入金额）
        keyboard = [
            [InlineKeyboardButton("💰 输入充值金额", callback_data='recharge_input_amount')],
            [InlineKeyboardButton("🔙 返回", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            '💰 **USDT 充值**\n\n'
            '支持：USDT TRC20\n'
            '到账时间：1-3 分钟\n'
            '最低充值：1 USDT\n\n'
            '请点击下方按钮输入充值金额',
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_amount_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理金额输入"""
        query = update.callback_query
        await query.answer()
        
        # 设置用户状态：等待输入金额
        context.user_data['waiting_for'] = 'recharge_amount'
        
        await query.edit_message_text(
            '💰 **请输入充值金额**\n\n'
            '⚠️ 最低充值：1 USDT\n'
            '⚠️ 请输入数字，例如：10',
            parse_mode='Markdown'
        )
    
    async def handle_amount_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理用户输入的金额"""
        user_id = update.effective_user.id
        
        # 检查是否在等待金额输入
        if context.user_data.get('waiting_for') != 'recharge_amount':
            return
        
        try:
            amount = float(update.message.text.strip())
            
            if amount < 1:
                await update.message.reply_text('❌ 最低充值金额为 1 USDT')
                return
            
            # 创建充值订单
            order_id = self._create_recharge_order(user_id, amount)
            
            # 生成支付信息
            await self._send_payment_info(update, amount, order_id)
            
            # 清除状态
            context.user_data['waiting_for'] = None
            
        except ValueError:
            await update.message.reply_text('❌ 请输入有效的数字，例如：10')
    
    def _create_recharge_order(self, user_id: int, amount: float) -> int:
        """创建充值订单"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO recharge_orders (user_id, amount, status, created_at)
            VALUES (?, ?, 'pending', ?)
        ''', (user_id, amount, datetime.now().isoformat()))
        
        order_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return order_id
    
    async def _send_payment_info(self, update: Update, amount: float, order_id: int):
        """发送支付信息"""
        # 生成二维码
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(self.recipient_address)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 保存到内存
        bio = io.BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)
        
        # 发送支付信息
        message = (
            f'💰 **充值订单 #{order_id}**\n\n'
            f'充值金额：`{amount}` USDT\n'
            f'网络类型：TRC20 (Tron)\n'
            f'收款地址：\n`{self.recipient_address}`\n\n'
            f'⚠️ **重要提示：**\n'
            f'1️⃣ 请确保使用 **TRC20 网络**\n'
            f'2️⃣ 转账完成后，发送交易哈希（TxID）\n'
            f'3️⃣ 系统将自动验证并入账\n\n'
            f'📝 交易哈希格式示例：\n'
            f'`7a1b2c3d4e5f...`'
        )
        
        # 发送二维码
        await update.message.reply_photo(
            photo=bio,
            caption=message,
            parse_mode='Markdown'
        )
        
        # 提示等待 TxID
        await update.message.reply_text(
            '⏳ 请完成转账后，发送交易哈希（TxID）给我\n\n'
            '💡 在钱包中复制交易哈希即可',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ 取消充值", callback_data=f'cancel_recharge_{order_id}')
            ]])
        )
    
    async def handle_txid_verification(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理用户提交的 TxID"""
        user_id = update.effective_user.id
        txid = update.message.text.strip()
        
        # 简单验证格式（64 位十六进制）
        if len(txid) != 64:
            await update.message.reply_text(
                '❌ 交易哈希格式错误\n\n'
                '正确格式：64 位字符\n'
                '示例：7a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d...'
            )
            return
        
        # 查询待验证的充值订单
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT id, amount FROM recharge_orders
            WHERE user_id = ? AND status = 'pending'
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))
        
        order = c.fetchone()
        
        if not order:
            await update.message.reply_text('❌ 未找到待充值的订单，请先点击"充值"按钮')
            conn.close()
            return
        
        order_id, expected_amount = order
        
        # 检查 TxID 是否已被使用
        c.execute('SELECT id FROM recharge_orders WHERE txid = ?', (txid,))
        if c.fetchone():
            await update.message.reply_text('❌ 该交易哈希已被使用')
            conn.close()
            return
        
        conn.close()
        
        # 开始验证
        msg = await update.message.reply_text('🔍 正在验证交易，请稍候...')
        
        # 验证交易
        result = self.verifier.verify_transaction(txid, expected_amount)
        
        if result['success']:
            # 验证通过，入账
            actual_amount = result['amount']
            
            # 更新订单状态
            conn = self.db.get_connection()
            c = conn.cursor()
            
            c.execute('''
                UPDATE recharge_orders
                SET status = 'completed', txid = ?, actual_amount = ?, completed_at = ?
                WHERE id = ?
            ''', (txid, actual_amount, datetime.now().isoformat(), order_id))
            
            # 增加用户余额
            c.execute('''
                UPDATE users
                SET balance = balance + ?
                WHERE user_id = ?
            ''', (actual_amount, user_id))
            
            conn.commit()
            conn.close()
            
            # 通知用户
            await msg.edit_text(
                f'✅ **充值成功！**\n\n'
                f'订单号：#{order_id}\n'
                f'充值金额：{actual_amount} USDT\n'
                f'交易哈希：`{txid[:16]}...{txid[-16:]}`\n'
                f'到账时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'
                f'当前余额：${self._get_user_balance(user_id):.2f}',
                parse_mode='Markdown'
            )
        else:
            # 验证失败
            await msg.edit_text(
                f'❌ **验证失败**\n\n'
                f'{result["message"]}\n\n'
                f'如有疑问，请联系客服',
                parse_mode='Markdown'
            )
    
    def _get_user_balance(self, user_id: int) -> float:
        """获取用户余额"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        
        return result[0] if result else 0.0
