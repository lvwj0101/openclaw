#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 互联网内容收集脚本
每天自动从互联网收集 OpenClaw 的最新资讯、文档、更新等信息
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# 配置
REPORT_DIR = Path(os.path.expanduser("~/Downloads"))
BASE_URL = "https://docs.openclaw.ai"
GITHUB_URL = "https://github.com/openclaw/openclaw"
COMMUNITY_URL = "https://discord.gg/clawd"

def fetch_url(url, timeout=30):
    """从 URL 获取内容"""
    try:
        # 使用 curl 获取内容
        result = subprocess.run(
            ['curl', '-s', '-L', '--max-time', str(timeout), url],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception as e:
        return None

def get_openclaw_docs():
    """获取 OpenClaw 最新文档信息"""
    # 获取文档首页
    content = fetch_url(BASE_URL)
    if content:
        # 提取一些关键信息
        info = []
        if "OpenClaw" in content:
            info.append("✓ OpenClaw 官网可访问")
        if "Documentation" in content or "文档" in content:
            info.append("✓ 文档服务正常")
        return "\n".join(info)
    return "❌ 无法获取文档网站内容"

def get_github_updates():
    """获取 GitHub 上的最新更新"""
    # 尝试获取 GitHub releases 或 commits
    content = fetch_url(GITHUB_URL + "/releases/latest")
    if content:
        # 提取版本信息
        if "tag_name" in content:
            import re
            match = re.search(r'"tag_name":\s*"([^"]+)"', content)
            if match:
                return f"✓ 最新版本: {match.group(1)}"
        return "✓ GitHub 仓库可访问"
    return "❌ 无法获取 GitHub 更新"

def get_community_news():
    """获取社区新闻"""
    content = fetch_url(COMMUNITY_URL)
    if content:
        return "✓ Discord 社区可访问"
    return "❌ 无法获取社区信息"

def generate_internet_report():
    """生成互联网内容报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    filename = REPORT_DIR / f"OpenClaw互联网报告_{today}.md"

    report = f"""# OpenClaw 互联网内容收集报告

## 报告日期
{datetime.now().strftime("%Y年%m月%d日 %H:%M")}

---

## 1. OpenClaw 官方资源

### 官网文档
网站: {BASE_URL}
状态:
{get_openclaw_docs()}

### GitHub 仓库
仓库: {GITHUB_URL}
状态:
{get_github_updates()}

### 社区
Discord: {COMMUNITY_URL}
状态:
{get_community_news()}

---

## 2. OpenClaw 核心资源

| 资源类型 | URL | 说明 |
|----------|-----|------|
| 官方文档 | https://docs.openclaw.ai | 完整的使用文档和 API 参考 |
| GitHub 仓库 | https://github.com/openclaw/openclaw | 源代码、Issues、Releases |
| Discord 社区 | https://discord.gg/clawd | 用户交流、问题讨论 |
| 技能市场 | https://clawhub.com | 社区贡献的技能和扩展 |

---

## 3. 使用建议

### 每日检查清单
- [ ] 查看 GitHub Releases 是否有新版本
- [ ] 检查文档网站是否有更新
- [ ] 在 Discord 社区查看最新讨论

### 学习资源
- [ ] 阅读官方文档
- [ ] 浏览社区技能库
- [ ] 参与社区讨论

---

## 4. 报告生成信息

- 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 报告文件: {filename}
- 数据来源: 互联网实时获取

---

*此报告由 OpenClaw 自动生成，每日更新一次*
"""

    # 保存报告
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"报告已生成: {filename}")
    return str(filename)

if __name__ == "__main__":
    generate_internet_report()
