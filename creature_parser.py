#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COC7th 怪物資料解析器
將守秘人規則書中的怪物資料解析並輸出為JSON格式
"""

import os
import json
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional


class CreatureParser:
    """COC怪物資料解析器"""

    def __init__(self):
        self.data = {
            "traditional": {},  # 傳統恐怖怪物
            "mythical": {},     # 神話怪物
            "gods": {}          # 神話諸神
        }

    def parse_html_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """解析單個HTML文件，返回怪物資料"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")
            return None

        soup = BeautifulSoup(content, 'html.parser')

        # Get creature name
        title_tag = soup.find('h1')
        if not title_tag:
            print(f"Could not find title: {file_path}")
            return None

        creature_name = title_tag.get_text().strip()

        # 初始化怪物資料結構
        creature_data = {
            "name": creature_name,
            "description": "",
            "special_abilities": [],
            "attributes": {},
            "stats": {},
            "attacks": {},
            "armor": "",
            "sanity_loss": "",
            "additional_info": []
        }

        # 解析描述（第一個p標籤，通常在h1之後）
        first_p = soup.find('p')
        if first_p:
            # 獲取所有連續的p標籤，直到遇到h3或其他標題
            description_parts = []
            current = first_p
            while current and current.name == 'p' and not current.find('table'):
                text = current.get_text().strip()
                if text and not text.startswith('——'):  # 跳過引用標記
                    description_parts.append(text)
                current = current.find_next_sibling()
                if current and current.name in ['h3', 'h2', 'h1']:
                    break

            creature_data["description"] = ' '.join(description_parts)

        # 解析特殊能力
        abilities = []
        special_attack_abilities = []  # 特殊攻擊能力的詳細描述

        # 首先處理攻擊相關的特殊能力描述
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text.startswith('噬咬：') or text.startswith('凝视：'):
                # 這些是特殊攻擊能力的詳細描述
                special_attack_abilities.append(text)

        # 處理標準的h3標題下的特殊能力
        for h3 in soup.find_all('h3'):
            if '特殊能力' in h3.get_text() or '其他特性' in h3.get_text() or '教团' in h3.get_text():
                # 獲取這個h3之後的所有p標籤，直到下一個h3
                current = h3.find_next_sibling()
                ability_text = ""
                while current and current.name != 'h3':
                    if current.name == 'p':
                        text = current.get_text().strip()
                        if text:
                            ability_text += text + " "
                    elif current.name == 'div' and 'bianlan' in current.get('class', []):
                        # 處理邊欄信息
                        text = current.get_text().strip()
                        if text:
                            ability_text += "[邊欄] " + text + " "
                    current = current.find_next_sibling()

                if ability_text.strip():
                    abilities.append({
                        "title": h3.get_text().strip(),
                        "content": ability_text.strip()
                    })

        creature_data["special_abilities"] = abilities

        # 解析屬性表格
        table = soup.find('table', {'id': 'monstertable-table'})
        if not table:
            # 備用：查找任何表格
            all_tables = soup.find_all('table')
            if all_tables:
                table = all_tables[0]  # 使用第一個表格
        if table:
            rows = table.find_all('tr')
            for row in rows[1:]:  # 跳過表頭
                cells = row.find_all('td')
                if len(cells) >= 2:
                    # 檢查是否是標準的三列表格或不規則的兩列表格
                    if len(cells) >= 3:
                        # 標準三列表格：屬性名稱、值、骰子
                        attr_name = cells[0].get_text().strip()
                        attr_value = cells[1].get_text().strip()
                        attr_roll = cells[2].get_text().strip()
                        creature_data["attributes"][attr_name] = {
                            "value": attr_value,
                            "roll": attr_roll
                        }
                    else:
                        # 不規則的兩列表格：每個單元格包含屬性名稱+值
                        # 需要解析每個單元格
                        for cell in cells:
                            cell_text = cell.get_text().strip()
                            # 使用正則表達式分離屬性名稱和值
                            # 匹配模式如 "STR260", "CON250", "SIZ 1000", "DEX 不适用"
                            match = re.match(r'^([A-Z]{3})\s*(.+)$', cell_text)
                            if match:
                                attr_name = match.group(1)
                                attr_value = match.group(2)
                                attr_roll = ""  # 不規則表格沒有骰子信息
                                creature_data["attributes"][attr_name] = {
                                    "value": attr_value,
                                    "roll": attr_roll
                                }

        # 解析統計數據（HP、傷害加值等）
        stats_text = ""
        # 尋找包含HP、傷害加值等信息的段落
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if any(keyword in text for keyword in ['HP：', '伤害加值：', '平均伤害加值：', '体格：', '平均体格：', '魔法值：', '移动：']):
                stats_text += text + " "

        if stats_text:
            creature_data["stats"]["raw_text"] = stats_text.strip()

            # 嘗試解析具體數值
            hp_match = re.search(r'HP：([^<\n]+)', stats_text)
            if hp_match:
                creature_data["stats"]["hp"] = hp_match.group(1).strip()

            damage_bonus_match = re.search(r'(?:平均)?伤害加值：([^<\n]+)', stats_text)
            if damage_bonus_match:
                creature_data["stats"]["damage_bonus"] = damage_bonus_match.group(1).strip()

            build_match = re.search(r'(?:平均)?体格：([^<\n]+)', stats_text)
            if build_match:
                creature_data["stats"]["build"] = build_match.group(1).strip()

            mp_match = re.search(r'魔法值：([^<\n]+)', stats_text)
            if mp_match:
                creature_data["stats"]["magic_points"] = mp_match.group(1).strip()

            move_match = re.search(r'移动：([^<\n]+)', stats_text)
            if move_match:
                creature_data["stats"]["movement"] = move_match.group(1).strip()

        # 解析攻擊信息
        attack_sections = []
        attacks_per_round = ""
        combat_style_desc = ""  # 戰鬥方式描述
        skills = {}

        # 找到所有攻擊相關的段落
        attack_detail_texts = {}  # 存儲詳細描述，如噬咬：xxx, 凝视：xxx
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text.startswith('噬咬：') or text.startswith('凝视：'):
                # 這是詳細描述，提取技能名稱和描述
                parts = text.split('：', 1)
                if len(parts) == 2:
                    skill_name = parts[0].strip()
                    description = parts[1].strip()
                    attack_detail_texts[skill_name] = description
            elif ('攻击' in text and ('每轮攻击次数：' in text or '战斗方式：' in text)) or ('格斗' in text or '闪避' in text or '噬咬' in text or '凝视' in text):
                # 添加包含具體攻擊統計的段落
                attack_sections.append(text)

        # 處理所有攻擊段落
        combat_style_parts = []
        for section in attack_sections:
            lines = re.split(r'\n|\r\n|\r', section.strip())

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 提取攻擊次數
                if '每轮攻击次数：' in line and not attacks_per_round:
                    match = re.search(r'每轮攻击次数：([^<\n]+)', line)
                    if match:
                        attacks_per_round = match.group(1).strip()
                    continue

                # 提取戰鬥方式描述
                if line.startswith('战斗方式：'):
                    match = re.search(r'战斗方式：([^<\n]+)', line)
                    if match:
                        combat_style_desc = match.group(1).strip()
                    continue

                # 跳過標題行
                if line.startswith('攻击'):
                    continue

                # 收集其他行，但排除詳細描述行（以技能名稱後跟冒號開頭，且不包含百分比的行）
                if not (re.match(r'^[^%：\d]+\s*：', line) and not '%' in line and not line.startswith('战斗方式：')):
                    combat_style_parts.append(line)

                # 特殊處理：對於沒有百分比但有技能名稱的行（如"凝视 目标被催眠，见上。"），創建技能條目
                if not '%' in line and not line.startswith('战斗方式：') and not line.startswith('每轮攻击次数：') and not line.startswith('攻击'):
                    # 檢查是否以技能名稱開頭
                    skill_match = re.match(r'^(格斗|闪避|噬咬|凝视|电光枪|神经鞭|融合|利爪|舌击|紧抓|搔痒|黏液攻击|吞噬|碾压|风力冲击|角顶|践踏)\s', line)
                    if skill_match:
                        skill_name = skill_match.group(1)
                        if skill_name not in skills:
                            # 這是一個沒有數值的技能描述
                            skill_description = line.strip()
                            if len(skill_description) > 10:  # 確保是真正的描述
                                skills[skill_name] = {"text": skill_description}

                # 解析技能
                if '%' in line:
                    if '：' in line:
                        # 有冒號的格式，如"闪避：25%（12/5）"
                        parts = line.split('：')
                        if len(parts) == 2:
                            skill_name = parts[0].strip()
                            skill_value_part = parts[1].strip()
                            percent_match = re.search(r'(\d+)%', skill_value_part)
                            if percent_match:
                                skills[skill_name] = percent_match.group(1)
                    elif '格斗' in line:
                        # 格斗技能
                        percent_match = re.search(r'格斗\s+(\d+)%', line)
                        if percent_match:
                            skill_value = percent_match.group(1)
                            damage = ""
                            special = ""

                            # 匹配damage部分
                            damage_match = re.search(r'伤害\s*([^<\n]+)', line)
                            if damage_match:
                                damage_text = damage_match.group(1).strip()
                                if '+' in damage_text:
                                    # 處理複雜的damage格式，如"1D3（或武器伤害）+ 伤害加值"
                                    # 找到第一個"+"前的骰子部分
                                    dice_match = re.match(r'^(\d+D\d+)', damage_text)
                                    if dice_match:
                                        damage = dice_match.group(1)
                                        # 剩下的部分作為special，包括"+"和之後的所有內容
                                        remaining = damage_text[len(damage):].strip()
                                        # 如果剩下的部分以"（"開頭或包含"点"，添加"伤"字
                                        if remaining.startswith('（') or '点' in remaining:
                                            special = '伤' + remaining
                                        else:
                                            special = remaining
                                    else:
                                        parts = damage_text.split('+', 1)
                                        damage = parts[0].strip()
                                        special = parts[1].strip()
                                else:
                                    # 處理不含"+"但含括號的情況，如"1D3（徒手）或依武器类型"
                                    dice_match = re.match(r'^(\d+D\d+)', damage_text)
                                    if dice_match:
                                        damage = dice_match.group(1)
                                        remaining = damage_text[len(damage):].strip()
                                        if remaining.startswith('（'):
                                            special = '伤' + remaining
                                        else:
                                            special = remaining
                                    else:
                                        # 處理複雜的damage描述，如"等于伤害加值，它还可以选择吞噬目标（见上）"
                                        if len(damage_text) > 5:
                                            damage = ""
                                            special = damage_text
                                        else:
                                            damage = damage_text
                                            special = ""

                            skills["格斗"] = {
                                "value": skill_value,
                                "damage": damage,
                                "special": special
                            }
                    elif any(skill_type in line for skill_type in ['噬咬', '凝视', '闪避']) and '%' in line:
                        # 其他技能
                        skill_name_match = re.match(r'^([^%\d]+)', line)
                        if skill_name_match:
                            skill_name = skill_name_match.group(1).strip()
                            percent_match = re.search(r'(\d+)%', line)
                            if percent_match:
                                skill_value = percent_match.group(1)
                                damage = ""
                                special = ""

                            # 匹配damage部分
                            damage_match = re.search(r'伤害\s*([^<\n]+)', line)
                            if damage_match:
                                    damage_text = damage_match.group(1).strip()
                                    if '+' in damage_text:
                                        # 處理複雜的damage格式，如"1D3（或武器伤害）+ 伤害加值"
                                        # 找到第一個"+"前的骰子部分
                                        dice_match = re.match(r'^(\d+D\d+)', damage_text)
                                        if dice_match:
                                            damage = dice_match.group(1)
                                            # 剩下的部分作為special，包括"+"和之後的所有內容
                                            remaining = damage_text[len(damage):].strip()
                                            # 如果剩下的部分以"（"開頭，添加"伤"字
                                            if remaining.startswith('（'):
                                                special = '伤' + remaining
                                            else:
                                                special = remaining
                                        else:
                                            parts = damage_text.split('+', 1)
                                            damage = parts[0].strip()
                                            special = parts[1].strip()
                                    else:
                                        # 處理複雜的damage描述，如"等于伤害加值，它还可以选择吞噬目标（见上）"
                                        if len(damage_text) > 5:
                                            damage = ""
                                            special = damage_text
                                        else:
                                            damage = damage_text
                                            special = ""

                            if skill_name == "闪避":
                                skills[skill_name] = skill_value
                            else:
                                skills[skill_name] = {
                                    "value": skill_value,
                                    "damage": damage,
                                    "special": special
                                }

                # 處理沒有百分比的技能行，如"闪避：僵尸缺乏决断力，无法进行闪避"
                elif '：' in line and '%' not in line:
                    parts = line.split('：', 1)  # 只分割第一次出現的冒號
                    if len(parts) == 2:
                        skill_name = parts[0].strip()
                        skill_description = parts[1].strip()
                        # 對於沒有數值的技能，檢查是否已經有技能記錄
                        if skill_name not in skills:
                            # 檢查是否是詳細描述（不只是簡單的敘述）
                            if len(skill_description) > 20 or '。' in skill_description or '，' in skill_description:
                                # 詳細描述，使用text字段
                                skills[skill_name] = {"text": skill_description}
                            else:
                                # 簡單描述，直接存儲字符串
                                skills[skill_name] = skill_description
                        # 如果這個技能已經存在且是字典格式，添加詳細描述
                        elif isinstance(skills[skill_name], dict) and skill_name in attack_detail_texts:
                            skills[skill_name]["text"] = attack_detail_texts[skill_name]


        # 添加特殊的攻擊能力描述
        for ability in special_attack_abilities:
            combat_style_parts.append(ability.strip())

        # 為已存在的技能添加詳細描述
        for skill_name, description in attack_detail_texts.items():
            if skill_name in skills and isinstance(skills[skill_name], dict):
                skills[skill_name]["text"] = description

        # 組合combat_style
        combat_style = ""
        if combat_style_desc:
            combat_style = combat_style_desc
        if combat_style_parts:
            if combat_style:
                combat_style += '\n' + '\n'.join(combat_style_parts)
            else:
                combat_style = '\n'.join(combat_style_parts)

        if attack_sections:
            # 確保raw_text包含所有攻擊信息，包括特殊攻擊能力的詳細描述
            all_attack_info = attack_sections.copy()
            for ability in special_attack_abilities:
                if ability not in all_attack_info:  # 避免重複
                    all_attack_info.append(ability)
            creature_data["attacks"]["raw_text"] = ' '.join(all_attack_info)

            # 設置攻擊次數
            if attacks_per_round:
                creature_data["attacks"]["attacks_per_round"] = attacks_per_round

            # 設置戰鬥方式
            if combat_style:
                creature_data["attacks"]["combat_style"] = combat_style

            # 設置技能
            if skills:
                creature_data["attacks"]["skills"] = skills

        # 解析護甲和理智損失
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if '护甲：' in text and '理智损失：' in text:
                # 同時包含護甲和理智損失的段落
                armor_match = re.search(r'护甲：([^<\n]+)', text)
                if armor_match:
                    creature_data["armor"] = armor_match.group(1).strip()

                sanity_match = re.search(r'理智损失：([^<\n]+)', text)
                if sanity_match:
                    creature_data["sanity_loss"] = sanity_match.group(1).strip()
                break
            elif '护甲：' in text:
                # 只包含護甲的段落
                armor_match = re.search(r'护甲：([^<\n]+)', text)
                if armor_match:
                    creature_data["armor"] = armor_match.group(1).strip()
            elif '理智损失：' in text:
                # 只包含理智損失的段落
                sanity_match = re.search(r'理智损失：([^<\n]+)', text)
                if sanity_match:
                    creature_data["sanity_loss"] = sanity_match.group(1).strip()

        # 解析額外信息（邊欄等）
        additional_info = []
        for div in soup.find_all('div', class_='bianlan'):
            text = div.get_text().strip()
            if text:
                additional_info.append(text)

        creature_data["additional_info"] = additional_info

        return creature_data

    def parse_directory(self, directory_path: str, category: str) -> None:
        """解析整個目錄的HTML文件"""
        if not os.path.exists(directory_path):
            print(f"Directory does not exist: {directory_path}")
            return

        print(f"Parsing category: {category}")

        count = 0
        for filename in os.listdir(directory_path):
            if filename.endswith('.htm') or filename.endswith('.html'):
                file_path = os.path.join(directory_path, filename)
                print(f"Processing file...")

                creature_data = self.parse_html_file(file_path)
                if creature_data:
                    creature_name = creature_data["name"]
                    self.data[category][creature_name] = creature_data
                    print(f"OK")
                    count += 1
                else:
                    print(f"Failed")

        print(f"Completed {category}: {count} creatures")

    def save_to_json(self, output_path: str) -> None:
        """將資料保存為JSON文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"Data saved to: {output_path}")
        except Exception as e:
            print(f"Failed to save JSON file: {e}")

    def parse_all_creatures(self) -> None:
        """解析所有怪物資料"""
        base_path = "守秘人规则书/怪物、野兽和异星诸神"

        # 解析傳統恐怖怪物
        traditional_path = os.path.join(base_path, "传统恐怖怪物")
        self.parse_directory(traditional_path, "traditional")

        # 解析神話怪物
        mythical_path = os.path.join(base_path, "神话怪物")
        self.parse_directory(mythical_path, "mythical")

        # 解析神話諸神
        gods_path = os.path.join(base_path, "神话诸神")
        self.parse_directory(gods_path, "gods")


def main():
    """Main function"""
    print("Starting COC7th creature data parsing...")

    parser = CreatureParser()
    parser.parse_all_creatures()
    parser.save_to_json("json/creature.json")

    print("Parsing completed!")
    print(f"Traditional horror creatures: {len(parser.data['traditional'])}")
    print(f"Mythical creatures: {len(parser.data['mythical'])}")
    print(f"Mythical gods: {len(parser.data['gods'])}")


if __name__ == "__main__":
    main()