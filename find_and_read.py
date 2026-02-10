from pathlib import Path
import glob

# 获取用户目录
user_dir = Path.home()

# 查找桌面下的电信相关文件夹
telecom_folder = None
for folder in user_dir.parent.parent.parent.glob('**/*'):
    if any(keyword in str(folder).lower() for keyword in ['电信', 'dianxin']):
        if '人才' in str(folder) or 'rencai' in str(folder).lower():
            telecom_folder = folder
            print(f"找到文件夹: {folder.name}")
            print(f"完整路径: {folder}")
            break

if not telecom_folder:
    print("未找到电信人才培养文件夹")
    exit(1)

# 列出所有文件
print(f"\n文件夹内容:")
for f in telecom_folder.iterdir():
    print(f"  {f.name}")

# 读取所有 .txt 文件
output_file = user_dir / ".openclaw" / "workspace" / "docs_content.txt"

with open(output_file, 'w', encoding='utf-8') as out:
    txt_files = [f for f in telecom_folder.iterdir() if f.suffix == '.txt']
    print(f"\n找到 {len(txt_files)} 个文本文件")

    for txt_file in txt_files:
        out.write(f"\n{'='*80}\n")
        out.write(f"文件: {txt_file.name}\n")
        out.write(f"{'='*80}\n")

        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            out.write(f"字符数: {len(content)}\n")
            out.write(f"字数: {len(content.split())}\n")
            out.write(f"\n内容:\n{content}\n\n")

print(f"\n已保存到: {output_file}")
