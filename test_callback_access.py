import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests

print('测试回调地址是否可访问...')
print('=' * 60)

# 测试健康检查
print('\n1. 测试健康检查端点:')
try:
    response = requests.get('http://188.137.245.150:8888/health', timeout=5)
    print(f'状态码: {response.status_code}')
    print(f'响应: {response.text}')
    if response.status_code == 200:
        print('✅ 健康检查成功')
    else:
        print('❌ 健康检查失败')
except Exception as e:
    print(f'❌ 无法访问: {e}')
    print('\n可能的原因:')
    print('1. 回调服务器没有运行')
    print('2. 防火墙阻止了端口 8888')
    print('3. IP 地址错误')

# 测试回调端点（模拟 POST 请求）
print('\n2. 测试回调端点 (模拟 OKPay):')
test_data = {
    'order_id': 'test123',
    'status': '1',
    'amount': '10'
}
try:
    response = requests.post('http://188.137.245.150:8888/okpay/callback', data=test_data, timeout=5)
    print(f'状态码: {response.status_code}')
    print(f'响应: {response.text}')
    if response.status_code == 200:
        print('✅ 回调端点可访问')
    else:
        print('⚠️ 回调端点返回错误（但至少可以访问）')
except Exception as e:
    print(f'❌ 无法访问: {e}')

print('\n' + '=' * 60)
print('结论:')
print('如果健康检查成功，说明回调服务器运行正常')
print('如果失败，需要先解决网络/防火墙问题')
