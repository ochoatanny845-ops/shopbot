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
            [
                InlineKeyboardButton("🎛️ 自定义按钮", callback_data='admin_custom_buttons'),
                InlineKeyboardButton("ℹ️ 信息配置", callback_data='admin_info_config')
            ],
            [InlineKeyboardButton("🏠 返回主菜单", callback_data='back_main')]
        ]
        
        text = (
            '<b>🔐 管理员后台</b>\n\n'
            '<b>📊 平台统计</b>\n'
            f'👥 用户总数: <code>{stats["total_users"]}</code>\n'
            f'💰 平台余额: <code>${stats["total_balance"]:.2f}</code>\n'
            f'📈 今日收入: <code>${stats["today_income"]:.2f}</code>\n'
            f'📈 昨日收入: <code>${stats["yesterday_income"]:.2f}</code>'
        )
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
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
        elif data == 'admin_info_config':
            await self._show_info_config(query, context)
        elif data == 'admin_broadcast':
            await self._start_broadcast(query, context)
        elif data == 'admin_edit_start':
            await self._edit_start_message(query, context)
        elif data == 'admin_edit_trc20':
            await self._edit_trc20_address(query, context)
        elif data == 'admin_edit_notification':
            await self._edit_notification_url(query, context)
        elif data == 'admin_edit_customer_service':
            await self._edit_customer_service_url(query, context)
        elif data == 'admin_edit_start_text':
            await self._edit_start_text(query, context)
        elif data == 'admin_custom_buttons':
            await self._manage_custom_buttons(query, context)
        elif data.startswith('admin_btn_'):
            await self._handle_button_management(query, context)
        elif data.startswith('btn_type_'):
            await self._handle_button_type_selection(query, context)
        elif data == 'admin_back':
            # 返回管理员主菜单
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
                [
                    InlineKeyboardButton("🎛️ 自定义按钮", callback_data='admin_custom_buttons'),
                    InlineKeyboardButton("ℹ️ 信息配置", callback_data='admin_info_config')
                ],
                [InlineKeyboardButton("🏠 返回主菜单", callback_data='back_main')]
            ]
            
            text = (
                '<b>🔐 管理员后台</b>\n\n'
                '<b>📊 平台统计</b>\n'
                f'👥 用户总数: <code>{stats["total_users"]}</code>\n'
                f'💰 平台余额: <code>${stats["total_balance"]:.2f}</code>\n'
                f'📈 今日收入: <code>${stats["today_income"]:.2f}</code>\n'
                f'📈 昨日收入: <code>${stats["yesterday_income"]:.2f}</code>'
            )
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
    
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
                f'<b>ID</b>: <code>{user_id}</code>\n'
                f'用户名: {username or "无"}\n'
                f'余额: ${balance:.2f}\n'
                f'注册: {created_at[:10]}\n'
                f'━━━━━━━━━━━━━\n'
            )
        
        keyboard = [[InlineKeyboardButton("« 返回", callback_data='admin_back')]]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
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
            parse_mode='HTML'
        )
    
    async def _start_broadcast(self, query, context):
        """开始群发通知"""
        await query.edit_message_text(
            '📢 **群发通知**\n\n'
            '请发送要群发的消息内容：\n\n'
            '支持：\n'
            '• 纯文本\n'
            '• 图片 + 文字说明\n'
            '• Markdown 格式\n\n'
            '发送消息后，可添加按钮并预览',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ 取消", callback_data='admin_back')
            ]])
        )
        
        # 设置状态
        context.user_data['admin_waiting_for'] = 'broadcast_message'
        context.user_data['broadcast_data'] = {
            'text': None,
            'photo': None,
            'buttons': []
        }
    
    async def handle_broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理群发消息输入"""
        broadcast_data = context.user_data.get('broadcast_data', {})
        
        # 获取消息内容
        if update.message.photo:
            # 图片消息
            photo = update.message.photo[-1]
            broadcast_data['photo'] = photo.file_id
            broadcast_data['text'] = update.message.caption or ''
        else:
            # 文本消息
            broadcast_data['text'] = update.message.text
        
        context.user_data['broadcast_data'] = broadcast_data
        
        # 显示预览和选项
        keyboard = [
            [InlineKeyboardButton("➕ 添加按钮", callback_data='broadcast_add_button')],
            [InlineKeyboardButton("👁️ 预览消息", callback_data='broadcast_preview')],
            [InlineKeyboardButton("✅ 确认发送", callback_data='broadcast_confirm')],
            [InlineKeyboardButton("❌ 取消", callback_data='admin_back')]
        ]
        
        await update.message.reply_text(
            '✅ **消息已接收**\n\n'
            '请选择操作：',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        # 清除等待状态
        context.user_data['admin_waiting_for'] = None
    
    async def handle_broadcast_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理群发相关回调"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == 'broadcast_add_button':
            await query.edit_message_text(
                '➕ **添加按钮**\n\n'
                '请发送按钮信息，格式：\n'
                '`按钮文字|URL`\n\n'
                '示例：\n'
                '`访问官网|https://example.com`',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ 取消", callback_data='broadcast_back')
                ]]),
                parse_mode='HTML'
            )
            context.user_data['admin_waiting_for'] = 'broadcast_button'
        
        elif data == 'broadcast_preview':
            await self._preview_broadcast(query, context)
        
        elif data == 'broadcast_confirm':
            await self._send_broadcast(query, context)
        
        elif data == 'broadcast_back':
            # 返回群发选项
            keyboard = [
                [InlineKeyboardButton("➕ 添加按钮", callback_data='broadcast_add_button')],
                [InlineKeyboardButton("👁️ 预览消息", callback_data='broadcast_preview')],
                [InlineKeyboardButton("✅ 确认发送", callback_data='broadcast_confirm')],
                [InlineKeyboardButton("❌ 取消", callback_data='admin_back')]
            ]
            
            await query.edit_message_text(
                '✅ **消息已接收**\n\n'
                '请选择操作：',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def handle_broadcast_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理按钮输入"""
        text = update.message.text.strip()
        
        if '|' not in text:
            await update.message.reply_text('❌ 格式错误！请使用：`按钮文字|URL`', parse_mode='Markdown')
            return
        
        parts = text.split('|', 1)
        button_text = parts[0].strip()
        button_url = parts[1].strip()
        
        # 添加按钮
        broadcast_data = context.user_data.get('broadcast_data', {})
        if 'buttons' not in broadcast_data:
            broadcast_data['buttons'] = []
        
        broadcast_data['buttons'].append({'text': button_text, 'url': button_url})
        context.user_data['broadcast_data'] = broadcast_data
        
        keyboard = [
            [InlineKeyboardButton("➕ 继续添加", callback_data='broadcast_add_button')],
            [InlineKeyboardButton("👁️ 预览消息", callback_data='broadcast_preview')],
            [InlineKeyboardButton("✅ 确认发送", callback_data='broadcast_confirm')],
            [InlineKeyboardButton("❌ 取消", callback_data='admin_back')]
        ]
        
        await update.message.reply_text(
            f'✅ 按钮已添加：{button_text}\n\n'
            f'当前按钮数：{len(broadcast_data["buttons"])}',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        context.user_data['admin_waiting_for'] = None
    
    async def _preview_broadcast(self, query, context):
        """预览群发消息"""
        broadcast_data = context.user_data.get('broadcast_data', {})
        
        text = broadcast_data.get('text', '（无文本）')
        photo = broadcast_data.get('photo')
        buttons = broadcast_data.get('buttons', [])
        
        # 构建按钮
        keyboard = []
        for btn in buttons:
            keyboard.append([InlineKeyboardButton(btn['text'], url=btn['url'])])
        
        # 发送预览
        await query.message.reply_text('📋 **消息预览：**')
        
        try:
            if photo:
                await query.message.reply_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None,
                    parse_mode='HTML'
                )
            else:
                await query.message.reply_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None,
                    parse_mode='HTML'
                )
        except Exception as e:
            await query.message.reply_text(f'❌ 预览失败：{e}')
    
    async def _send_broadcast(self, query, context):
        """发送群发消息"""
        broadcast_data = context.user_data.get('broadcast_data', {})
        
        text = broadcast_data.get('text', '')
        photo = broadcast_data.get('photo')
        buttons = broadcast_data.get('buttons', [])
        
        # 获取所有用户
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute('SELECT user_id FROM users')
        users = c.fetchall()
        conn.close()
        
        total = len(users)
        success = 0
        failed = 0
        
        # 构建按钮
        keyboard = []
        for btn in buttons:
            keyboard.append([InlineKeyboardButton(btn['text'], url=btn['url'])])
        
        # 发送进度消息
        progress_msg = await query.message.reply_text(
            f'📤 **开始群发...**\n\n'
            f'总用户数：{total}\n'
            f'已发送：0\n'
            f'失败：0'
        )
        
        # 逐个发送
        for i, (user_id,) in enumerate(users, 1):
            try:
                if photo:
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo,
                        caption=text,
                        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None,
                        parse_mode='HTML'
                    )
                else:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=text,
                        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None,
                        parse_mode='HTML'
                    )
                success += 1
            except Exception as e:
                failed += 1
                print(f'  ⚠️ 发送给用户 {user_id} 失败: {e}')
            
            # 每10个用户更新一次进度
            if i % 10 == 0 or i == total:
                try:
                    await progress_msg.edit_text(
                        f'📤 **群发进度**\n\n'
                        f'总用户数：{total}\n'
                        f'已发送：{success}\n'
                        f'失败：{failed}\n'
                        f'进度：{i}/{total} ({i*100//total}%)'
                    )
                except:
                    pass
            
            # 智能间隔（1-2秒）
            await asyncio.sleep(1.5)
        
        # 完成提示
        await progress_msg.edit_text(
            f'✅ **群发完成！**\n\n'
            f'总用户数：{total}\n'
            f'成功发送：{success}\n'
            f'发送失败：{failed}'
        )
        
        # 清除群发数据
        context.user_data['broadcast_data'] = None
    
    async def _manage_custom_buttons(self, query, context):
        """管理自定义按钮"""
        buttons = self.db.get_custom_buttons()
        
        text = '🎛️ **自定义菜单按钮管理**\n\n'
        
        if buttons:
            text += '**当前按钮：**\n\n'
            for btn in buttons:
                btn_type_text = '🔗 链接' if btn['type'] == 'url' else '💬 消息'
                text += f'{btn["position"]}. {btn["text"]} ({btn_type_text})\n'
                text += f'   内容: {btn["content"][:50]}...\n\n'
        else:
            text += '暂无自定义按钮\n\n'
        
        text += '点击下方按钮管理'
        
        keyboard = [[InlineKeyboardButton("➕ 添加按钮", callback_data='admin_btn_add')]]
        
        if buttons:
            keyboard.append([InlineKeyboardButton("📋 编辑按钮", callback_data='admin_btn_list')])
        
        keyboard.append([InlineKeyboardButton("« 返回", callback_data='admin_back')])
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    
    async def _handle_button_management(self, query, context):
        """处理按钮管理操作"""
        data = query.data
        
        if data == 'admin_btn_add':
            await query.edit_message_text(
                '➕ **添加自定义按钮 - 步骤 1/3**\n\n'
                '请输入按钮文字：',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ 取消", callback_data='admin_custom_buttons')
                ]])
            )
            context.user_data['admin_waiting_for'] = 'custom_button_text'
            context.user_data['custom_button_data'] = {}
        
        elif data == 'admin_btn_list':
            buttons = self.db.get_custom_buttons()
            
            text = '📋 **编辑自定义按钮**\n\n选择要编辑的按钮：\n\n'
            
            keyboard = []
            for btn in buttons:
                keyboard.append([InlineKeyboardButton(
                    f'{btn["text"]}',
                    callback_data=f'admin_btn_edit_{btn["id"]}'
                )])
            
            keyboard.append([InlineKeyboardButton("« 返回", callback_data='admin_custom_buttons')])
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        
        elif data.startswith('admin_btn_edit_'):
            button_id = int(data.split('_')[3])
            
            # 查询按钮信息
            buttons = self.db.get_custom_buttons()
            btn = next((b for b in buttons if b['id'] == button_id), None)
            
            if not btn:
                await query.answer('❌ 按钮不存在', show_alert=True)
                return
            
            text = (
                f'✏️ **编辑按钮**\n\n'
                f'**按钮文字：** {btn["text"]}\n'
                f'**类型：** {btn["type"]}\n'
                f'**内容：**\n{btn["content"]}\n\n'
                f'选择操作：'
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("🔼 上移", callback_data=f'admin_btn_up_{button_id}'),
                    InlineKeyboardButton("🔽 下移", callback_data=f'admin_btn_down_{button_id}')
                ],
                [InlineKeyboardButton("🗑️ 删除", callback_data=f'admin_btn_del_{button_id}')],
                [InlineKeyboardButton("« 返回", callback_data='admin_btn_list')]
            ]
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        
        elif data.startswith('admin_btn_up_') or data.startswith('admin_btn_down_'):
            direction = 'up' if 'up' in data else 'down'
            button_id = int(data.split('_')[3])
            
            self.db.move_custom_button(button_id, direction)
            await query.answer(f'✅ 已{"上移" if direction == "up" else "下移"}')
            
            # 刷新编辑页面
            await self._handle_button_management(
                type('obj', (), {'data': f'admin_btn_edit_{button_id}', 'answer': query.answer, 'edit_message_text': query.edit_message_text})(),
                context
            )
        
        elif data.startswith('admin_btn_del_'):
            button_id = int(data.split('_')[3])
            
            self.db.delete_custom_button(button_id)
            await query.answer('✅ 已删除按钮')
            
            # 返回按钮列表
            await self._manage_custom_buttons(query, context)
    
    async def _handle_button_type_selection(self, query, context):
        """处理按钮类型选择"""
        btn_type = query.data.split('_')[2]  # message or url
        
        custom_button_data = context.user_data.get('custom_button_data', {})
        custom_button_data['type'] = btn_type
        context.user_data['custom_button_data'] = custom_button_data
        
        if btn_type == 'message':
            await query.edit_message_text(
                '➕ **添加自定义按钮 - 步骤 3/3**\n\n'
                '请输入消息内容：\n\n'
                '💡 **提示：**\n'
                '• 支持 Markdown 格式\n'
                '• 输入 `\\n` 表示换行\n\n'
                '**示例：**\n'
                '📖 **使用教程**\\n\\n1. 充值余额\\n2. 选择商品',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ 取消", callback_data='admin_custom_buttons')
                ]]),
                parse_mode='HTML'
            )
            context.user_data['admin_waiting_for'] = 'custom_button_message'
        else:  # url
            await query.edit_message_text(
                '➕ **添加自定义按钮 - 步骤 3/3**\n\n'
                '请输入跳转链接：\n\n'
                '**示例：**\n'
                '`https://t.me/yourchannel`',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ 取消", callback_data='admin_custom_buttons')
                ]]),
                parse_mode='HTML'
            )
            context.user_data['admin_waiting_for'] = 'custom_button_url'
    
    async def handle_custom_button_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理自定义按钮输入（交互式）"""
        waiting_for = context.user_data.get('admin_waiting_for')
        text = update.message.text.strip()
        
        if waiting_for == 'custom_button_text':
            # 步骤 1：保存按钮文字，询问类型
            context.user_data['custom_button_data'] = {'text': text}
            
            keyboard = [
                [
                    InlineKeyboardButton("💬 消息", callback_data='btn_type_message'),
                    InlineKeyboardButton("🔗 链接", callback_data='btn_type_url')
                ],
                [InlineKeyboardButton("❌ 取消", callback_data='admin_custom_buttons')]
            ]
            
            await update.message.reply_text(
                '➕ **添加自定义按钮 - 步骤 2/3**\n\n'
                f'按钮文字：{text}\n\n'
                '请选择按钮类型：',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            context.user_data['admin_waiting_for'] = None
            return True
        
        elif waiting_for == 'custom_button_message':
            # 步骤 3：保存消息内容，完成添加
            custom_button_data = context.user_data.get('custom_button_data', {})
            
            # 处理换行
            content = text.replace('\\n', '\n')
            
            # 添加按钮
            self.db.add_custom_button(
                custom_button_data['text'],
                'message',
                content
            )
            
            await update.message.reply_text(
                f'✅ **按钮已添加**\n\n'
                f'按钮文字：{custom_button_data["text"]}\n'
                f'类型：💬 消息\n\n'
                f'**内容预览：**\n{content}',
                parse_mode='HTML'
            )
            
            context.user_data['admin_waiting_for'] = None
            context.user_data['custom_button_data'] = None
            return True
        
        elif waiting_for == 'custom_button_url':
            # 步骤 3：保存链接，完成添加
            custom_button_data = context.user_data.get('custom_button_data', {})
            
            # 验证 URL
            if not text.startswith(('http://', 'https://', 't.me/')):
                await update.message.reply_text(
                    '❌ 链接格式错误！\n\n'
                    '链接必须以 `http://`、`https://` 或 `t.me/` 开头',
                    parse_mode='HTML'
                )
                return True
            
            # 添加按钮
            self.db.add_custom_button(
                custom_button_data['text'],
                'url',
                text
            )
            
            await update.message.reply_text(
                f'✅ **按钮已添加**\n\n'
                f'按钮文字：{custom_button_data["text"]}\n'
                f'类型：🔗 链接\n'
                f'链接：{text}',
                parse_mode='HTML'
            )
            
            context.user_data['admin_waiting_for'] = None
            context.user_data['custom_button_data'] = None
            return True
        
        return False
    
    async def handle_add_custom_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理添加自定义按钮输入"""
        text = update.message.text.strip()
        
        # 支持两种分隔符：--- 或 |
        separator = '---' if '---' in text else '|'
        
        if text.count(separator) < 2:
            await update.message.reply_text(
                '❌ 格式错误！\n\n'
                '正确格式：`按钮文字---类型---内容`\n'
                '或：`按钮文字|类型|内容`',
                parse_mode='HTML'
            )
            return
        
        parts = text.split(separator, 2)
        btn_text = parts[0].strip()
        btn_type = parts[1].strip()
        btn_content = parts[2].strip()
        
        # 处理 \n 转义（将 \\n 转换为真正的换行）
        btn_content = btn_content.replace('\\n', '\n')
        
        if btn_type not in ['message', 'url']:
            await update.message.reply_text('❌ 类型必须是 `message` 或 `url`', parse_mode='Markdown')
            return
        
        # 添加按钮
        self.db.add_custom_button(btn_text, btn_type, btn_content)
        
        await update.message.reply_text(
            f'✅ **按钮已添加**\n\n'
            f'按钮文字：{btn_text}\n'
            f'类型：{btn_type}\n'
            f'内容预览：\n{btn_content[:100]}{"..." if len(btn_content) > 100 else ""}',
            parse_mode='HTML'
        )
        
        context.user_data['admin_waiting_for'] = None
    
    async def _edit_start_message(self, query, context):
        """编辑主菜单文案"""
        current_message = self.db.get_setting('start_message')
        
        text = (
            '📝 **主菜单文案编辑**\n\n'
            '**当前文案：**\n'
            f'{current_message}\n\n'
            '点击下方按钮修改文案'
        )
        
        keyboard = [
            [InlineKeyboardButton("📝 修改文案", callback_data='admin_edit_start_text')],
            [InlineKeyboardButton("« 返回", callback_data='admin_back')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _edit_trc20_address(self, query, context):
        """编辑 TRC20 地址"""
        await query.edit_message_text(
            '📝 **修改 TRC20 收款地址**\n\n'
            '请发送新的 TRC20 地址：',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ 取消", callback_data='admin_settings')
            ]])
        )
        
        # 设置用户状态
        context.user_data['admin_waiting_for'] = 'trc20_address'
    
    async def _edit_start_text(self, query, context):
        """编辑主菜单文案"""
        await query.edit_message_text(
            '📝 **修改主菜单文案**\n\n'
            '请发送新的欢迎文案：',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ 取消", callback_data='admin_edit_start')
            ]])
        )
        
        # 设置用户状态
        context.user_data['admin_waiting_for'] = 'start_message'
    
    async def handle_admin_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理管理员消息（用于接收配置输入）"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            return False
        
        waiting_for = context.user_data.get('admin_waiting_for')
        
        if not waiting_for:
            return False
        
        text = update.message.text.strip()
        
        # 处理自定义按钮交互式输入
        if waiting_for in ['custom_button_text', 'custom_button_message', 'custom_button_url']:
            return await self.handle_custom_button_input(update, context)
        
        if waiting_for == 'notification_url':
            # 保存订单通知链接
            self.db.set_setting('order_notification_url', text)
            
            keyboard = [[InlineKeyboardButton("🔙 返回信息配置", callback_data='admin_info_config')]]
            
            await update.message.reply_text(
                f'✅ <b>订单通知链接已更新</b>\n\n'
                f'新链接：<code>{text}</code>\n\n'
                '修改已生效',
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            
            # 清除状态
            context.user_data['admin_waiting_for'] = None
            return True
        
        elif waiting_for == 'customer_service_url':
            # 保存官方客服链接
            self.db.set_setting('customer_service_url', text)
            
            keyboard = [[InlineKeyboardButton("🔙 返回信息配置", callback_data='admin_info_config')]]
            
            await update.message.reply_text(
                f'✅ <b>官方客服链接已更新</b>\n\n'
                f'新链接：<code>{text}</code>\n\n'
                '修改已生效',
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            
            # 清除状态
            context.user_data['admin_waiting_for'] = None
            return True
        
        elif waiting_for == 'trc20_address':
            # 验证 TRC20 地址格式
            if not text.startswith('T') or len(text) != 34:
                await update.message.reply_text('❌ TRC20 地址格式错误！地址应以 T 开头，长度为 34 位')
                return True
            
            # 保存地址
            self.db.set_setting('trc20_address', text)
            
            await update.message.reply_text(
                f'✅ **TRC20 地址已更新**\n\n'
                f'新地址：`{text}`\n\n'
                '修改已生效，无需重启',
                parse_mode='HTML'
            )
            
            # 清除状态
            context.user_data['admin_waiting_for'] = None
            return True
        
        elif waiting_for == 'start_message':
            # 保存欢迎文案
            self.db.set_setting('start_message', text)
            
            await update.message.reply_text(
                f'✅ **主菜单文案已更新**\n\n'
                f'新文案：\n{text}\n\n'
                '修改已生效，用户下次 /start 时将看到新文案',
                parse_mode='HTML'
            )
            
            # 清除状态
            context.user_data['admin_waiting_for'] = None
            return True
        
        elif waiting_for == 'add_custom_button':
            # 处理自定义按钮添加
            await self.handle_add_custom_button(update, context)
            return True
        
        return False
    
    async def _show_info_config(self, query, context):
        """显示信息配置菜单"""
        order_notification_url = self.db.get_setting('order_notification_url', 'https://t.me/your_channel')
        customer_service_url = self.db.get_setting('customer_service_url', 'https://t.me/id2uu')
        
        keyboard = [
            [InlineKeyboardButton("📢 订单通知链接", callback_data='admin_edit_notification')],
            [InlineKeyboardButton("👩🏻‍💻 官方客服链接", callback_data='admin_edit_customer_service')],
            [InlineKeyboardButton("🔙 返回", callback_data='admin_back')]
        ]
        
        text = (
            '<b>ℹ️ 信息配置</b>\n\n'
            f'<b>📢 订单通知链接：</b>\n<code>{order_notification_url}</code>\n\n'
            f'<b>👩🏻‍💻 官方客服链接：</b>\n<code>{customer_service_url}</code>\n\n'
            '💡 点击按钮修改配置'
        )
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    
    async def _edit_notification_url(self, query, context):
        """编辑订单通知链接"""
        await query.edit_message_text(
            '<b>📢 修改订单通知链接</b>\n\n'
            '请发送新的订单通知链接（支持@username或https://链接）：',
            parse_mode='HTML'
        )
        context.user_data['admin_waiting_for'] = 'notification_url'
    
    async def _edit_customer_service_url(self, query, context):
        """编辑官方客服链接"""
        await query.edit_message_text(
            '<b>👩🏻‍💻 修改官方客服链接</b>\n\n'
            '请发送新的官方客服链接（支持@username或https://链接）：',
            parse_mode='HTML'
        )
        context.user_data['admin_waiting_for'] = 'customer_service_url'
