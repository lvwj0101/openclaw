#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查邮件队列"""
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

    print("[1] 检查邮件队列...")
    output = run(ssh, 'sudo mailq')
    if output.strip() and 'Mail queue is empty' not in output:
        print("[OK] 邮件队列中有邮件:")
        print(output)
    else:
        print("[OK] 邮件队列为空")

    print()
    print("[2] 检查deferred队列...")
    output = run(ssh, 'sudo postqueue -c deferred')
    if output.strip():
        print("[OK] deferred队列:")
        print(output)
    else:
        print("[OK] deferred队列为空")

    print()
    print("[3] 检查incoming队列...")
    output = run(ssh, 'sudo postqueue -c incoming')
    if output.strip():
        print("[OK] incoming队列:")
        print(output)
    else:
        print("[OK] incoming队列为空")

    print()
    print("[4] 发送新测试邮件...")
    output = run(ssh, 'echo "Test $(date)" | mail -s "Test Postfix Queue" root@localhost')
    print("[OK] 测试邮件已发送")

    print()
    print("[5] 再次检查队列...")
    import time
    time.sleep(2)
    output = run(ssh, 'sudo mailq')
    if output.strip() and 'Mail queue is empty' not in output:
        print("[OK] 邮件队列:")
        print(output)
    else:
        print("[OK] 邮件队列为空")

    print()
    print("[6] 刷新队列...")
    run(ssh, 'sudo postsuper -r ALL')
    print("[OK] 队列已刷新")

    print()
    print("[7] 检查root邮箱...")
    output = run(ssh, 'ls -la /root/Maildir/new/ 2>/dev/null || ls -la /var/mail/root 2>/dev/null')
    if output.strip():
        print("[OK] root邮箱内容:")
        print(output)
    else:
        print("[OK] root邮箱为空")

    print()
    print("[8] 检查邮件日志...")
    output = run(ssh, 'sudo tail -20 /var/log/mail.log')
    if output.strip():
        print("[OK] 邮件日志:")
        print(output)
    else:
        print("[INFO] 邮件日志为空")

    ssh.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
