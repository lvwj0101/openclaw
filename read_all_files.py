from pathlib import Path

# 文件夹路径
folder = Path(r"C:\Users\gw\Desktop\电信人才培养")

# 读取三个文本文件
files = [
    "中国电信信号故障发布及值班维护员操作手册（无修改0126).txt",
    "电信网络运行维护公告管理办法.txt",
    "电信网络运行维护管理办法（发布稿）.txt"
]

for filename in files:
    filepath = folder / filename
    if filepath.exists():
        print(f"\n{'='*80}")
        print(f"文件: {filename}")
        print('='*80)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"字符数: {len(content)}")
            print(f"字数: {len(content.split())}")
            print(f"\n内容:\n{content}")
    else:
        print(f"\n文件不存在: {filename}")
