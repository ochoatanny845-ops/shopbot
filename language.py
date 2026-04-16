"""
语言翻译模块 - Language Translation Module
支持中文和英文双语
"""

# 语言字典 - Language Dictionary
LANG = {
    'zh': {
        # ===== 主菜单 Main Menu =====
        'main_menu_title': '🤖 欢迎使用 Telegram 账号代购系统',
        'welcome_message': '👋 欢迎使用电报账号商城!\n\n📱 请选择服务:',
        'user_id_label': '用户ID',
        'your_id_label': '您的ID:',
        'current_balance': '当前余额:',
        'btn_products': '📱 Telegram账号购买',
        'product_types': 'tdata+session+api',
        'btn_recharge': '💰 充值',
        'btn_balance': '💳 余额',
        'btn_orders': '📦 我的订单',
        'btn_support': '👨‍💼 联系客服',
        'btn_language': '🌐 My Language',
        'btn_back': '🔙 返回',
        'btn_cancel': '❌ 取消',
        'btn_confirm': '✅ 确认',
        'btn_refresh': '🔄 刷新',
        
        # ===== 首次语言选择 First Language Selection =====
        'select_language': '🌐 请选择您的语言\nPlease select your language',
        'language_en': '🇺🇸 English',
        'language_zh': '🇨🇳 中文简体',
        'language_changed': '✅ 语言已切换为中文',
        'current_language': '当前语言',
        
        # ===== 分类 Categories =====
        'select_product_type': '📱 请选择商品类型：',
        'select_category': '选择账号国家或时间段:',
        'cat_asian': '🌏 亚洲国家',
        'cat_european': '🌍 欧美国家',
        'cat_african': '🌍 非洲国家',
        'cat_feb_may': '🛡 2月-5月',
        'cat_jun_dec': '⭐️ 6月-12月',
        'cat_1_2_year': '💎 1年-2年老号',
        'cat_3_4_year': '🔮 3年-4年老号',
        'cat_5plus_year': '👑 5年以上老号',
        'cat_7plus_year': '🌈七年以上适合当主号使用',
        'cat_vip': '💍会员号~VIP',
        'cat_fancy': '✨靓号5A~~9A（AAAAA连号）',
        
        # ===== 商品列表 Product List =====
        'product_info': '商品信息',
        'stock_label': '📦 库存',
        'products_available': '件商品',
        'product_list_title': '商品列表:',
        'total_products': '共',
        'pieces': '个',
        'enter_quantity_prompt': '💬 请输入购买数量',
        'available_quantity': '可用数量',
        'include': '包含:',
        'unit_price': '单价',
        'stock': '库存',
        'out_of_stock': '暂无库存',
        
        # ===== 购买流程 Purchase Process =====
        'btn_back_category': '🔙 返回分类',
        'btn_main_menu': '🏠 主菜单',
        'total_price_label': '💵 总价',
        'order_number_label': '📋 订单号',
        'product_label': '🛍 商品',
        'quantity_label': '📦 数量',
        'enter_quantity': '请输入购买数量:',
        'processing_order': '⏳ 订单处理中...',
        'checking_accounts': '♻️ 正在打包检查账号存活，请耐心稍候...',
        'product': '🛍 商品',
        'unit_price_label': '💰 单价',
        'quantity': '📦 数量',
        'total_price': '💵 总价',
        'order_id': '📋 订单号',
        'purchase_product': '🗂 购买商品',
        'product_price': '💰 商品价格',
        'purchase_quantity': '🛍 购买数量',
        'files_packaged': '🗂文件打包完成 ♻️存活账号',
        'insufficient_balance': '余额不足',
        'need_recharge': '需要充值:',
        'recharge_cancelled': '已取消充值订单',
        'order_not_found_or_processed': '订单不存在或已处理',
        
        # ===== 充值模块 Recharge Module =====
        'select_recharge_method_title': '💰 选择充值方式',
        'trc20_method_title': '💎 USDT TRC20 充值',
        'trc20_method_desc_1': '去中心化，资金直达',
        'trc20_method_desc_2': '到账时间：1-3 分钟',
        'trc20_method_desc_3': '需要复制交易哈希验证',
        'okpay_method_title': '⚡ OKPay 快速充值',
        'okpay_method_desc_1': '支付即到账，无需等待',
        'okpay_method_desc_2': '到账时间：秒到',
        'okpay_method_desc_3': '一键支付，自动确认',
        'minimum_recharge_notice': '最低充值：1 USDT',
        'minimum_recharge_warning': '⚠️ 最低充值：1 USDT',
        'enter_recharge_amount_prompt': '⚠️ 充值金额不能为空，请重新输入充值金额',
        'enter_amount_example': '💵 输入充值金额，例如：10',
        'trc20_recharge_instructions_title': '💎 USDT TRC20 充值',
        'recharge_address_notice': '📋 充值地址',
        'recharge_amount_notice': '💵 充值金额',
        'copy_address': '📋 复制地址',
        'notes_title': '⚠️ 注意事项',
        'trc20_note_exact_amount': '转账金额务必精确到',
        'trc20_note_use_trc20': '请使用 USDT-TRC20 转账',
        'trc20_note_auto_detect': '转账后系统将自动检测并到账',
        'trc20_note_copy_hash': '到账后复制 交易哈希(TxID) 提交验证',
        'confirm_payment_button': '✅ 我已转账，提交验证',
        'cancel_recharge_button': '❌ 取消充值',
        'payment_verification_title': '💎 支付验证',
        'enter_tx_hash_prompt': '📝 请输入交易哈希 (TxID):',
        'tx_hash_example': '例如: 1a2b3c4d5e6f...',
        'verifying_payment': '⏳ 正在验证支付...',
        'payment_success': '✅ 支付验证成功！',
        'recharge_completed': '充值已到账',
        'payment_failed': '❌ 验证失败',
        'payment_not_found': '未找到该交易',
        'amount_mismatch': '金额不匹配',
        'already_used': '该交易已使用',
        'okpay_recharge_title': '⚡ OKPay 快速充值',
        'okpay_minimum_notice': '⚠️ 最低充值：5 USDT',
        'okpay_enter_amount_example': '💵 输入充值金额(≥5),例如：10',
        'okpay_payment_link_title': '⚡ OKPay 支付链接',
        'okpay_click_to_pay': '🔗 点击下方链接完成支付',
        'okpay_auto_confirm': '✅ 支付完成后会自动到账',
        'open_payment_link': '🔗 打开支付链接',
        'recharge_input_amount_title': '💰 请输入充值金额',
        'okpay_order_title': '⚡ OKPay 充值订单',
        'order_number_prefix': '订单号:',
        'recharge_amount_prefix': '充值金额:',
        'validity_period': '有效期:',
        'expiry_time': '过期时间:',
        'operation_steps': '💡 操作步骤:',
        'step_1_click_pay': '1️⃣ 点击"💰 点击支付"按钮',
        'step_2_complete_payment': '2️⃣ 在 OKPay 中完成支付',
        'step_3_click_confirmed': '3️⃣ 返回这里点击"✅ 我已支付"',
        'step_4_auto_arrival': '4️⃣ 系统查询订单后自动到账',
        'payment_reminder': '⚠️ 支付完成后必须点击"我已支付"才能到账',
        'btn_click_to_pay': '💰 点击支付',
        'btn_i_have_paid': '✅ 我已支付',
        'querying_order_status': '🔍 正在查询订单状态...',
        'recharge_success_title': '✅ 充值成功！',
        'arrival_time': '到账时间:',
        'current_balance_prefix': '当前余额:',
        'minutes_suffix': '分钟',
        'trc20_order_title': '💰 充值订单',
        'network_type': '网络类型:',
        'recipient_address_label': '收款地址:',
        'order_time': '⏰ 订单时间:',
        'created_time': '创建时间:',
        'expire_time_label': '过期时间:',
        'validity_period_label': '有效期:',
        'important_reminder': '⚠️ 重要提示:',
        'trc20_reminder_1': '1️⃣ 请确保使用 TRC20 网络',
        'trc20_reminder_2': '2️⃣ 转账完成后，发送交易哈希（TxID）',
        'trc20_reminder_3': '3️⃣ 系统将自动验证并入账',
        'trc20_reminder_4': '4️⃣ 超过 10 分钟订单自动失效',
        'tx_hash_format_example': '📝 交易哈希格式示例:',
        'tip_after_transfer': '💰 请完成转账后，发送交易哈希（TxID）给我',
        'tip_copy_in_wallet': '💡 在钱包中复制交易哈希即可',
        'tip_submit_before': '⏰ 请在',
        'tip_submit_suffix': '前提交',
        'cancel_recharge_btn': '❌ 取消充值',
        
        # ===== 使用说明 Usage Instructions =====
        'protocol_note': '📄 协议号: 适用于软件或脚本',
        'direct_login_note': '🗂 直登号: 适用于在电脑直接登入',
        'api_link_note': '📎 Api链接: 适用于在网页上接收验证码以登录其他设备',
        'cache_cleared': '✅ 所有账号均已删除缓存',
        'keep_files_safe': '⚠️ 请妥善保管好您的文件',
        
        # ===== 充值 Recharge =====
        'recharge_title': '💰 充值',
        'select_recharge_method': '请选择充值方式:',
        'trc20_recharge': '💳 USDT TRC20 充值',
        'okpay_recharge': '⚡ OKPay 快速充值',
        'enter_amount': '💵 请输入充值金额 (USDT):',
        'minimum_recharge': '💵 最低充值',
        'recharge_address': '充值地址',
        'recharge_amount': '充值金额',
        'waiting_payment': '⏳ 等待到账',
        'recharge_success': '✅ 充值成功',
        'recharge_failed': '❌ 充值失败',
        
        # TRC20 充值详情
        'trc20_recharge_title': '💳 **USDT TRC20 充值**',
        'recharge_address_label': '📋 充值地址',
        'recharge_amount_label': '💵 充值金额',
        'notes_label': '⚠️ 注意事项',
        'trc20_note_1': '1️⃣ 请使用 **USDT-TRC20** 转账',
        'trc20_note_2': '2️⃣ 转账金额务必精确到 **{amount} USDT**',
        'trc20_note_3': '3️⃣ 转账后系统将自动检测并到账',
        'arrival_time': '🔄 到账时间',
        'arrival_time_desc': '通常 1-5 分钟',
        'monitoring_transfer': '🔍 正在监控转账,请稍候...',
        
        # OKPay 充值详情
        'okpay_recharge_title': '⚡ **OKPay 快速充值**',
        'actual_payment': '💰 实际支付',
        'exchange_rate': '汇率',
        'operation_steps': '📋 操作步骤',
        'okpay_step_1': '1️⃣ 点击下方 "前往 OKPay 支付" 按钮',
        'okpay_step_2': '2️⃣ 在打开的页面完成支付',
        'okpay_step_3': '3️⃣ **支付成功后点击"检查 支付状态"**',
        'okpay_reminder': '⚠️ 请在支付完成后点击"检查 支付状态"按钮',
        'goto_okpay': '💳 前往 OKPay 支付',
        'check_payment': '✅ 检查 支付状态',
        'cancel_recharge': '❌ 取消 充值',
        
        # 充值状态
        'recharge_success_title': '✅ 充值成功!',
        'recharged_amount': '💰 充值金额',
        'thank_you': '🎉 感谢使用!祝您购物愉快 🛍️',
        'invalid_verification_code': '❌ 验证码格式错误,请输入6位"数字"码',
        'tx_hash_used': '❌ 该交易哈希已被使用',
        'verifying_transaction': '🔍 正在验证交易，请稍候...',
        'order_not_found': '❌ 订单不存在',
        'checking_order_status': '🔍 正在查询订单状态...',
        
        # ===== 余额 Balance =====
        'balance_title': '💳 余额',
        'current_balance': '当前余额',
        'recharge_history': '充值历史',
        'spending_history': '消费记录',
        'no_records': '暂无记录',
        
        # ===== 订单 Orders =====
        'orders_title': '📦 我的订单',
        'order_id_label': '🆔 订单号',
        'time': '📅 时间',
        'product_label': '🛍 商品',
        'quantity_label': '📦 数量',
        'amount': '💵 金额',
        'status': '📊 状态',
        'status_processing': '⏳ 处理中',
        'status_completed': '✅ 已完成',
        'status_failed': '❌ 已失败',
        'status_refunded': '💰 已退款',
        'no_orders': '暂无订单',
        'view_details': '📄 查看详情',
        
        # ===== 错误提示 Error Messages =====
        'enter_between': '请输入',
        'invalid_number': '❌ 请输入有效的数字',
        'minimum_recharge_error': '❌ 最低充值金额为 1 USDT',
        'no_pending_order': '❌ 未找到待充值的订单，请先点击"充值"按钮',
        'insufficient_balance': '❌ 余额不足，请先充值',
        'out_of_stock_error': '❌ 库存不足，无法购买',
        'purchase_failed': '❌ 购买失败',
        'recharge_failed_error': '❌ 充值失败',
        'invalid_quantity': '❌ 无效的数量，请输入正整数',
        'quantity_exceeds_stock': '❌ 数量超出库存',
        'invalid_amount': '❌ 金额格式错误，请输入有效的数字',
        'amount_below_minimum': '❌ 充值金额低于最低限制',
        'error_occurred': '❌ 操作失败',
        
        # ===== 成功提示 Success Messages =====
        'purchase_success': '✅ 购买成功',
        'recharge_success_msg': '✅ 充值成功',
        'order_completed': '✅ 订单已完成',
        'operation_success': '✅ 操作成功',
        
        # ===== 其他 Others =====
        'loading': '⏳ 加载中...',
        'please_wait': '请稍候...',
        'yes': '是',
        'no': '否',
        'unknown': '未知',
    },
    
    'en': {
        # ===== Main Menu =====
        'main_menu_title': '🤖 Welcome to Telegram Account Store',
        'welcome_message': '👋 Welcome to Telegram Account Store!\n\n📱 Please select service:',
        'user_id_label': 'User ID',
        'your_id_label': 'Your ID:',
        'current_balance': 'Current Balance:',
        'btn_products': '📱 Telegram Accounts',
        'product_types': 'tdata+session+api',
        'btn_recharge': '💰 Recharge',
        'btn_balance': '💳 Balance',
        'btn_orders': '📦 My Orders',
        'btn_support': '👨‍💼 Contact Support',
        'btn_language': '🌐 My Language',
        'btn_back': '🔙 Back',
        'btn_cancel': '❌ Cancel',
        'btn_confirm': '✅ Confirm',
        'btn_refresh': '🔄 Refresh',
        
        # ===== First Language Selection =====
        'select_language': '🌐 Please select your language\n请选择您的语言',
        'language_en': '🇺🇸 English',
        'language_zh': '🇨🇳 中文简体',
        'language_changed': '✅ Language changed to English',
        'current_language': 'Current Language',
        
        # ===== Categories =====
        'select_product_type': '📱 Please select product type:',
        'select_category': 'Select account country or time period:',
        'cat_asian': '🌏 Asian Countries',
        'cat_european': '🌍 European & American',
        'cat_african': '🌍 African Countries',
        'cat_feb_may': '🛡 February-May',
        'cat_jun_dec': '⭐️ June-December',
        'cat_1_2_year': '💎 1-2 Year Old',
        'cat_3_4_year': '🔮 3-4 Year Old',
        'cat_5plus_year': '👑 5+ Year Old',
        'cat_7plus_year': '🌈 7+ Year (Main Account)',
        'cat_vip': '💍 VIP Membership',
        'cat_fancy': '✨ Premium Numbers (5A-9A)',
        
        # ===== Product List =====
        'product_info': 'Product Info',
        'stock_label': '📦 Stock',
        'products_available': 'products available',
        'product_list_title': 'Product List:',
        'total_products': 'Total',
        'pieces': 'pcs',
        'enter_quantity_prompt': '💬 Enter purchase quantity',
        'available_quantity': 'Available Quantity',
        'include': 'include:',
        'unit_price': 'Unit Price',
        'stock': 'Stock',
        'out_of_stock': 'Out of Stock',
        
        # ===== Purchase Process =====
        'btn_back_category': '🔙 Back to Categories',
        'btn_main_menu': '🏠 Main Menu',
        'total_price_label': '💵 Total',
        'order_number_label': '📋 Order Number',
        'product_label': '🛍 Product',
        'quantity_label': '📦 Quantity',
        'enter_quantity': 'Please enter purchase quantity:',
        'processing_order': '⏳ Processing Order...',
        'checking_accounts': '♻️ Packaging and checking account status, please wait...',
        'product': '🛍 Product',
        'unit_price_label': '💰 Unit Price',
        'quantity': '📦 Quantity',
        'total_price': '💵 Total',
        'order_id': '📋 Order ID',
        'insufficient_balance': 'Insufficient Balance',
        'need_recharge': 'Need Recharge:',
        'recharge_cancelled': 'Recharge order cancelled',
        'order_not_found_or_processed': 'Order not found or already processed',
        
        # ===== Recharge Module =====
        'select_recharge_method_title': '💰 Select Recharge Method',
        'trc20_method_title': '💎 USDT TRC20 Recharge',
        'trc20_method_desc_1': 'Decentralized, direct transfer',
        'trc20_method_desc_2': 'Arrival time: 1-3 minutes',
        'trc20_method_desc_3': 'Need to copy transaction hash for verification',
        'okpay_method_title': '⚡ OKPay Quick Recharge',
        'okpay_method_desc_1': 'Instant arrival after payment',
        'okpay_method_desc_2': 'Arrival time: Instant',
        'okpay_method_desc_3': 'One-click payment, auto confirmation',
        'minimum_recharge_notice': 'Minimum recharge: 1 USDT',
        'minimum_recharge_warning': '⚠️ Minimum recharge: 1 USDT',
        'enter_recharge_amount_prompt': '⚠️ Amount cannot be empty, please re-enter',
        'enter_amount_example': '💵 Enter amount, e.g.: 10',
        'trc20_recharge_instructions_title': '💎 USDT TRC20 Recharge',
        'recharge_address_notice': '📋 Recharge Address',
        'recharge_amount_notice': '💵 Recharge Amount',
        'copy_address': '📋 Copy Address',
        'notes_title': '⚠️ Important Notes',
        'trc20_note_exact_amount': 'Transfer amount must be exact',
        'trc20_note_use_trc20': 'Please use USDT-TRC20 network',
        'trc20_note_auto_detect': 'System will auto-detect after transfer',
        'trc20_note_copy_hash': 'Copy Transaction Hash (TxID) after arrival',
        'confirm_payment_button': '✅ I have transferred, submit verification',
        'cancel_recharge_button': '❌ Cancel Recharge',
        'payment_verification_title': '💎 Payment Verification',
        'enter_tx_hash_prompt': '📝 Enter Transaction Hash (TxID):',
        'tx_hash_example': 'e.g.: 1a2b3c4d5e6f...',
        'verifying_payment': '⏳ Verifying payment...',
        'payment_success': '✅ Payment verified!',
        'recharge_completed': 'Recharge completed',
        'payment_failed': '❌ Verification failed',
        'payment_not_found': 'Transaction not found',
        'amount_mismatch': 'Amount mismatch',
        'already_used': 'Transaction already used',
        'okpay_recharge_title': '⚡ OKPay Quick Recharge',
        'okpay_minimum_notice': '⚠️ Minimum recharge: 5 USDT',
        'okpay_enter_amount_example': '💵 Enter amount (≥5), e.g.: 10',
        'okpay_payment_link_title': '⚡ OKPay Payment Link',
        'okpay_click_to_pay': '🔗 Click link below to complete payment',
        'okpay_auto_confirm': '✅ Auto arrival after payment',
        'open_payment_link': '🔗 Open Payment Link',
        'recharge_input_amount_title': '💰 Enter Recharge Amount',
        'okpay_order_title': '⚡ OKPay Recharge Order',
        'order_number_prefix': 'Order Number:',
        'recharge_amount_prefix': 'Recharge Amount:',
        'validity_period': 'Valid for:',
        'expiry_time': 'Expires at:',
        'operation_steps': '💡 Steps:',
        'step_1_click_pay': '1️⃣ Click "💰 Click to Pay" button',
        'step_2_complete_payment': '2️⃣ Complete payment in OKPay',
        'step_3_click_confirmed': '3️⃣ Return here and click "✅ I have paid"',
        'step_4_auto_arrival': '4️⃣ System will auto-credit after query',
        'payment_reminder': '⚠️ Must click "I have paid" after payment',
        'btn_click_to_pay': '💰 Click to Pay',
        'btn_i_have_paid': '✅ I have paid',
        'querying_order_status': '🔍 Querying order status...',
        'recharge_success_title': '✅ Recharge Successful!',
        'arrival_time': 'Arrival time:',
        'current_balance_prefix': 'Current balance:',
        'minutes_suffix': 'minutes',
        'trc20_order_title': '💰 Recharge Order',
        'network_type': 'Network:',
        'recipient_address_label': 'Recipient Address:',
        'order_time': '⏰ Order Time:',
        'created_time': 'Created:',
        'expire_time_label': 'Expires:',
        'validity_period_label': 'Valid for:',
        'important_reminder': '⚠️ Important:',
        'trc20_reminder_1': '1️⃣ Ensure using TRC20 network',
        'trc20_reminder_2': '2️⃣ Send Transaction Hash (TxID) after transfer',
        'trc20_reminder_3': '3️⃣ System will auto-verify and credit',
        'trc20_reminder_4': '4️⃣ Order expires after 10 minutes',
        'tx_hash_format_example': '📝 TxID format example:',
        'tip_after_transfer': '💰 Please send Transaction Hash (TxID) after transfer',
        'tip_copy_in_wallet': '💡 Copy transaction hash in your wallet',
        'tip_submit_before': '⏰ Please submit before',
        'tip_submit_suffix': '',
        'cancel_recharge_btn': '❌ Cancel Recharge',
        
        'purchase_product': '🗂 Purchase Product',
        'product_price': '💰 Product Price',
        'purchase_quantity': '🛍 Purchase Quantity',
        'files_packaged': '🗂 File packaged ♻️ Active accounts',
        
        # ===== Usage Instructions =====
        'protocol_note': '📄 Protocol: For software or scripts',
        'direct_login_note': '🗂 Direct Login: For direct computer login',
        'api_link_note': '📎 API Link: For receiving verification codes on web pages to login to other devices',
        'cache_cleared': '✅ All accounts have cache cleared',
        'keep_files_safe': '⚠️ Please keep your files safe',
        
        # ===== Recharge =====
        'recharge_title': '💰 Recharge',
        'select_recharge_method': 'Please select recharge method:',
        'trc20_recharge': '💳 USDT TRC20 Recharge',
        'okpay_recharge': '⚡ OKPay Fast Recharge',
        'enter_amount': '💵 Please enter recharge amount (USDT):',
        'minimum_recharge': '💵 Minimum recharge',
        'recharge_address': 'Recharge Address',
        'recharge_amount': 'Recharge Amount',
        'waiting_payment': '⏳ Waiting for payment',
        'recharge_success': '✅ Recharge successful',
        'recharge_failed': '❌ Recharge failed',
        
        # TRC20 Recharge Details
        'trc20_recharge_title': '💳 **USDT TRC20 Recharge**',
        'recharge_address_label': '📋 Recharge Address',
        'recharge_amount_label': '💵 Recharge Amount',
        'notes_label': '⚠️ Important Notes',
        'trc20_note_1': '1️⃣ Please use **USDT-TRC20** transfer',
        'trc20_note_2': '2️⃣ Transfer amount must be exactly **{amount} USDT**',
        'trc20_note_3': '3️⃣ System will auto-detect and credit after transfer',
        'arrival_time': '🔄 Arrival Time',
        'arrival_time_desc': 'Usually 1-5 minutes',
        'monitoring_transfer': '🔍 Monitoring transfer, please wait...',
        
        # OKPay Recharge Details
        'okpay_recharge_title': '⚡ **OKPay Fast Recharge**',
        'actual_payment': '💰 Actual Payment',
        'exchange_rate': 'Exchange Rate',
        'operation_steps': '📋 Operation Steps',
        'okpay_step_1': '1️⃣ Click "Go to OKPay" button below',
        'okpay_step_2': '2️⃣ Complete payment on the opened page',
        'okpay_step_3': '3️⃣ **Click "Check Payment Status" after payment**',
        'okpay_reminder': '⚠️ Please click "Check Payment Status" button after completing payment',
        'goto_okpay': '💳 Go to OKPay',
        'check_payment': '✅ Check Payment Status',
        'cancel_recharge': '❌ Cancel Recharge',
        
        # Recharge Status
        'recharge_success_title': '✅ Recharge Successful!',
        'recharged_amount': '💰 Recharged Amount',
        'thank_you': '🎉 Thank you! Happy shopping 🛍️',
        'invalid_verification_code': '❌ Invalid verification code, please enter 6-digit code',
        'tx_hash_used': '❌ This transaction hash has been used',
        'verifying_transaction': '🔍 Verifying transaction, please wait...',
        'order_not_found': '❌ Order not found',
        'checking_order_status': '🔍 Checking order status...',
        
        # ===== Balance =====
        'balance_title': '💳 Balance',
        'current_balance': 'Current Balance',
        'recharge_history': 'Recharge History',
        'spending_history': 'Spending History',
        'no_records': 'No records',
        
        # ===== Orders =====
        'orders_title': '📦 My Orders',
        'order_id_label': '🆔 Order ID',
        'time': '📅 Time',
        'product_label': '🛍 Product',
        'quantity_label': '📦 Quantity',
        'amount': '💵 Amount',
        'status': '📊 Status',
        'status_processing': '⏳ Processing',
        'status_completed': '✅ Completed',
        'status_failed': '❌ Failed',
        'status_refunded': '💰 Refunded',
        'no_orders': 'No orders',
        'view_details': '📄 View Details',
        
        # ===== Error Messages =====
        'enter_between': 'Please enter',
        'invalid_number': '❌ Please enter a valid number',
        'minimum_recharge_error': '❌ Minimum recharge amount is 1 USDT',
        'no_pending_order': '❌ No pending order found, please click "Recharge" button first',
        'insufficient_balance': '❌ Insufficient balance, please recharge first',
        'out_of_stock_error': '❌ Out of stock, cannot purchase',
        'purchase_failed': '❌ Purchase failed',
        'recharge_failed_error': '❌ Recharge failed',
        'invalid_quantity': '❌ Invalid quantity, please enter a positive integer',
        'quantity_exceeds_stock': '❌ Quantity exceeds stock',
        'invalid_amount': '❌ Invalid amount format, please enter a valid number',
        'amount_below_minimum': '❌ Amount below minimum recharge limit',
        'error_occurred': '❌ Operation failed',
        
        # ===== Success Messages =====
        'purchase_success': '✅ Purchase successful',
        'recharge_success_msg': '✅ Recharge successful',
        'order_completed': '✅ Order completed',
        'operation_success': '✅ Operation successful',
        
        # ===== Others =====
        'loading': '⏳ Loading...',
        'please_wait': 'Please wait...',
        'yes': 'Yes',
        'no': 'No',
        'unknown': 'Unknown',
    }
}

# 国家名称翻译字典 - Country Name Translation Dictionary (210+ countries/regions)
COUNTRY_NAMES = {
    'zh_to_en': {
        # ===== 亚洲 (51个) =====
        '中国': 'China',
        '日本': 'Japan',
        '韩国': 'South Korea',
        '朝鲜': 'North Korea',
        '蒙古': 'Mongolia',
        '越南': 'Vietnam',
        '老挝': 'Laos',
        '柬埔寨': 'Cambodia',
        '泰国': 'Thailand',
        '缅甸': 'Myanmar',
        '马来西亚': 'Malaysia',
        '新加坡': 'Singapore',
        '印度尼西亚': 'Indonesia',
        '文莱': 'Brunei',
        '菲律宾': 'Philippines',
        '东帝汶': 'East Timor',
        '印度': 'India',
        '巴基斯坦': 'Pakistan',
        '孟加拉': 'Bangladesh',
        '孟加拉国': 'Bangladesh',
        '斯里兰卡': 'Sri Lanka',
        '马尔代夫': 'Maldives',
        '尼泊尔': 'Nepal',
        '不丹': 'Bhutan',
        '阿富汗': 'Afghanistan',
        '伊朗': 'Iran',
        '伊拉克': 'Iraq',
        '叙利亚': 'Syria',
        '约旦': 'Jordan',
        '黎巴嫩': 'Lebanon',
        '以色列': 'Israel',
        '巴勒斯坦': 'Palestine',
        '沙特阿拉伯': 'Saudi Arabia',
        '沙特': 'Saudi Arabia',
        '也门': 'Yemen',
        '阿曼': 'Oman',
        '阿联酋': 'UAE',
        '阿拉伯联合酋长国': 'UAE',
        '卡塔尔': 'Qatar',
        '巴林': 'Bahrain',
        '科威特': 'Kuwait',
        '土耳其': 'Turkey',
        '塞浦路斯': 'Cyprus',
        '格鲁吉亚': 'Georgia',
        '亚美尼亚': 'Armenia',
        '阿塞拜疆': 'Azerbaijan',
        '哈萨克斯坦': 'Kazakhstan',
        '乌兹别克斯坦': 'Uzbekistan',
        '土库曼斯坦': 'Turkmenistan',
        '吉尔吉斯斯坦': 'Kyrgyzstan',
        '吉尔吉斯坦': 'Kyrgyzstan',
        '塔吉克斯坦': 'Tajikistan',
        '塔吉克': 'Tajikistan',
        '香港': 'Hong Kong',
        '澳门': 'Macau',
        '台湾': 'Taiwan',
        
        # ===== 欧洲 (47个) =====
        '英国': 'United Kingdom',
        '爱尔兰': 'Ireland',
        '法国': 'France',
        '德国': 'Germany',
        '荷兰': 'Netherlands',
        '比利时': 'Belgium',
        '卢森堡': 'Luxembourg',
        '瑞士': 'Switzerland',
        '奥地利': 'Austria',
        '列支敦士登': 'Liechtenstein',
        '摩纳哥': 'Monaco',
        '西班牙': 'Spain',
        '葡萄牙': 'Portugal',
        '安道尔': 'Andorra',
        '意大利': 'Italy',
        '圣马力诺': 'San Marino',
        '梵蒂冈': 'Vatican',
        '马耳他': 'Malta',
        '希腊': 'Greece',
        '挪威': 'Norway',
        '瑞典': 'Sweden',
        '芬兰': 'Finland',
        '丹麦': 'Denmark',
        '冰岛': 'Iceland',
        '波兰': 'Poland',
        '捷克': 'Czech Republic',
        '捷克共和国': 'Czech Republic',
        '斯洛伐克': 'Slovakia',
        '匈牙利': 'Hungary',
        '罗马尼亚': 'Romania',
        '保加利亚': 'Bulgaria',
        '塞尔维亚': 'Serbia',
        '克罗地亚': 'Croatia',
        '斯洛文尼亚': 'Slovenia',
        '波黑': 'Bosnia and Herzegovina',
        '波斯尼亚': 'Bosnia and Herzegovina',
        '波斯尼亚和黑塞哥维那': 'Bosnia and Herzegovina',
        '黑山': 'Montenegro',
        '北马其顿': 'North Macedonia',
        '马其顿': 'North Macedonia',
        '阿尔巴尼亚': 'Albania',
        '科索沃': 'Kosovo',
        '爱沙尼亚': 'Estonia',
        '拉脱维亚': 'Latvia',
        '立陶宛': 'Lithuania',
        '白俄罗斯': 'Belarus',
        '乌克兰': 'Ukraine',
        '摩尔多瓦': 'Moldova',
        '俄罗斯': 'Russia',
        
        # ===== 非洲 (57个) =====
        '埃及': 'Egypt',
        '利比亚': 'Libya',
        '突尼斯': 'Tunisia',
        '阿尔及利亚': 'Algeria',
        '摩洛哥': 'Morocco',
        '苏丹': 'Sudan',
        '南苏丹': 'South Sudan',
        '埃塞俄比亚': 'Ethiopia',
        '厄立特里亚': 'Eritrea',
        '索马里': 'Somalia',
        '吉布提': 'Djibouti',
        '肯尼亚': 'Kenya',
        '坦桑尼亚': 'Tanzania',
        '乌干达': 'Uganda',
        '卢旺达': 'Rwanda',
        '布隆迪': 'Burundi',
        '塞舌尔': 'Seychelles',
        '毛里求斯': 'Mauritius',
        '科摩罗': 'Comoros',
        '马达加斯加': 'Madagascar',
        '赞比亚': 'Zambia',
        '津巴布韦': 'Zimbabwe',
        '马拉维': 'Malawi',
        '莫桑比克': 'Mozambique',
        '博茨瓦纳': 'Botswana',
        '纳米比亚': 'Namibia',
        '南非': 'South Africa',
        '斯威士兰': 'Eswatini',
        '莱索托': 'Lesotho',
        '安哥拉': 'Angola',
        '刚果民主共和国': 'DR Congo',
        '刚果金': 'DR Congo',
        '刚果': 'Congo',
        '刚果共和国': 'Republic of Congo',
        '加蓬': 'Gabon',
        '赤道几内亚': 'Equatorial Guinea',
        '圣多美和普林西比': 'Sao Tome and Principe',
        '喀麦隆': 'Cameroon',
        '尼日利亚': 'Nigeria',
        '尼日尔': 'Niger',
        '乍得': 'Chad',
        '中非': 'Central African Republic',
        '中非共和国': 'Central African Republic',
        '贝宁': 'Benin',
        '多哥': 'Togo',
        '加纳': 'Ghana',
        '布基纳法索': 'Burkina Faso',
        '科特迪瓦': 'Ivory Coast',
        '利比里亚': 'Liberia',
        '塞拉利昂': 'Sierra Leone',
        '几内亚': 'Guinea',
        '几内亚比绍': 'Guinea-Bissau',
        '冈比亚': 'Gambia',
        '塞内加尔': 'Senegal',
        '马里': 'Mali',
        '毛里塔尼亚': 'Mauritania',
        '西撒哈拉': 'Western Sahara',
        '佛得角': 'Cape Verde',
        
        # ===== 北美洲 (28个) =====
        '美国': 'United States',
        '加拿大': 'Canada',
        '墨西哥': 'Mexico',
        '危地马拉': 'Guatemala',
        '伯利兹': 'Belize',
        '萨尔瓦多': 'El Salvador',
        '洪都拉斯': 'Honduras',
        '尼加拉瓜': 'Nicaragua',
        '哥斯达黎加': 'Costa Rica',
        '巴拿马': 'Panama',
        '巴哈马': 'Bahamas',
        '古巴': 'Cuba',
        '牙买加': 'Jamaica',
        '海地': 'Haiti',
        '多米尼加': 'Dominican Republic',
        '多米尼加共和国': 'Dominican Republic',
        '圣基茨和尼维斯': 'Saint Kitts and Nevis',
        '安提瓜和巴布达': 'Antigua and Barbuda',
        '多米尼克': 'Dominica',
        '圣卢西亚': 'Saint Lucia',
        '圣文森特和格林纳丁斯': 'Saint Vincent and the Grenadines',
        '格林纳达': 'Grenada',
        '巴巴多斯': 'Barbados',
        '特立尼达和多巴哥': 'Trinidad and Tobago',
        '波多黎各': 'Puerto Rico',
        '格陵兰': 'Greenland',
        '百慕大': 'Bermuda',
        '马提尼克': 'Martinique',
        '瓜德罗普': 'Guadeloupe',
        
        # ===== 南美洲 (13个) =====
        '哥伦比亚': 'Colombia',
        '委内瑞拉': 'Venezuela',
        '圭亚那': 'Guyana',
        '苏里南': 'Suriname',
        '法属圭亚那': 'French Guiana',
        '巴西': 'Brazil',
        '秘鲁': 'Peru',
        '厄瓜多尔': 'Ecuador',
        '玻利维亚': 'Bolivia',
        '智利': 'Chile',
        '阿根廷': 'Argentina',
        '乌拉圭': 'Uruguay',
        '巴拉圭': 'Paraguay',
        
        # ===== 大洋洲 (14个) =====
        '澳大利亚': 'Australia',
        '新西兰': 'New Zealand',
        '巴布亚新几内亚': 'Papua New Guinea',
        '斐济': 'Fiji',
        '所罗门群岛': 'Solomon Islands',
        '瓦努阿图': 'Vanuatu',
        '萨摩亚': 'Samoa',
        '汤加': 'Tonga',
        '基里巴斯': 'Kiribati',
        '图瓦卢': 'Tuvalu',
        '瑙鲁': 'Nauru',
        '帕劳': 'Palau',
        '密克罗尼西亚': 'Micronesia',
        '马绍尔群岛': 'Marshall Islands',
    }
}

def get_text(key, lang='zh'):
    """
    获取翻译文本
    Get translated text
    
    Args:
        key: 文本键名 Text key
        lang: 语言代码 ('zh' or 'en')
    
    Returns:
        str: 翻译后的文本 Translated text
    """
    return LANG.get(lang, LANG['zh']).get(key, key)

def translate_country_name(name, target_lang='zh'):
    """
    翻译国家名称
    Translate country name
    
    Args:
        name: 国家名称 Country name
        target_lang: 目标语言 ('zh' or 'en')
    
    Returns:
        str: 翻译后的国家名 Translated country name
    """
    if target_lang == 'zh':
        return name  # 中文保持原样 Keep Chinese as is
    
    # 英文：替换国家名 English: Replace country name
    return COUNTRY_NAMES['zh_to_en'].get(name, name)

def translate_product_name(product_name, target_lang='zh'):
    """
    翻译商品名称中的国家名和描述
    Translate country name and description in product name
    
    Args:
        product_name: 商品名称 Product name (e.g., "🇲🇲+95缅甸-5年以上老号 [26118] - $0.33")
        target_lang: 目标语言 ('zh' or 'en')
    
    Returns:
        str: 翻译后的商品名 Translated product name
    """
    if target_lang == 'zh':
        return product_name  # 中文保持原样 Keep Chinese as is
    
    result = product_name
    
    # 英文：先替换商品描述（按长度从长到短排序，避免部分匹配）
    description_map = {
        # 特殊长描述
        '数字1的随机5A靓号': 'Random 5A Premium (starts with 1)',
        '会员VIP（盲盒低于两天可退换）': 'VIP (Blind Box, Refundable <2 days)',
        '2-5月联系人受限少量测': '2-5 Month (Limited Contacts)',
        '11年以上老号（2014年）': '11+ Year Old (2014)',
        '最少11年以上（2014年）老号': 'Min 11+ Year (2014)',
        '2014年（11年以上老号）': '2014 (11+ Year)',
        '7年以上适合当主号使用': '7+ Year (Main Account)',
        '实卡（真机注册）': 'Real SIM (Real Device)',
        '精品月号40天+': 'Premium Monthly 40+Days',
        
        # 年份+老号组合
        '10年以上老号': '10+ Year Old',
        '11年以上老号': '11+ Year Old',
        '9年以上老号': '9+ Year Old',
        '8年以上老号': '8+ Year Old',
        '7年以上老号': '7+ Year Old',
        '6年以上老号': '6+ Year Old',
        '5年以上老号': '5+ Year Old',
        '3-4年以上': '3-4 Year Old',
        '3年-4年老号': '3-4 Year Old',
        '3-4年老号': '3-4 Year Old',
        '1年-2年老号': '1-2 Year Old',
        '1-2年老号': '1-2 Year Old',
        
        # 月份描述
        '6-12月': '6-12 Month',
        '6月-12月': '6-12 Month',
        '6-12个月': '6-12 Month',
        '2-5月': '2-5 Month',
        '2月-5月': '2-5 Month',
        '2-5个月': '2-5 Month',
        
        # 特殊标签
        '会员号~VIP': 'VIP Membership',
        '靓号5A~~9A': 'Premium 5A-9A',
        '实卡1年以上': 'Real SIM 1+ Year',
        '实卡注册': 'Real SIM',
        '真机注册': 'Real Device',
        '精养月号': 'Premium Monthly',
        '精品月号': 'Premium Monthly',
        '全新一手': 'Brand New',
        '满月': 'Full Month',
        
        # 文件类型（用户确认）
        ' 直登号': ' tdata',
        ' 协议号': ' session',
        ' API ': ' api ',
        '直登号': 'tdata',
        '协议号': 'session',
        
        # 天数
        '45天以上': '45+ Days',
        '45天+': '45+ Days',
        '40天以上': '40+ Days',
        '40天+': '40+ Days',
        '30天以上': '30+ Days',
        '30天+': '30+ Days',
        
        # 单独年份（1-11年）
        '11年以上': '11+ Year',
        '10年以上': '10+ Year',
        '9年以上': '9+ Year',
        '8年以上': '8+ Year',
        '7年以上': '7+ Year',
        '6年以上': '6+ Year',
        '5年以上': '5+ Year',
        '4年以上': '4+ Year',
        '3年以上': '3+ Year',
        '2年以上': '2+ Year',
        '1年以上': '1+ Year',
        
        # 拼写错误版本（数据库中的错误需要兼容）
        '5以年上老号': '5+ Year Old',
        '2以年上': '2+ Year',
        '1以年上': '1+ Year',
        
        # 通用词
        '混合国家': 'Mixed Countries',
        '老号': 'Old',
        '月号': 'Monthly',
        '账号': 'Account',
    }
    
    # 按长度降序排序，避免短字符串先匹配导致长字符串无法匹配
    for zh_desc in sorted(description_map.keys(), key=len, reverse=True):
        if zh_desc in result:
            result = result.replace(zh_desc, description_map[zh_desc])
    
    # 英文：再替换国家名（按长度从长到短排序）
    # 对国家名也按长度排序，优先匹配长名称（如"巴布亚新几内亚"优先于"几内亚"）
    sorted_countries = sorted(COUNTRY_NAMES['zh_to_en'].items(), key=lambda x: len(x[0]), reverse=True)
    for zh_name, en_name in sorted_countries:
        if zh_name in result:
            result = result.replace(zh_name, en_name)
    
    return result

def translate_category_name(category_name, target_lang='zh'):
    """
    翻译分类名称
    Translate category name
    
    Args:
        category_name: 分类名称 Category name
        target_lang: 目标语言 ('zh' or 'en')
    
    Returns:
        str: 翻译后的分类名 Translated category name
    """
    # 分类名称映射 Category name mapping (匹配数据库实际分类名)
    category_map = {
        '🌏 亚洲国家': 'cat_asian',
        '🌍 欧美国家': 'cat_european',
        '🌍 非洲国家': 'cat_african',
        '🛡 2月-5月': 'cat_feb_may',
        '⭐️ 6月-12月': 'cat_jun_dec',
        '💎 1年-2年老号': 'cat_1_2_year',
        '🔮 3年-4年老号': 'cat_3_4_year',
        '👑 5年以上老号': 'cat_5plus_year',
        '🌈七年以上适合当主号使用': 'cat_7plus_year',
        '💍会员号~VIP': 'cat_vip',
        '✨靓号5A~~9A（AAAAA连号）': 'cat_fancy',
    }
    
    # 查找对应的键 Find corresponding key
    key = category_map.get(category_name)
    if key:
        return get_text(key, target_lang)
    
    return category_name  # 如果找不到，返回原文 Return original if not found
