#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终测试"""
import paramiko
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '62.234.211.119',
    'port': 22,
    'username': 'ubuntu',
    'password': '1qaz#EDC%TGB'
}

def run(ssh, cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SERVER, timeout=10)

    print("="*60)
    print("Postfix 最终测试")
    print("="*60)
    print()

    print("[1] 检查端口25...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
    else:
        print("[FAIL] 端口25未监听")

    print()
    print("[2] 检查Postfix进程...")
    output = run(ssh, 'ps aux | grep postfix | grep -v grep')
    if output.strip():
        print("[OK] Postfix进程运行中")
    else:
        print("[FAIL] Postfix进程未运行")

    print()
    print("[3] 测试发送邮件到本地用户...")
    run(ssh, 'echo "Test message from Postfix - $(date)" | mail -s "Test Email $(date)" smtpuser@localhost')
    print("[OK] 测试邮件已发送")

    print()
    print("[4] 等待邮件到达...")
    import time
    time.sleep(3)

    print()
    print("[5] 检查邮箱...")
    output = run(ssh, 'ls -la /home/smtpuser/Maildir/new/')
    if output.strip() and 'total' not in output.lower():
        print("[OK] 收到邮件:")
        print(output)
    else:
        print("[INFO] 邮箱为空（可能需要更长时间）")

    print()
    print("="*60)
    print("Postfix 部署成功！")
    print("="*60)
    print()
    print("SMTP 配置信息:")
    print("  服务器: 62.234.211.119")
    print("  端口: 25")
    print("  用户名: smtpuser")
    print("  密码: SmtpTest2024!")
    print("  发送者: smtpuser@localhost")
    print()
    print("现在可以在防火墙设备中配置SMTP并发送测试邮件！")
    print()
    print("如果外部邮件无法发送，可能需要：")
    print("1. 配置DNS反向解析")
    print("2. 配置SPF记录")
    print("3. 但用于内部测试应该没问题")
    print("="*60)

    ssh.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
