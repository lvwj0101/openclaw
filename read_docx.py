import os
from pathlib import Path
from docx import Document

# 桌面文件夹
desktop = Path.home() / "Desktop"

# 找到电信人才培养文件夹
target_folder = None
for f in desktop.iterdir():
    if "电信" in f.name and "人才" in f.name:
        target_folder = f
        break

if not target_folder or not target_folder.is_dir():
    print("未找到电信人才培养文件夹")
    exit(1)

print(f"找到文件夹: {target_folder.name}")
print("="*60)

# 列出所有文件
files = list(target_folder.iterdir())
print(f"找到 {len(files)} 个文件")
print("="*60)

for f in sorted(files):
    print(f"\n文件名: {f.name}")
    print(f"大小: {f.stat().st_size:,} 字节")
    print("-"*60)

    # 尝试读取 .docx 文件
    try:
        if f.suffix.lower() == '.docx':
            doc = Document(f)
            # 提取所有段落文本
            paragraphs = [p.text for p in doc.paragraphs]
            content = '\n'.join(paragraphs)

            char_count = len(content)
            word_count = len(content.split())
            print(f"字符数: {char_count:,}")
            print(f"字数: {word_count:,}")

            # 显示前800字符预览
            print(f"\n内容预览 (前800字符):\n")
            print(content[:800])
            print("="*60)

            # 保存为文本文件以便后续处理
            txt_file = f.with_suffix('.txt')
            with open(txt_file, 'w', encoding='utf-8') as txt:
                txt.write(content)
            print(f"已提取文本到: {txt_file.name}")
        else:
            print("非 .docx 文件，跳过")
    except Exception as e:
        print(f"读取失败: {e}")
    print("="*60)
