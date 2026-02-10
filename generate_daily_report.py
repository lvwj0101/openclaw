#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 每日报告生成脚本
每天自动收集 OpenClaw 的状态、日志、会话等信息，生成报告文档
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# 配置
REPORT_DIR = Path(os.path.expanduser("~/Downloads"))
LOG_DIR = Path(os.path.expanduser("~/.openclaw"))

def get_system_status():
    """获取系统状态"""
    try:
        with open(LOG_DIR / "logs" / f"openclaw-{datetime.now():%Y-%m-%d}.log", "r", encoding="utf-8", errors="ignore") as f:
            # 读取最后 100 行
            lines = f.readlines()[-100:]
            return "\n".join(lines)
    except:
        return "日志文件未找到或无法读取"

def get_session_info():
    """获取会话信息"""
    try:
        with open(LOG_DIR / "agents" / "main" / "sessions" / "sessions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return json.dumps(data, indent=2, ensure_ascii=False)
    except:
        return "会话信息未找到"

def get_feishu_messages():
    """获取飞书消息摘要"""
    try:
        msg_file = LOG_DIR / "workspace" / "memory" / f"{datetime.now():%Y-%m-%d}.md"
        if msg_file.exists():
            with open(msg_file, "r", encoding="utf-8") as f:
                return f.read()
        return "今日无飞书消息记录"
    except:
        return "无法读取飞书消息"

def generate_report():
    """生成每日报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    filename = REPORT_DIR / f"OpenClaw每日报告_{today}.md"

    report = f"""# OpenClaw 每日报告

## 报告日期
{datetime.now():%Y年%m月%d日 %H:%M}

---

## 1. 系统状态

### 最近日志（最后100行）
```
{get_system_status()}
```

---

## 2. 会话信息

```json
{get_session_info()}
```

---

## 3. 飞书消息

{get_feishu_messages()}

---

## 4. 报告生成信息

- 生成时间: {datetime.now():%Y-%m-%d %H:%M:%S}
- 报告文件: {filename}

---

*此报告由 OpenClaw 自动生成*
"""

    # 保存报告
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"报告已生成: {filename}")
    return str(filename)

if __name__ == "__main__":
    generate_report()
