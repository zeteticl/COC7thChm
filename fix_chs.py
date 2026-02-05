import re
path = r'E:\github\COC7thChm\json\basic\chs\skills.json'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()
c = re.sub(r'和\s+或', '和/或', c)
c = re.sub(r'并\s+或', '并/或', c)
c = re.sub(r'"艺术 手艺"', '"艺术和手艺"', c)
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')
