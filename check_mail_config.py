#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查mail配置和测试"""
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

    print("[1] 检查mail命令使用的MTA...")
    output = run(ssh, 'sudo alternatives --display mail | grep current')
    print(output)

    print()
    print("[2] 检查aliases...")
    output = run(ssh, 'sudo postconf | grep alias_maps')
    print(output)

    print()
    print("[3] 尝试用sendmail发送...")
    output = run(ssh, 'echo "Test via sendmail" | sendmail -t root@localhost root@localhost')
    print("[OK] sendmail命令已执行")

    print()
    print("[4] 检查root邮箱...")
    output = run(ssh, 'ls -la /var/mail/root 2>/dev/null || ls -la /root/Maildir/new/')
    print(output)

    print()
    print("[5] 测试发送到smtpuser邮箱...")
    output = run(ssh, 'echo "Test to smtpuser" | mail -s "Test" smtpuser@localhost')
    print("[OK] 测试邮件已发送")

    print()
    print("[6] 检查smtpuser邮箱...")
    output = run(ssh, 'ls -la /home/smtpuser/Maildir/new/')
    print(output)

    print()
    print("[7] 检查所有邮箱...")
    output = run(ssh, 'find /home -name Maildir -type d')
    print(output)

    print()
    print("[8] 查看系统邮件日志...")
    output = run(ssh, 'sudo tail -20 /var/log/syslog | grep mail')
    print(output)

    print()
    print("[9] 重新检查Postfix配置...")
    output = run(ssh, 'sudo postconf -n | grep -E "(inet|networks|destinations)"')
    print(output)

    print()
    print("="*60)
    print("检查完成")
    print("="*60)

    ssh.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
