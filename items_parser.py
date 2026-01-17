#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COC7th 神話造物和異星科技數據解析器
解析守秘人規則書的神話造物和異星科技目錄
"""

import os
import json
import re
import sys
from bs4 import BeautifulSoup
from typing import Dict, List, Any

# 修復編碼問題
sys.stdout.reconfigure(encoding='utf-8')


class ItemsParser:
    """神話造物和異星科技數據解析器"""

    def __init__(self):
        self.items = []

    def parse_item_file(self, file_path: str) -> None:
        """解析單個物品HTML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")
            return

        soup = BeautifulSoup(content, 'html.parser')

        # 獲取物品名稱（從h3標題）
        name = ""
        h3_title = soup.find('h3')
        if h3_title:
            name = h3_title.get_text().strip()

        # 如果沒有h3標題，嘗試從bianlantitle獲取（种族目錄格式）
        if not name:
            bianlantitle = soup.find('div', class_='bianlantitle')
            if bianlantitle:
                name = bianlantitle.get_text().strip()

        if not name:
            print(f"Could not find item name: {file_path}")
            return

        # 獲取物品類型（從文件路徑推斷）
        item_type = "神話造物"
        if "种族" in file_path:
            item_type = "異星科技"

        # 提取所有描述文本
        description_parts = []
        body = soup.find('body')
        if body:
            # 獲取所有段落和div
            for element in body.find_all(['p', 'div']):
                # 跳過bianlantitle（已經在名稱中處理）
                if element.get('class') == ['bianlantitle']:
                    continue

                text = element.get_text().strip()
                if text and not text.startswith(name):  # 避免重複名稱
                    description_parts.append(text)

        # 組合完整描述
        description = '\n\n'.join(description_parts)

        # 創建物品數據
        item_data = {
            "name": name,
            "type": item_type,
            "description": description,
            "source": "守秘人规则书"
        }

        # 嘗試提取額外信息
        # 提取使用者信息
        user_match = re.search(r'使用者[：:]\s*([^<\n]+)', description)
        if user_match:
            item_data["user"] = user_match.group(1).strip()

        self.items.append(item_data)
        print(f"Parsed item: {name} ({item_type})")

    def parse_items_directory(self, directory_path: str) -> None:
        """遞歸解析物品目錄"""
        if not os.path.exists(directory_path):
            print(f"Directory does not exist: {directory_path}")
            return

        print(f"Parsing items directory: {directory_path}")

        for root, dirs, files in os.walk(directory_path):
            for filename in files:
                if filename.endswith('.htm') or filename.endswith('.html'):
                    # 跳過索引文件
                    if filename == '神话造物和异星科技.htm':
                        continue

                    file_path = os.path.join(root, filename)
                    self.parse_item_file(file_path)

    def save_to_json(self, output_path: str) -> None:
        """將數據保存為JSON文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)
            print(f"Items data saved to: {output_path}")
        except Exception as e:
            print(f"Failed to save JSON file: {e}")


def main():
    """Main function"""
    print("Starting COC7th mythical artifacts and alien technology parsing...")

    parser = ItemsParser()

    # 解析守秘人規則書的神話造物和異星科技
    items_path = "守秘人规则书/神话造物和异星科技"
    parser.parse_items_directory(items_path)

    parser.save_to_json("json/items.json")

    print("Items parsing completed!")
    print(f"Total items parsed: {len(parser.items)}")

    # 統計各種類型的物品數量
    type_counts = {}
    for item in parser.items:
        item_type = item.get('type', '未知')
        type_counts[item_type] = type_counts.get(item_type, 0) + 1

    print("Items by type:")
    for item_type, count in type_counts.items():
        print(f"  {item_type}: {count}")


if __name__ == "__main__":
    main()