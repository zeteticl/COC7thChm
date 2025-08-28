def convert_html_to_ini():
    title_level_map = {
        'H1': 0,
        'H2': 1,
        'H3': 2,
        'H4': 3,
        'H5': 4
    }

    # 输入的标题数据
    print("请右键贴上你的目录（回车两次结束输入）：")
    
    lines = []
    while True:
        line = input()
        if line.strip() == '':  # 结束输入
            break
        lines.append(line.strip())
    
    title_list = []
    index = 1  # 从 TitleList.Title.9 开始，如果要修改起始序号，请修改这里

    # 维护上一级和上上一级标题
    last_h1_title = None
    last_h2_title = None
    last_h2_index = 0  # H2 的当前序号
    last_h3_title = None
    h2_count = 0  # 用于跟踪 H2 的数量

    for line in lines:
        if line.startswith("<") and line.endswith(">"):
            tag = line[1:line.index(">")]  # 提取标签名称
            title = line[line.index(">") + 1:line.rindex("<")]  # 提取标题内容
            level = title_level_map.get(tag, None)

            if level is not None:
                # 根据标题级别更新上一级标题
                if level == 0:  # H1
                    last_h1_title = title
                    last_h2_title = None  # Reset last H2 when H1 is found
                    last_h3_title = None  # Reset last H3 when H1 is found
                    last_h4_title = None

                elif level == 1:  # H2
                    h2_count += 1  # 增加 H2 的数量
                    last_h2_title = title
                    last_h3_title = None  # Reset last H3 when H2 is found
                    last_h4_title = None

                elif level == 2:  # H3
                    last_h3_title = title
                    last_h4_title = None
                
                elif level == 3:  # H4
                    last_h4_title = title

                # 根据级别生成 URL
                # {h2_count}.代表第一级标题的序号，默认最上面的文件夹带有序号，如果最上面的文件夹不带序号，请删掉下方的{h2_count}.
                if level == 0:  # H1
                    url = f"{title}\{title}.htm"
                elif level == 1:  # H2
                    url = f"{last_h1_title}\{h2_count}.{title}\{title}.htm"
                elif level == 2:  # H3
                    url = f"{last_h1_title}\{h2_count}.{last_h2_title}\{title}.htm"
                elif level == 3:  # H4
                    url = f"{last_h1_title}\{h2_count}.{last_h2_title}\{last_h3_title}\{title}.htm"
                elif level == 4:  # H5
                    url = f"{last_h1_title}\{h2_count}.{last_h2_title}\{last_h3_title}\{last_h4_title}\{title}.htm"
                
                # 添加 TitleList 信息
                title_list.append(f"TitleList.Title.{index}={title}")
                title_list.append(f"TitleList.Level.{index}={level}")
                title_list.append(f"TitleList.Url.{index}={url}")
                title_list.append(f"TitleList.Icon.{index}=0")
                title_list.append(f"TitleList.Status.{index}=0")
                title_list.append(f"TitleList.Keywords.{index}=")
                title_list.append(f"TitleList.ContextNumber.{index}={1000 + index - 9}")
                title_list.append(f"TitleList.ApplyTemp.{index}=0")
                title_list.append(f"TitleList.Expanded.{index}=1")
                title_list.append(f"TitleList.Kind.{index}=0")
                index += 1

    # 将转换后的结果写入到文本文件
    with open("output.txt", "w", encoding="utf-8") as f:
        for item in title_list:
            f.write(item + "\n")

    print("\n转换结果已保存到 output.txt")
    input("请按任意键退出...")

# 调用函数
convert_html_to_ini()