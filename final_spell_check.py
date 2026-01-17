import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('json/spells.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

total_categories = len(data)
total_spells = sum(len(spells) for spells in data.values())

print(f'法術類別總數: {total_categories}')
print(f'法術總數: {total_spells}')

# 檢查有多少法術有英文名稱
spells_with_english = 0
# 檢查有多少法術有施法用時
spells_with_casting_time = 0
# 檢查有多少法術有別名
spells_with_aliases = 0

for category, spells in data.items():
    for spell in spells:
        if spell.get('english_name') and spell['english_name'].strip():
            spells_with_english += 1
        if spell.get('casting_time') and spell['casting_time'].strip():
            spells_with_casting_time += 1
        if spell.get('aliases') and len(spell['aliases']) > 0:
            spells_with_aliases += 1

print(f'有英文名稱的法術數: {spells_with_english}')
print(f'有施法用時的法術數: {spells_with_casting_time}')
print(f'有別名的法術數: {spells_with_aliases}')
print(f'沒有施法用時的法術數: {total_spells - spells_with_casting_time}')

for category, spells in data.items():
    print(f'{category}: {len(spells)} 個法術')