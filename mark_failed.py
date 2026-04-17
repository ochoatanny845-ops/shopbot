"""
标记指定账号为失败状态（临时跳过）
"""
import json
import os

def mark_account_failed(account_id):
    """标记账号为失败状态"""
    config_file = 'accounts_pool.json'
    
    if not os.path.exists(config_file):
        print('❌ 配置文件不存在')
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for acc in data['accounts']:
        if acc['id'] == account_id:
            acc['status'] = 'failed'
            print(f'✅ 账号 #{account_id} 已标记为失败状态')
            break
    else:
        print(f'❌ 未找到账号 #{account_id}')
        return
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f'💾 已保存')

if __name__ == '__main__':
    print('='*60)
    print('🔧 标记账号为失败状态')
    print('='*60)
    print()
    
    ids = input('请输入要标记的账号ID（多个用逗号分隔，如 2,3）: ').strip()
    
    for id_str in ids.split(','):
        try:
            account_id = int(id_str.strip())
            mark_account_failed(account_id)
        except ValueError:
            print(f'❌ 无效的ID: {id_str}')
    
    print()
    print('✅ 完成！刷新器会自动跳过这些账号')
