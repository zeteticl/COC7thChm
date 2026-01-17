import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('json/weapon.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

total_categories = len(data)
total_weapons = sum(len(weapons) for weapons in data.values())

print(f'武器類別總數: {total_categories}')
print(f'武器總數: {total_weapons}')
print()

for category, weapons in data.items():
    print(f'{category}: {len(weapons)} 件武器')