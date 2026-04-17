# -*- coding: utf-8 -*-
"""
Fix: Add asyncio.sleep() in wait loop to prevent blocking event loop
"""

with open('purchaser.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the while loop in _wait_for_files and add sleep at the end
insert_idx = None
for i, line in enumerate(lines):
    if 'while len(files) <' in line:
        # Find the end of the loop (before the return statement)
        for j in range(i, min(i + 100, len(lines))):
            if 'return files' in lines[j] and 'files' not in lines[j+1]:
                insert_idx = j
                break
        break

if not insert_idx:
    print("Could not find insertion point")
else:
    # Insert sleep before the return (at the end of loop iteration)
    # Find the last await in the loop
    for i in range(insert_idx, insert_idx - 50, -1):
        if 'await asyncio.sleep' in lines[i]:
            print("Sleep already exists")
            break
        if '            # 处理消息' in lines[i] or 'for msg in msgs:' in lines[i-10:i+1]:
            # Insert sleep after the for loop
            for j in range(i, min(i + 30, len(lines))):
                if lines[j].strip() == '' and 'await' in lines[j-1]:
                    insert_idx = j
                    lines.insert(insert_idx, '            \n')
                    lines.insert(insert_idx + 1, '            # Yield control to event loop (prevent blocking)\n')
                    lines.insert(insert_idx + 2, '            await asyncio.sleep(2)\n')
                    
                    with open('purchaser.py', 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    
                    print(f"Added asyncio.sleep(2) at line {insert_idx + 2}")
                    break
            break
