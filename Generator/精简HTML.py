import os
from bs4 import BeautifulSoup

def clean_html(file_path):
    with open(file_path, 'r', encoding='gbk') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # 删除所有style标签和内联样式
    for tag in soup.find_all(style=True):
        del tag['style']
    
    # 删除Word特有的XML命名空间
    for tag in soup.find_all():
        for attr in ['xmlns:v', 'xmlns:o', 'xmlns:w', 'xmlns:m']:
            if attr in tag.attrs:
                del tag.attrs[attr]
    
    # 删除空的meta标签
    for meta in soup.find_all('meta'):
        if not meta.attrs:
            meta.decompose()
    
    # 保存清理后的HTML
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html') or file.endswith('.htm'):
                file_path = os.path.join(root, file)
                print(f'Processing {file_path}...')
                clean_html(file_path)

if __name__ == '__main__':
    target_dir = os.path.join(os.path.dirname(__file__), '..', '怪物图鉴')
    process_directory(target_dir)
    print('All HTML files cleaned successfully!')
