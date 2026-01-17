import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('json/creature.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for cat_name, category in data.items():
    for name, creature in category.items():
        if 'attacks' in creature and creature['attacks'] and 'skills' not in creature['attacks']:
            print(f'{cat_name}: {name}')
            count += 1

print(f'總共有 {count} 個怪物有attacks但沒有skills')