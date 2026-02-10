import os
from pathlib import Path
import sys

# 设置 UTF-8 编码输出
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

folder = Path(r"C:\Users\gw\Desktop\电信人才培养")

if not folder.exists():
    print(f"文件夹不存在: {folder}")
    sys.exit(1)

files = list(folder.glob("*.*"))
print(f"找到 {len(files)} 个文件")
print("="*50)

for f in sorted(files):
    print(f"\n文件名: {f.name}")
    print(f"大小: {f.stat().st_size} 字节")
    print("-"*50)

    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            char_count = len(content)
            word_count = len(content.split())
            print(f"字符数: {char_count}")
            print(f"字数: {word_count}")
            preview = content[:500]
            print(f"\n内容预览:\n{preview}")
    except Exception as e:
        print(f"读取失败: {e}")
    print("="*50)
