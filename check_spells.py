import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('json/spells.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

total_categories = len(data)
total_spells = sum(len(spells) for spells in data.values())

print(f'法術類別總數: {total_categories}')
print(f'法術總數: {total_spells}')
print()

for category, spells in data.items():
    print(f'{category}: {len(spells)} 個法術')