import sqlite3

# 创建 SQLite3 数据库
def create_database(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pinyin_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hanzi TEXT NOT NULL,
            pinyin TEXT NOT NULL
        )
    ''')

    # 在 hanzi 列上创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hanzi ON pinyin_mapping (hanzi)')

    conn.commit()
    return conn, cursor

# 插入数据
def insert_data(cursor, hanzi, pinyin):
    cursor.execute('''
        INSERT INTO pinyin_mapping (hanzi, pinyin) VALUES (?, ?)
    ''', (hanzi, pinyin))

# 将 Unicode 编码转换为汉字
def unicode_to_hanzi(unicode_str):
    try:
        # 去掉 'U+' 前缀并转换为整数
        code_point = int(unicode_str[2:], 16)
        # 将整数转换为 Unicode 字符
        return chr(code_point)
    except (ValueError, IndexError):
        return None

# 带声调的字母到不带声调字母的映射
TONED_TO_UNTONED = {
    'ā': 'a', 'á': 'a', 'ǎ': 'a', 'à': 'a',
    'ō': 'o', 'ó': 'o', 'ǒ': 'o', 'ò': 'o',
    'ē': 'e', 'é': 'e', 'ě': 'e', 'è': 'e',
    'ī': 'i', 'í': 'i', 'ǐ': 'i', 'ì': 'i',
    'ū': 'u', 'ú': 'u', 'ǔ': 'u', 'ù': 'u',
    'ǖ': 'v', 'ǘ': 'v', 'ǚ': 'v', 'ǜ': 'v',
    'ü': 'v'
}

# 清理拼音，将带声调的字母替换为不带声调的字母
def clean_pinyin(pinyin):
    cleaned_pinyin = []
    for char in pinyin:
        # 如果是带声调的字母，替换为不带声调的字母
        if char in TONED_TO_UNTONED:
            cleaned_pinyin.append(TONED_TO_UNTONED[char])
        else:
            cleaned_pinyin.append(char)
    return ''.join(cleaned_pinyin)

# 去掉注释行和行内注释
def remove_comments(line):
    # 去掉行内注释（从 # 开始到行尾）
    return line.split('#')[0].strip()

# 读取 pinyin.txt 文件并插入数据
def import_pinyin_data(cursor, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = remove_comments(line)  # 去掉注释
            if line:  # 如果行不为空
                parts = line.split(':')
                if len(parts) == 2:
                    unicode_str = parts[0].strip()  # 获取 Unicode 编码
                    hanzi = unicode_to_hanzi(unicode_str)  # 转换为汉字
                    if hanzi:
                        pinyin_list = parts[1].strip().split(',')
                        # 使用集合去重
                        unique_pinyin = set()
                        for pinyin in pinyin_list:
                            # 清理拼音，将带声调的字母替换为不带声调的字母
                            cleaned_pinyin = clean_pinyin(pinyin)
                            unique_pinyin.add(cleaned_pinyin)
                        # 插入去重后的拼音
                        for pinyin in unique_pinyin:
                            insert_data(cursor, hanzi, pinyin)

# 主函数
def main():
    db_file = 'pinyin.db'
    pinyin_file = 'pinyin.txt'

    conn, cursor = create_database(db_file)
    import_pinyin_data(cursor, pinyin_file)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
