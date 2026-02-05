#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re

with open('json/basic/skills.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for key, obj in data.items():
    if not isinstance(obj, dict) or '标题信息' not in obj:
        continue
    info = obj['标题信息']
    name = info.get('名称', '')
    m = re.search(r'（(\d+)%）', name)
    if m:
        info['默认值'] = int(m.group(1))

with open('json/basic/skills.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Updated 默认值 for skills with （XX%） in 名称.')
