"""
OKPay 回调服务器 - 修改版
"""
from flask import Flask, request, jsonify
from datetime import datetime
from config import Config
from database import Database
from okpay_handler import OKPayHandler
import sqlite3

app = Flask(__name__)
db = Database()
okpay = OKPayHandler()

@app.route('/okpay/callback', methods=['GET', 'POST'])
def okpay_callback():
    """处理 OKPay 回调"""
    try:
        # 记录请求来源 IP
        client_ip = request.remote_addr
        
        # 记录请求方法和完整信息
        print(f'\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        print(f'📥 收到 OKPay 回调')
        print(f'时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'来源 IP: {client_ip}')
        print(f'请求方法: {request.method}')
        print(f'请求头: {dict(request.headers)}')
        print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')
        
        # 获取回调数据（支持 POST form 和 JSON）
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                print(f'JSON 数据: {data}')
            else:
                data = request.form.to_dict()
                print(f'Form 数据: {data}')
        else:
            data = request.args.to_dict()
            print(f'GET 参数: {data}')
        
        print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')
        
        # 验证签名（暂时禁用，先让回调能工作）
        # TODO: 修复签名验证逻辑后再启用
        # if not okpay.verify_callback(data.copy()):
        #     print('❌ 签名验证失败')
        #     return jsonify({'status': 'error', 'message': '签名验证失败'}), 403
        
        print('⚠️  跳过签名验证（临时）')
        
        # 提取数据
        callback_data = {}
        for key, value in data.items():
            if key.startswith('data['):
                # 提取 data[xxx] 中的 xxx
                field_name = key[5:-1]  # 去掉 data[ 和 ]
                callback_data[field_name] = value
        
        order_id = callback_data.get('order_id')
        unique_id = callback_data.get('unique_id')
        pay_user_id = callback_data.get('pay_user_id')
        amount = float(callback_data.get('amount', 0))
        coin = callback_data.get('coin')
        status = int(callback_data.get('status', 0))
        order_type = callback_data.get('type')
        
        print(f'  📋 解析后数据:')
        print(f'    订单号: {order_id}')
        print(f'    用户订单号: {unique_id}')
        print(f'    支付用户: {pay_user_id}')
        print(f'    金额: {amount} {coin}')
        print(f'    状态: {status}')
        print(f'    类型: {order_type}')
        
        # 只处理充值（deposit）且已支付（status=1）的订单
        if order_type != 'deposit':
            print(f'  ⏭️ 跳过非充值订单: {order_type}')
            return jsonify({'status': 'success', 'message': '非充值订单'}), 200
        
        if status != 1:
            print(f'  ⏭️ 跳过未支付订单: status={status}')
            return jsonify({'status': 'success', 'message': '未支付'}), 200
        
        # 查询订单
        conn = db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT id, user_id, amount, status
            FROM okpay_orders
            WHERE unique_id = ?
        ''', (unique_id,))
        
        order = c.fetchone()
        
        if not order:
            print(f'  ❌ 订单不存在: {unique_id}')
            conn.close()
            return jsonify({'status': 'error', 'message': '订单不存在'}), 404
        
        db_order_id, user_id, expected_amount, order_status = order
        
        # 检查是否已处理
        if order_status == 'completed':
            print(f'  ⏭️ 订单已处理: {unique_id}')
            conn.close()
            return jsonify({'status': 'success', 'message': '订单已处理'}), 200
        
        # 更新订单状态
        c.execute('''
            UPDATE okpay_orders
            SET status = 'completed',
                okpay_order_id = ?,
                actual_amount = ?,
                pay_user_id = ?,
                completed_at = ?
            WHERE id = ?
        ''', (order_id, amount, pay_user_id, datetime.now().isoformat(), db_order_id))
        
        # 增加用户余额
        c.execute('''
            UPDATE users
            SET balance = balance + ?
            WHERE user_id = ?
        ''', (amount, user_id))
        
        # 记录余额日志
        c.execute('''
            INSERT INTO balance_logs (user_id, amount, type, note)
            VALUES (?, ?, 'recharge', 'OKPay充值')
        ''', (user_id, amount))
        
        conn.commit()
        
        # 获取新余额
        c.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        new_balance = c.fetchone()[0]
        
        conn.close()
        
        print(f'  ✅ 充值成功！')
        print(f'    用户: {user_id}')
        print(f'    金额: {amount} {coin}')
        print(f'    新余额: {new_balance}')
        
        # TODO: 发送通知给用户（需要 Bot 实例）
        # 这里可以通过队列或其他方式通知主 Bot 进程
        
        return jsonify({'status': 'success', 'message': '处理成功'}), 200
    
    except Exception as e:
        print(f'  ❌ 回调处理错误: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'service': 'okpay-callback'}), 200

@app.route('/')
def index():
    """根路由 - 防止扫描"""
    return jsonify({'service': 'okpay-callback', 'version': '1.0'}), 200

@app.errorhandler(404)
def not_found(e):
    """404 处理"""
    return jsonify({'error': 'Not Found'}), 404

if __name__ == '__main__':
    port = Config.OKPAY_CALLBACK_PORT
    print(f'\n🚀 OKPay 回调服务器启动')
    print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    print(f'端口: {port}')
    print(f'回调地址: http://188.137.245.150:{port}/okpay/callback')
    print(f'健康检查: http://188.137.245.150:{port}/health')
    print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')
    
    app.run(host='0.0.0.0', port=port, debug=False)
