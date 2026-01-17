from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('守秘人规则书/神话法术/法术列表/犹格·索托斯之拳.htm', 'r', encoding='utf-8') as f:
    content = f.read()

soup = BeautifulSoup(content, 'html.parser')
body = soup.find('body')
all_strong = body.find_all('strong')

print("All strong tags in the file:")
for i, strong in enumerate(all_strong):
    print(f'{i}: "{strong.get_text().strip()}"')