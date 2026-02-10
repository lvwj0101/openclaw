#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习电信人才培养文件夹中的文档
"""

import os
from pathlib import Path

# 桌面文件夹路径
folder = Path.home() / "Desktop" / "电信人才培养"

def read_file(filepath):
    """读取文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None

def analyze_documents():
    """分析文档"""
    if not folder.exists():
        print(f"文件夹不存在: {folder}")
        return

    # 列出所有文件
    files = list(folder.glob("*.*"))

    print(f"找到 {len(files)} 个文件")
    print("="*50)

    for f in sorted(files):
        print(f"\n文件名: {f.name}")
        print(f"大小: {f.stat().st_size} 字节")
        print("-"*50)

        content = read_file(f)
        if content:
            # 分析字数
            char_count = len(content)
            word_count = len(content.split())
            print(f"字符数: {char_count}")
            print(f"字数: {word_count}")

            # 显示前500字符预览
            preview = content[:500]
            print(f"\n内容预览:\n{preview}")
            print("="*50)

if __name__ == "__main__":
    analyze_documents()
