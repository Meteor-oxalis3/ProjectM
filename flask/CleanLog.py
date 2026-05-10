import re
def clean_log(file_path):
    # 正则表达式
    pattern = r'(\[.*\]|Finished\ job\ |%\)\ done)'

    matched_lines = []
    
    with open(file_path, 'r') as file:
        for line in file:
            if re.search(pattern, line):  # 使用正则表达式匹配
                matched_lines.append(line.strip())  # 将匹配行去除换行符后添加到列表

    return '\n'.join(matched_lines)  # 将匹配行合并为一个字符串，并以换行符分隔

def completed_work(file_path):
    # 正则表达式
    pattern = r'(Finished\ job\ )'

    matched_lines = []
    
    with open(file_path, 'r') as file:
        for line in file:
            if re.search(pattern, line):  # 使用正则表达式匹配
                # 提取第三列的内容，然后去除"."
                line = line.split(' ')[2].replace(".", "")
                matched_lines.append(line.strip())  # 将匹配行去除换行符后添加到列表

    return ','.join(matched_lines)  # 将匹配行合并为一个字符串，并以换行符分隔