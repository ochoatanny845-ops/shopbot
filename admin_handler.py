"""
管理员后台功能模块
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from database import Database
from config import Config
import asyncio

class AdminHandler:
    """管理员功能处理器"""
    
    def __init__(self):
        self.db = Database()
    
    def is_admin(self, user_id: int) -> bool:
        """检查是否为管理员"""
        return user_id in Config.ADMIN_IDS
    
    async def cmd_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /admin 命令"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text('❌ 无权限访问管理员后台')
            return
        
        # 获取统计数据
        stats = self.db.get_statistics()
        
        keyboard = [
            [
                InlineKeyboardButton("👥 用户列表", callback_data='admin_users'),
                InlineKeyboardButton("🔧 系统配置", callback_data='admin_settings')
            ],
            [
                InlineKeyboardButton("📢 群发通知", callback_data='admin_broadcast'),
                InlineKeyboardButton("📝 主菜单编辑", callback_data='admin_edit_start')
            ],
            [InlineKeyboardButton("🏠 返回主菜单", callback_data='back_main')]
        ]
        
        text = (
            '🔐 **管理员后台**\n\n'
            '📊 **平台统计**\n'
            f'👥 用户总数：`{stats["total_users"]}`\n'
            f'💰 平台余额：`${stats["total_balance"]:.2f}`\n'
            f'📈 今日收入：`${stats["today_income"]:.2f}`\n'
            f'📈 昨日收入：`${stats["yesterday_income"]:.2f}`'
        )
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def cmd_cha(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /cha 用户ID 命令"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text('❌ 无权限使用此命令')
            return
        
        # 检查参数
        if not context.args or len(context.args) < 1:
            await update.message.reply_text('❌ 用法：/cha <用户ID>')
            return
        
        try:
            target_user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text('❌ 用户ID必须是数字')
            return
        
        # 查询用户信息
        conn = self.db.get_connection()
        c = conn.cursor()
        
        # 基本信息
        c.execute('''
            SELECT user_id, username, first_name, balance, created_at
            FROM users
            WHERE user_id = ?
        ''', (target_user_id,))
        
        user = c.fetchone()
        
        if not user:
            conn.close()
            await update.message.reply_text(f'❌ 用户 {target_user_id} 不存在')
            return
        
        user_id_db, username, first_name, balance, created_at = user
        
        # 充值统计
        c.execute('''
            SELECT 
                COUNT(*) as count,
                COALESCE(SUM(amount), 0) as total,
                MAX(created_at) as last_time
            FROM balance_logs
            WHERE user_id = ? AND type = 'recharge'
        ''', (target_user_id,))
        
        recharge_stats = c.fetchone()
        recharge_count, recharge_total, last_recharge = recharge_stats
        
        # 消费统计
        c.execute('''
            SELECT 
                COUNT(*) as count,
                COALESCE(SUM(total_price), 0) as total,
                MAX(created_at) as last_time
            FROM orders
            WHERE user_id = ? AND status = 'completed'
        ''', (target_user_id,))
        
        order_stats = c.fetchone()
        order_count, order_total, last_order = order_stats
        
        # 最近订单
        c.execute('''
            SELECT product_name, total_price, created_at, status
            FROM orders
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 5
        ''', (target_user_id,))
        
        recent_orders = c.fetchall()
        conn.close()
        
        # 构建消息
        text = (
            '👤 **用户信息**\n\n'
            f'**ID**: `{user_id_db}`\n'
            f'**用户名**: @{username or "无"}\n'
            f'**昵称**: {first_name or "无"}\n'
            f'**余额**: `${balance:.2f}`\n'
            f'**注册时间**: {created_at[:19]}\n\n'
            '💰 **充值统计**\n'
            f'总充值: `${recharge_total:.2f}` ({recharge_count}次)\n'
            f'最近充值: {last_recharge[:19] if last_recharge else "无"}\n\n'
            '🛍️ **消费统计**\n'
            f'总消费: `${order_total:.2f}` ({order_count}次)\n'
            f'最近购买: {last_order[:19] if last_order else "无"}\n\n'
        )
        
        if recent_orders:
            text += '📋 **最近订单**\n'
            for product_name, price, created, status in recent_orders:
                status_emoji = '✅' if status == 'completed' else '⏳'
                text += f'{status_emoji} {product_name} - ${price:.2f}\n'
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理管理员后台回调"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if not self.is_admin(user_id):
            await query.answer('❌ 无权限', show_alert=True)
            return
        
        data = query.data
        
        if data == 'admin_users':
            await self._show_users(query, context)
        elif data == 'admin_settings':
            await self._show_settings(query, context)
        elif data == 'admin_broadcast':
            await self._start_broadcast(query, context)
        elif data == 'admin_edit_start':
            await self._edit_start_message(query, context)
    
    async def _show_users(self, query, context):
        """显示用户列表"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT user_id, username, balance, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 10
        ''')
        
        users = c.fetchall()
        conn.close()
        
        if not users:
            await query.edit_message_text('暂无用户')
            return
        
        text = '👥 **用户列表** (最近10个)\n\n'
        
        for user_id, username, balance, created_at in users:
            text += (
                f'**ID**: `{user_id}`\n'
                f'用户名: @{username or "无"}\n'
                f'余额: ${balance:.2f}\n'
                f'注册: {created_at[:10]}\n'
                f'━━━━━━━━━━━━━\n'
            )
        
        keyboard = [[InlineKeyboardButton("« 返回", callback_data='admin_back')]]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def _show_settings(self, query, context):
        """显示系统配置"""
        trc20_address = self.db.get_setting('trc20_address')
        
        text = (
            '🔧 **系统配置**\n\n'
            f'**TRC20 收款地址**\n`{trc20_address}`\n\n'
            '点击下方按钮修改配置'
        )
        
        keyboard = [
            [InlineKeyboardButton("📝 修改 TRC20 地址", callback_data='admin_edit_trc20')],
            [InlineKeyboardButton("« 返回", callback_data='admin_back')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def _start_broadcast(self, query, context):
        """开始群发通知"""
        await query.edit_message_text(
            '📢 **群发通知**\n\n'
            '功能开发中...\n\n'
            '将支持：\n'
            '• 图文消息\n'
            '• 自定义按钮\n'
            '• 发送进度显示\n'
            '• 智能间隔防刷屏',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« 返回", callback_data='admin_back')
            ]])
        )
    
    async def _edit_start_message(self, query, context):
        """编辑主菜单文案"""
        current_message = self.db.get_setting('start_message')
        
        text = (
            '📝 **主菜单文案编辑**\n\n'
            '**当前文案：**\n'
            f'{current_message}\n\n'
            '功能开发中...'
        )
        
        keyboard = [[InlineKeyboardButton("« 返回", callback_data='admin_back')]]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
