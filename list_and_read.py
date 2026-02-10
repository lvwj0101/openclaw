from pathlib import Path
import os

# 使用 Windows 原始路径
folder = r"C:\Users\gw\Desktop\电信人才培养"

print(f"检查文件夹: {folder}")
print(f"文件夹存在: {os.path.exists(folder)}")

if not os.path.exists(folder):
    exit(1)

# 列出所有文件
files = os.listdir(folder)
print(f"\n找到 {len(files)} 个文件:")
for f in files:
    print(f"  - {f}")

# 读取所有 .txt 文件
print("\n" + "="*80)
print("读取 .txt 文件内容")
print("="*80)

output_file = r"C:\Users\gw\.openclaw\workspace\docs_content.txt"

with open(output_file, 'w', encoding='utf-8') as out:
    for filename in files:
        if filename.endswith('.txt'):
            filepath = os.path.join(folder, filename)
            out.write(f"\n{'='*80}\n")
            out.write(f"文件: {filename}\n")
            out.write(f"{'='*80}\n")
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                out.write(f"字符数: {len(content)}\n")
                out.write(f"字数: {len(content.split())}\n")
                out.write(f"\n内容:\n{content}\n\n")

print(f"\n已保存到: {output_file}")
