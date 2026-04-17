"""
删除指定账号
"""
import json
import os

def remove_account(account_id):
    """删除账号"""
    config_file = 'accounts_pool.json'
    
    if not os.path.exists(config_file):
        print('❌ 配置文件不存在')
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_count = len(data['accounts'])
    data['accounts'] = [acc for acc in data['accounts'] if acc['id'] != account_id]
    
    if len(data['accounts']) == original_count:
        print(f'❌ 未找到账号 #{account_id}')
        return
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f'✅ 账号 #{account_id} 已删除')

if __name__ == '__main__':
    print('='*60)
    print('🗑️ 删除账号')
    print('='*60)
    print()
    
    ids = input('请输入要删除的账号ID（多个用逗号分隔，如 2,3）: ').strip()
    
    for id_str in ids.split(','):
        try:
            account_id = int(id_str.strip())
            remove_account(account_id)
        except ValueError:
            print(f'❌ 无效的ID: {id_str}')
    
    print()
    print('✅ 完成！')
