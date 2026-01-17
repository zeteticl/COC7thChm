#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COC7th 武器數據解析器
將守秘人規則書中的武器資料解析並輸出為JSON格式
"""

import os
import json
import re
import sys
from bs4 import BeautifulSoup
from typing import Dict, List, Any

# 修復編碼問題
sys.stdout.reconfigure(encoding='utf-8')


class WeaponParser:
    """武器數據解析器"""

    def __init__(self):
        self.data = {}

    def parse_weapon_file(self, file_path: str) -> None:
        """解析單個武器HTML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")
            return

        soup = BeautifulSoup(content, 'html.parser')

        # 獲取武器類別名稱（從h3標題）
        category_title = soup.find('h3')
        if not category_title:
            print(f"Could not find category title: {file_path}")
            return

        category_name = category_title.get_text().strip()

        # 查找武器表格
        table = soup.find('table', {'id': 'zebra-table'})
        if not table:
            print(f"Could not find weapon table: {file_path}")
            return

        # 解析表格頭部來確定列的順序
        headers = []
        header_row = table.find('tr')
        if header_row:
            for th in header_row.find_all('th'):
                headers.append(th.get_text().strip())

        # 解析武器數據
        weapons = []
        rows = table.find_all('tr')[1:]  # 跳過表頭

        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= len(headers) - 1:  # 至少要有基本列數
                weapon_data = {}

                for i, cell in enumerate(cells):
                    if i < len(headers):
                        header = headers[i]
                        value = cell.get_text().strip()

                        # 標準化列名映射
                        if header == "武器名称":
                            weapon_data["name"] = value
                        elif header == "技能":
                            weapon_data["skill"] = value
                        elif header == "伤害":
                            weapon_data["damage"] = value
                        elif header == "贯穿":
                            weapon_data["armor_piercing"] = value
                        elif header == "基础射程":
                            weapon_data["range"] = value
                        elif header == "每轮":
                            weapon_data["shots_per_round"] = value
                        elif header == "弹容量":
                            weapon_data["capacity"] = value
                        elif header == "价格20s/现代":
                            weapon_data["price"] = value
                        elif header == "故障值":
                            weapon_data["malfunction"] = value
                        elif header == "时代":
                            weapon_data["era"] = value

                if weapon_data.get("name"):  # 確保有武器名稱
                    weapons.append(weapon_data)

        if weapons:
            self.data[category_name] = weapons
            print(f"Parsed {len(weapons)} weapons from {category_name}")

    def parse_weapon_directory(self, directory_path: str) -> None:
        """解析整個武器目錄"""
        if not os.path.exists(directory_path):
            print(f"Directory does not exist: {directory_path}")
            return

        print(f"Parsing weapon directory: {directory_path}")

        count = 0
        for filename in os.listdir(directory_path):
            if filename.endswith('.htm') or filename.endswith('.html'):
                # 跳過主索引文件
                if filename == "武器列表.htm":
                    continue

                file_path = os.path.join(directory_path, filename)
                print(f"Processing {filename}...")
                self.parse_weapon_file(file_path)
                count += 1

        print(f"Completed parsing {count} weapon files")

    def save_to_json(self, output_path: str) -> None:
        """將數據保存為JSON文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"Weapon data saved to: {output_path}")
        except Exception as e:
            print(f"Failed to save JSON file: {e}")


def main():
    """Main function"""
    print("Starting COC7th weapon data parsing...")

    parser = WeaponParser()
    weapon_path = "守秘人规则书/附录/装备列表/武器列表"
    parser.parse_weapon_directory(weapon_path)
    parser.save_to_json("json/weapon.json")

    print("Weapon parsing completed!")
    total_weapons = sum(len(weapons) for weapons in parser.data.values())
    print(f"Total weapon categories: {len(parser.data)}")
    print(f"Total weapons parsed: {total_weapons}")


if __name__ == "__main__":
    main()