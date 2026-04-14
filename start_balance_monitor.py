"""
启动余额监控服务
"""
import subprocess
import sys

print('🚀 启动余额监控服务...')
print('按 Ctrl+C 停止')
print('='*50)

try:
    subprocess.run([sys.executable, 'balance_monitor.py'])
except KeyboardInterrupt:
    print('\n👋 服务已停止')
