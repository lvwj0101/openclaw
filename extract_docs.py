from pathlib import Path

# 文件夹路径
folder = Path(r"C:\Users\gw\Desktop\电信人才培养")

# 读取三个文本文件
files = [
    "中国电信信号故障发布及值班维护员操作手册（无修改0126).txt",
    "电信网络运行维护公告管理办法.txt",
    "电信网络运行维护管理办法（发布稿）.txt"
]

# 保存所有内容到一个新文件
output_file = Path.home() / ".openclaw" / "workspace" / "all_docs_content.txt"

with open(output_file, 'w', encoding='utf-8') as out:
    for filename in files:
        filepath = folder / filename
        if filepath.exists():
            out.write(f"\n{'='*80}\n")
            out.write(f"文件名: {filename}\n")
            out.write(f"{'='*80}\n")
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                out.write(f"字符数: {len(content)}\n")
                out.write(f"字数: {len(content.split())}\n")
                out.write(f"\n【完整内容】\n")
                out.write(content)
                out.write("\n\n\n")
        else:
            out.write(f"\n文件不存在: {filename}\n\n\n")

print(f"已读取并保存到: {output_file}")
