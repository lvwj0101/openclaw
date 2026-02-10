#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重建aliases并诊断"""
import paramiko
import sys
import io
import time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '49.233.89.28',
    'port': 22,
    'username': 'ubuntu',
    'password': 'dyc#10010'
}

WAF_EMAIL = 'waftest@gmail.com'

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("重建aliases并诊断")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查当前aliases配置...")
    output = run(ssh, f'sudo grep "{WAF_EMAIL}" /etc/aliases')
    print(output)
    print()

    print("[2] 重建aliases数据库...")
    run(ssh, 'sudo newaliases')
    print("[OK] aliases数据库已重建")
    print()

    print("[3] 检查所有邮箱...")
    output = run(ssh, 'find /home -name "Maildir" -type d -exec echo "=== {} ===" \\; -exec ls -la {}/new/ \\; 2>/dev/null | head -30')
    print(output)
    print()

    print("[4] 检查root邮箱...")
    output = run(ssh, 'ls -la /root/Maildir/new/ 2>/dev/null | tail -10')
    if output.strip():
        print("[OK] root邮箱中的邮件:")
        print(output)
    else:
        print("[INFO] root邮箱为空")
    print()

    print("[5] 检查waftest用户邮箱...")
    output = run(ssh, 'ls -la /home/waftest/Maildir/new/ 2>/dev/null | tail -10')
    if output.strip():
        print("[OK] waftest用户邮箱中的邮件:")
        print(output)
    else:
        print("[INFO] waftest用户邮箱为空")
    print()

    print("[6] 发送测试邮件到WAF邮箱...")
    run(ssh, f'echo "Test to WAF at $(date)" | mail -s "WAF Email Test" {WAF_EMAIL}')
    print(f"[OK] 测试邮件已发送到: {WAF_EMAIL}")
    print()

    print("[7] 等待5秒...")
    time.sleep(5)
    print()

    print("[8] 再次检查邮箱...")
    print("[8a] waftest@gmail.com (应该转发到waftest)...")
    output1 = run(ssh, 'ls -la /home/waftest/Maildir/new/ 2>/dev/null | tail -5')
    if output1.strip() and 'total' not in output1.lower():
        print("[OK] waftest邮箱:")
        print(output1)
    else:
        print("[INFO] waftest邮箱为空")
    print()

    print("[8b] root邮箱...")
    output2 = run(ssh, 'ls -la /root/Maildir/new/ 2>/dev/null | tail -5')
    if output2.strip() and 'total' not in output2.lower():
        print("[OK] root邮箱:")
        print(output2)
    else:
        print("[INFO] root邮箱为空")
    print()

    print("[9] 检查最近的邮件日志...")
    output = run(ssh, 'sudo tail -20 /var/log/mail.log')
    print(output)
    print()

    print("[10] 检查邮件队列...")
    output = run(ssh, 'sudo mailq')
    if 'empty' not in output.lower():
        print("[WARNING] 邮件队列不为空:")
        print(output)
    else:
        print("[OK] 邮件队列为空")
    print()

    print("="*60)
    print("诊断完成")
    print("="*60)
    print()
    print("WAF 配置信息:")
    print(f"  邮箱地址: {WAF_EMAIL}")
    print(f"  服务器: 49.233.89.28")
    print(f"  端口: 25")
    print(f"  认证: 不启用")
    print(f"  密码: WafTest2024!")
    print()

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] 诊断失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
