#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 日报生成脚本（精简版）
生成精简易读的每日报告
"""

from datetime import datetime
from pathlib import Path

def generate_simple_report():
    """生成精简报告"""
    today = datetime.now().strftime("%m月%d日")
    filename = Path.home() / "Downloads" / f"OpenClaw日报_{today}.md"

    report = f"""# OpenClaw 日报

📅 {today}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 最新信息

• 📚 官网文档: https://docs.openclaw.ai
• 🔖 GitHub: https://github.com/openclaw/openclaw
• 💬 Discord: https://discord.gg/clawd
• 🧩 技能市场: https://clawhub.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 今日建议

• 检查 GitHub Releases 是否有新版本
• 查看文档网站的最新更新
• 浏览社区技能库

━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ 更新时间: {datetime.now().strftime("%H:%M")}

*由 OpenClaw 自动生成*
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    return str(filename)

if __name__ == "__main__":
    result = generate_simple_report()
    print(f"报告已生成: {result}")
