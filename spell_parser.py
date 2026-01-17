#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COC7th 神話法術數據解析器
將守秘人規則書和克蘇魯神話魔法大典中的法術資料解析並輸出為JSON格式
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

    def parse_spell_file(self, file_path: str, category: str = None) -> None:
        """解析單個法術HTML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")
            return

        soup = BeautifulSoup(content, 'html.parser')

        # 獲取法術名稱（從h1標題）
        h1_title = soup.find('h1')
        if h1_title:
            chinese_name = h1_title.get_text().strip()
            # 移除分類標記，如〔保〕
            chinese_name = re.sub(r'〔[^〕]*〕', '', chinese_name).strip()
        else:
            # 嘗試從title標籤獲取
            title_tag = soup.find('title')
            if title_tag:
                chinese_name = title_tag.get_text().strip()
            else:
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
            "description": "",
            "cost": {},
            "casting_time": "",
            "aliases": []
        }

        # 解析法術內容
        body = soup.find('body')
        if body:
            # 獲取所有段落和strong標籤
            paragraphs = body.find_all(['p', 'strong'])
            description_parts = []

            # 查找消耗和施法用時 - 遍歷所有strong標籤
            all_strong_tags = body.find_all('strong')
            for strong_tag in all_strong_tags:
                strong_text = strong_tag.get_text().strip()
                if strong_text == '别名：':
                    # 別名在strong標籤之後
                    parent = strong_tag.parent
                    if parent and parent.name == 'p':
                        p_text = parent.get_text()
                        if '别名：' in p_text:
                            # 分割並提取別名部分
                            parts = p_text.split('别名：')
                            if len(parts) > 1:
                                aliases_part = parts[1].strip()
                                # 分割別名（用、分隔）
                                aliases = [alias.strip() for alias in aliases_part.split('、') if alias.strip()]
                                spell_data["aliases"] = aliases
                                break

            for element in paragraphs:
                text = element.get_text().strip()

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

                # 如果還沒有找到別名，檢查段落文本
                elif ('别名：' in text or '别名:' in text) and not spell_data.get("aliases"):
                    aliases_text = text.replace('别名：', '').replace('别名:', '').strip()
                    aliases = [alias.strip() for alias in aliases_text.split('、') if alias.strip()]
                    spell_data["aliases"] = aliases

                # 其他內容作為描述
                else:
                    # 跳過已經處理過的消耗、施法用時和別名標籤
                    if element.name == 'strong' and ('消耗' in text or '施法用时' in text or '别名' in text):
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
        print(f"Parsed spell: {chinese_name}")

    def parse_spell_directory(self, directory_path: str) -> None:
        """遞歸解析法術目錄"""
        if not os.path.exists(directory_path):
            print(f"Directory does not exist: {directory_path}")
            return

        print(f"Parsing spell directory: {directory_path}")

        for root, dirs, files in os.walk(directory_path):
            for filename in files:
                if filename.endswith('.htm') or filename.endswith('.html'):
                    # 跳過索引文件和非法術文件
                    if filename in ['法术列表.htm', '请神术、联络术和召唤术的辨析.htm', '深层魔法.htm', '神话法术.htm']:
                        continue

                    file_path = os.path.join(root, filename)
                    self.parse_spell_file(file_path)

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
    print("Starting COC7th spell data parsing...")

    parser = SpellParser()

    # 解析守秘人規則書的法術
    print("Parsing Keeper's Rulebook spells...")
    spell_path1 = "守秘人规则书/神话法术"
    parser.parse_spell_directory(spell_path1)

    # 解析克蘇魯神話魔法大典的法術
    print("Parsing Cthulhu Mythos Grimoire spells...")
    spell_path2 = "克苏鲁神话魔法大典/大典正文"
    parser.parse_spell_directory(spell_path2)

    parser.save_to_json("json/spells.json")

    print("Spell parsing completed!")
    total_categories = len(parser.data)
    total_spells = sum(len(spells) for spells in parser.data.values())
    print(f"Total spell categories: {total_categories}")
    print(f"Total spells parsed: {total_spells}")


if __name__ == "__main__":
    main()