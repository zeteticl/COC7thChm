#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COC7th Book Parser - Parse CoC 7th edition books and convert to JSON
分析克苏鲁的呼唤第7版规则书中的书籍数据并转换为JSON格式
"""

import os
import json
import re
from bs4 import BeautifulSoup
from pathlib import Path


class COCBookParser:
    """克苏鲁的呼唤书籍解析器"""

    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.books_data = {
            "神秘学书籍": {},
            "神话典籍": {}
        }

    def parse_html_file(self, file_path):
        """解析单个HTML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            soup = BeautifulSoup(content, 'html.parser')

            # 提取标题
            title_tag = soup.find('h3')
            if not title_tag:
                return None

            title = title_tag.get_text().strip()

            # 提取作者信息
            author_info = ""
            em_tag = soup.find('em')
            if em_tag:
                author_info = em_tag.get_text().strip()

            # 提取描述
            description = ""
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                if p.find('em'):  # 跳过包含作者信息的段落
                    continue
                if p.find('strong'):  # 这是属性信息段落
                    break
                description += p.get_text().strip() + "\n"
            description = description.strip()

            # 提取属性信息
            attributes = {}
            strong_tags = soup.find_all('strong')
            for strong in strong_tags:
                text = strong.get_text().strip()
                next_text = ""
                sibling = strong.next_sibling
                while sibling:
                    if hasattr(sibling, 'get_text'):
                        next_text += sibling.get_text().strip()
                    elif isinstance(sibling, str):
                        next_text += sibling.strip()
                    if sibling.name == 'br':
                        break
                    sibling = sibling.next_sibling
                    if sibling and sibling.name == 'strong':
                        break

                # 清理文本
                next_text = next_text.replace('\n', '').replace('\r', '').strip()
                if ':' in text:
                    key = text.replace('：', ':').split(':')[0]
                    value = next_text if next_text else ""
                    attributes[key] = value
                elif '理智损失' in text:
                    attributes['理智损失'] = next_text
                elif '克苏鲁神话' in text:
                    attributes['克苏鲁神话'] = next_text
                elif '神秘学' in text:
                    attributes['神秘学'] = next_text

            return {
                "标题": title,
                "作者信息": author_info,
                "描述": description,
                "属性": attributes
            }

        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return None

    def parse_mystery_books(self):
        """解析神秘学书籍"""
        mystery_path = self.base_path / "守秘人规则书" / "可怖传说书籍" / "神秘学书籍"

        if not mystery_path.exists():
            print(f"Mystery books directory not found: {mystery_path}")
            return

        for file_path in mystery_path.glob("*.htm"):
            if file_path.name == "神秘学书籍.htm":  # 跳过索引文件
                continue

            book_data = self.parse_html_file(file_path)
            if book_data:
                # 从文件名提取书名作为key
                book_name = file_path.stem  # 移除扩展名
                self.books_data["神秘学书籍"][book_name] = book_data
                print("Parsed mystery book")

    def parse_mythology_books(self):
        """解析神话典籍"""
        myth_path = self.base_path / "守秘人规则书" / "可怖传说书籍" / "神话典籍"

        if not myth_path.exists():
            print(f"Mythology books directory not found: {myth_path}")
            return

        for file_path in myth_path.glob("*.htm"):
            book_data = self.parse_html_file(file_path)
            if book_data:
                # 从文件名提取书名作为key
                book_name = file_path.stem  # 移除扩展名
                self.books_data["神话典籍"][book_name] = book_data
                print("Parsed mythology book")

    def save_to_json(self, output_path):
        """保存数据到JSON文件"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.books_data, f, ensure_ascii=False, indent=2)

            print(f"JSON file saved to: {output_path}")
            print(f"Parsed {len(self.books_data['神秘学书籍'])} mystery books")
            print(f"Parsed {len(self.books_data['神话典籍'])} mythology books")

        except Exception as e:
            print(f"Error saving JSON file: {e}")

    def parse_all_books(self):
        """解析所有书籍"""
        print("Parsing mystery books...")
        self.parse_mystery_books()

        print("Parsing mythology books...")
        self.parse_mythology_books()

        return self.books_data


def main():
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent

    # 创建解析器
    parser = COCBookParser(current_dir)

    # 解析所有书籍
    books_data = parser.parse_all_books()

    # 保存到JSON文件
    output_path = current_dir / "json" / "book" / ".cn.json"
    parser.save_to_json(output_path)


if __name__ == "__main__":
    main()