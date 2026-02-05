#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析通俗克苏鲁范例奇妙道具，輸出格式參照 json/basic/items.json"""

import os
import json
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

ITEMS_DIR = "通俗克苏鲁/6.通俗魔法、灵能和怪奇技术/范例奇妙道具"
OUT_PATH = "json/pulp/items.json"


def parse_item_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # 名稱：h1 或 title
    h1 = soup.find('h1')
    name = h1.get_text().strip() if h1 else soup.find('title').get_text().strip()

    body = soup.find('body')
    if not body:
        return None

    parts = []
    craft = None
    for p in body.find_all('p'):
        text = p.get_text().strip()
        if not text:
            continue
        if text.startswith('制造') or ('<strong>制造</strong>' in str(p) or '制造' in text and '零件' in text):
            craft = text
            continue
        parts.append(text)

    description = '\n\n'.join(parts)

    item = {
        "name": name,
        "type": "奇妙道具",
        "description": description,
        "source": "通俗克苏鲁",
    }
    if craft:
        item["craft"] = craft
    return item


def main():
    items = []
    if not os.path.isdir(ITEMS_DIR):
        print("Directory not found:", ITEMS_DIR)
        return

    for fn in sorted(os.listdir(ITEMS_DIR)):
        if not (fn.endswith('.htm') or fn.endswith('.html')) or fn == '范例奇妙道具.htm':
            continue
        path = os.path.join(ITEMS_DIR, fn)
        if not os.path.isfile(path):
            continue
        obj = parse_item_file(path)
        if obj:
            items.append(obj)
            print("Parsed:", obj["name"])

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print("Saved %d items to %s" % (len(items), OUT_PATH))


if __name__ == "__main__":
    main()
