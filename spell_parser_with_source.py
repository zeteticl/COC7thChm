#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COC7th 神話法術數據解析器 - 增加來源標記版本
添加 source 字段：守秘人規則書 vs 魔法大典
"""

import os
import json
import re
import sys
from bs4 import BeautifulSoup
from typing import Dict, List, Any

# 修復編碼問題
sys.stdout.reconfigure(encoding='utf-8')


class SpellParser:
    """法術數據解析器"""

    def __init__(self):
        self.data = {}

    def parse_spell_file(self, file_path: str, category: str = None, source: str = None) -> None:
        """解析單個法術HTML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")
            return

        soup = BeautifulSoup(content, 'html.parser')

        # 獲取法術名稱（從h1標題或strong標籤）
        chinese_name = ""
        h1_title = soup.find('h1')
        if h1_title:
            chinese_name = h1_title.get_text().strip()
            # 移除分類標記，如〔召〕
            chinese_name = re.sub(r'〔[^〕]*〕', '', chinese_name).strip()
        else:
            # 嘗試從strong標籤獲取（守秘人規則書格式）
            strong_titles = soup.find_all('strong')
            for strong in strong_titles:
                strong_text = strong.get_text().strip()
                if '请神术：' in strong_text or '通神术：' in strong_text or '联络术：' in strong_text:
                    chinese_name = strong_text.replace('请神术：', '').replace('通神术：', '').replace('联络术：', '').strip()
                    break

        if not chinese_name:
            print(f"Could not find spell name: {file_path}")
            return

        # 獲取英文名稱（從h3標題）
        english_name = ""
        h3_title = soup.find('h3')
        if h3_title:
            english_name = h3_title.get_text().strip()

        spell_data = {
            "name": chinese_name,
            "english_name": english_name,
            "source": source,  # 添加來源字段
            "description": "",
            "cost": {},
            "casting_time": "",
            "aliases": []
        }

        # 解析法術內容
        body = soup.find('body')
        if body:
            # 獲取所有段落
            paragraphs = body.find_all('p')
            description_parts = []

            for p in paragraphs:
                text = p.get_text().strip()

                # 解析消耗信息
                if '消耗：' in text or '消耗:' in text:
                    cost_text = text.replace('消耗：', '').replace('消耗:', '').strip()

                    # 如果同時包含施法用時，需要分離
                    casting_time_in_cost = ""
                    if '施法用时：' in cost_text:
                        parts = cost_text.split('施法用时：', 1)
                        cost_text = parts[0].strip()
                        casting_time_in_cost = parts[1].strip()

                    spell_data["cost"]["description"] = cost_text

                    # 嘗試提取POW消耗
                    pow_match = re.search(r'(\d+)\s*点\s*POW', cost_text)
                    if pow_match:
                        spell_data["cost"]["pow"] = int(pow_match.group(1))

                    # 嘗試提取理智損失
                    san_match = re.search(r'(\d*D\d*)\s*点\s*理智', cost_text)
                    if san_match:
                        spell_data["cost"]["sanity_loss"] = san_match.group(1)

                    # 如果在消耗中找到了施法用時
                    if casting_time_in_cost:
                        spell_data["casting_time"] = casting_time_in_cost

                # 如果還沒有找到施法用時，檢查段落文本
                elif ('施法用时：' in text or '施法用时:' in text) and not spell_data.get("casting_time"):
                    casting_time = text.replace('施法用时：', '').replace('施法用时:', '').strip()
                    spell_data["casting_time"] = casting_time

                # 解析別名
                elif ('别名：' in text or '别名:' in text) and not spell_data.get("aliases"):
                    aliases_text = text.replace('别名：', '').replace('别名:', '').strip()
                    aliases = [alias.strip() for alias in aliases_text.split('、') if alias.strip()]
                    spell_data["aliases"] = aliases

                # 其他內容作為描述
                else:
                    # 跳過已經處理過的消耗、施法用時和別名標籤
                    if p.find('strong'):
                        strong_text = p.find('strong').get_text().strip()
                        if '消耗' in strong_text or '施法用时' in strong_text or '别名' in strong_text:
                            continue
                    # 跳過標題段落
                    if text == chinese_name or (english_name and text == english_name):
                        continue
                    if text and not text.startswith(chinese_name) and not (english_name and text.startswith(english_name)):
                        description_parts.append(text)

            # 組合描述
            spell_data["description"] = '\n\n'.join(description_parts)

        # 如果沒有指定分類，嘗試從路徑推斷
        if not category:
            # 從文件路徑推斷分類
            path_parts = file_path.split(os.sep)
            for part in reversed(path_parts):
                if part in ['召唤术', '独立束缚术', '请神术和送神术', '通神术', '联络术', '时空门法术', '附魔术', '法术列表']:
                    category = part
                    break

        # 如果還是沒有分類，使用"其他法术"
        if not category:
            category = "其他法术"

        # 確保分類存在
        if category not in self.data:
            self.data[category] = []

        self.data[category].append(spell_data)
        print(f"Parsed spell: {chinese_name} (source: {source})")

    def parse_spell_directory(self, directory_path: str, source: str) -> None:
        """遞歸解析法術目錄"""
        if not os.path.exists(directory_path):
            print(f"Directory does not exist: {directory_path}")
            return

        print(f"Parsing spell directory: {directory_path} (source: {source})")

        for root, dirs, files in os.walk(directory_path):
            for filename in files:
                if filename.endswith('.htm') or filename.endswith('.html'):
                    # 跳過索引文件和非法術文件
                    if filename in ['法术列表.htm', '请神术、联络术和召唤术的辨析.htm', '深层魔法.htm', '神话法术.htm']:
                        continue

                    file_path = os.path.join(root, filename)
                    self.parse_spell_file(file_path, source=source)

    def save_to_json(self, output_path: str) -> None:
        """將數據保存為JSON文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"Spell data saved to: {output_path}")
        except Exception as e:
            print(f"Failed to save JSON file: {e}")


def main():
    """Main function"""
    print("Starting COC7th spell data parsing with source tagging...")

    parser = SpellParser()

    # 解析守秘人規則書的法術
    print("Parsing Keeper's Rulebook spells...")
    keeper_path = "守秘人规则书/神话法术/法术列表"
    parser.parse_spell_directory(keeper_path, source="守秘人规则书")

    # 解析克蘇魯神話魔法大典的法術
    print("Parsing Cthulhu Mythos Grimoire spells...")
    grimoire_path = "克苏鲁神话魔法大典/大典正文"
    parser.parse_spell_directory(grimoire_path, source="魔法大典")

    parser.save_to_json("json/spells.json")

    print("Spell parsing completed!")
    total_categories = len(parser.data)
    total_spells = sum(len(spells) for spells in parser.data.values())
    print(f"Total spell categories: {total_categories}")
    print(f"Total spells parsed: {total_spells}")

    # 統計各來源的法術數量
    keeper_count = 0
    grimoire_count = 0
    for category, spells in parser.data.items():
        for spell in spells:
            if spell.get('source') == '守秘人规则书':
                keeper_count += 1
            elif spell.get('source') == '魔法大典':
                grimoire_count += 1

    print(f"守秘人规则书 spells: {keeper_count}")
    print(f"魔法大典 spells: {grimoire_count}")


if __name__ == "__main__":
    main()