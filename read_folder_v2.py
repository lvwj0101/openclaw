import os
from pathlib import Path

# 桌面文件夹
desktop = Path.home() / "Desktop"

# 找到电信人才培养文件夹
target_folder = None
for f in desktop.iterdir():
    if "电信" in f.name and "人才" in f.name:
        target_folder = f
        print(f"找到文件夹: {f.name}")
        break

if not target_folder or not target_folder.is_dir():
    print("未找到电信人才培养文件夹")
    exit(1)

print(f"\n文件夹路径: {target_folder}")
print("="*60)

# 列出所有文件
files = list(target_folder.iterdir())
print(f"\n找到 {len(files)} 个文件")
print("="*60)

for f in sorted(files):
    print(f"\n文件名: {f.name}")
    print(f"大小: {f.stat().st_size:,} 字节")
    print("-"*60)

    # 读取文件内容
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            char_count = len(content)
            word_count = len(content.split())
            print(f"字符数: {char_count:,}")
            print(f"字数: {word_count:,}")
            print(f"\n内容预览 (前500字符):\n")
            print(content[:500])
    except Exception as e:
        print(f"读取失败: {e}")
    print("="*60)
