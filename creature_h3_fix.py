#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COC7th Creature H3 Fix - Fix missing description content in creature.json
修復creature.json中缺失的描述內容
"""

import json
from pathlib import Path
from bs4 import BeautifulSoup


class CreatureH3Fix:
    """修復H3解析中缺失的描述內容"""

    def __init__(self, input_path, output_path):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)

    def load_creature_data(self):
        """加載creature.json數據"""
        try:
            with open(self.input_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading creature.json: {e}")
            return {}

    def parse_missing_descriptions(self):
        """解析缺失的描述內容"""
        missing_descriptions = {}

        # 定義需要檢查的文件
        categories = {
            "神话诸神": "神话诸神"
        }

        for category_name, folder_name in categories.items():
            category_path = Path("守秘人规则书/怪物、野兽和异星诸神") / folder_name
            if not category_path.exists():
                continue

            for html_file in category_path.glob("*.htm"):
                creature_name = html_file.stem

                # 解析HTML獲取描述
                descriptions = self.extract_descriptions_from_html(html_file)
                if descriptions:
                    if category_name not in missing_descriptions:
                        missing_descriptions[category_name] = {}
                    missing_descriptions[category_name][creature_name] = descriptions

        return missing_descriptions

    def extract_descriptions_from_html(self, html_file):
        """從HTML文件中提取描述內容"""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {html_file}: {e}")
            return []

        soup = BeautifulSoup(content, 'html.parser')
        descriptions = []

        # 找到所有p標籤
        paragraphs = soup.find_all('p')

        for p in paragraphs:
            # 跳過包含表格的段落
            if p.find_parent('table') or p.find('table'):
                continue

            # 跳過屬性表格
            if p.get('id') == 'monstertable-table':
                continue

            text = p.get_text().strip()

            # 跳過空內容
            if not text:
                continue

            # 檢查是否在h3標題之後
            h3_before = None
            for sibling in p.previous_siblings:
                if sibling.name == 'h3':
                    h3_before = sibling.get_text().strip()
                    break

            # 如果沒有h3標題在前面，或者是h1之後的第一個內容，則視為描述
            if h3_before is None or h3_before not in ['教团', '其他特性', '乌波·萨斯拉，无源之源', '乌波·萨斯拉的子嗣']:
                # 額外檢查 - 確保不是屬性相關內容
                if not any(keyword in text for keyword in [
                    'HP：', '伤害加值：', '体格：', '魔法值：', '移动：',
                    '护甲：', '法术：', '理智损失：', '每轮攻击次数：'
                ]):
                    descriptions.append(text)

        return descriptions

    def update_creature_data(self, existing_data, missing_descriptions):
        """更新creature數據，添加缺失的描述"""
        for category, creatures in missing_descriptions.items():
            if category not in existing_data:
                continue

            for creature_name, descriptions in creatures.items():
                if creature_name in existing_data[category]:
                    # 更新描述字段
                    if "描述" not in existing_data[category][creature_name]:
                        existing_data[category][creature_name]["描述"] = []

                    # 添加缺失的描述，但避免重複
                    existing_descriptions = existing_data[category][creature_name]["描述"]
                    for desc in descriptions:
                        if desc not in existing_descriptions:
                            existing_descriptions.append(desc)

        return existing_data

    def save_updated_data(self, data):
        """保存更新後的數據"""
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"Updated creature.json with missing descriptions saved to: {self.output_path}")

        except Exception as e:
            print(f"Error saving updated creature.json: {e}")


def main():
    # 設置路徑
    input_path = Path("json/creature.json")
    output_path = Path("json/creature_fixed.json")

    # 創建修復器
    fixer = CreatureH3Fix(input_path, output_path)

    # 加載現有數據
    existing_data = fixer.load_creature_data()

    # 解析缺失的描述
    missing_descriptions = fixer.parse_missing_descriptions()

    # 更新數據
    updated_data = fixer.update_creature_data(existing_data, missing_descriptions)

    # 保存更新後的數據
    fixer.save_updated_data(updated_data)

    # 備份並替換
    backup_path = Path("json/creature_backup8.json")
    input_path.rename(backup_path)
    output_path.rename(input_path)

    print(f"Original file backed up to: {backup_path}")
    print(f"Fixed file is now at: {input_path}")


if __name__ == "__main__":
    main()