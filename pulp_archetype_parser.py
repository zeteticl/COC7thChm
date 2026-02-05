#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析通俗克苏鲁「选择英雄类型」目錄，寫入 json/pulp/archetype.json"""

import os
import re
import json
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

ARCHETYPE_DIR = "通俗克苏鲁/2.创建英雄/1.选择英雄类型"
OUT_PATH = "json/pulp/archetype.json"
SKIP_FILES = {"选择英雄类型.htm"}  # 僅跳過索引頁


def parse_archetype_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    h1 = soup.find('h1')
    name = (h1.get_text().strip() if h1 else soup.find('title').get_text().strip())
    # 去掉可能的多餘後綴（如「第一步：」）
    if name.startswith("第一步：") or name.startswith("第一步:"):
        return None

    body = soup.find('body')
    if not body:
        return None

    description_parts = []
    stats_block = None
    special = None
    all_ps = body.find_all('p')
    stats_idx = -1

    for i, p in enumerate(all_ps):
        text = p.get_text().strip()
        if not text:
            continue
        if '核心属性' in text:
            stats_block = p.get_text(separator='\n').strip()
            stats_idx = i
            break
        description_parts.append(text)

    if stats_block is not None and stats_idx >= 0:
        for next_p in all_ps[stats_idx + 1:]:
            t = next_p.get_text().strip()
            if t and '特殊' in t:
                special = t
                break

    description = '\n\n'.join(description_parts)

    # 解析屬性區塊（容許全形/半形冒號與不同換行）
    core_attribute = ""
    skills_note = ""
    suggested_occupations = ""
    talents = ""
    suggested_traits = ""

    if stats_block:
        # 統一換行再依關鍵字切段
        block = re.sub(r'\r\n|\r', '\n', stats_block)
        # 核心属性： INT / DEX 或 APP
        m = re.search(r'核心属性\s*[：:]\s*([^\n]+?)(?=\n|将\s*100|$)', block)
        if m:
            core_attribute = m.group(1).strip()
        m = re.search(r'将\s*100\s*个奖励点数分配给\s*[：:]\s*([^\n]+?)(?=\n|建议职业|$)', block)
        if m:
            skills_note = m.group(1).strip()
        m = re.search(r'建议职业\s*[：:]\s*([^\n]+?)(?=\n|天赋|$)', block)
        if m:
            suggested_occupations = m.group(1).strip()
        m = re.search(r'天赋\s*[：:]\s*([^\n]+?)(?=\n|建议特质|$)', block)
        if m:
            talents = m.group(1).strip()
        m = re.search(r'建议特质\s*[：:]\s*([^\n]+?)(?=\n|$)', block)
        if m:
            suggested_traits = m.group(1).strip()

    item = {
        "name": name,
        "description": description,
        "core_attribute": core_attribute,
        "skill_points_note": "将 100 个奖励点数分配给",
        "skills": skills_note,
        "suggested_occupations": suggested_occupations,
        "talents": talents,
        "suggested_traits": suggested_traits,
        "source": "通俗克苏鲁",
    }
    if special:
        item["special"] = special
    return item


def main():
    items = []
    if not os.path.isdir(ARCHETYPE_DIR):
        print("Directory not found:", ARCHETYPE_DIR)
        return

    for fn in sorted(os.listdir(ARCHETYPE_DIR)):
        if not (fn.endswith('.htm') or fn.endswith('.html')):
            continue
        if fn in SKIP_FILES:
            continue
        path = os.path.join(ARCHETYPE_DIR, fn)
        if not os.path.isfile(path):
            continue
        obj = parse_archetype_file(path)
        if obj:
            items.append(obj)
            print("Parsed:", obj["name"])

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print("Saved %d archetypes to %s" % (len(items), OUT_PATH))


if __name__ == "__main__":
    main()
