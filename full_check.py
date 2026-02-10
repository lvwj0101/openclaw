#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查Postfix完整状态"""
import paramiko
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
    print("Postfix 完整状态检查")
    print("="*60)
    print()

    print("[1] 检查Postfix服务...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    print(output)
    print()

    print("[2] 检查Postfix进程...")
    output = run(ssh, 'ps aux | grep "master\|qmgr\|pickup" | grep -v grep')
    if output.strip():
        print(f"[OK] Postfix进程运行中:")
        print(output)
    else:
        print("[FAIL] Postfix进程未运行")
    print()

    print("[3] 检查端口25...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print(f"[OK] 端口25正在监听:")
        print(output)
    else:
        print("[FAIL] 端口25未监听")
    print()

    print("[4] 检查端口587...")
    output = run(ssh, 'sudo netstat -tlnp | grep :587')
    if ':587' in output:
        print(f"[OK] 端口587正在监听")
    else:
        print("[INFO] 端口587未监听")
    print()

    print("[5] 测试本地发送...")
    output = run(ssh, 'echo "Test from server $(date)" | mail -s "Server Test" root@localhost')
    print(f"[OK] 本地测试邮件已发送")
    print()

    print("[6] 检查邮箱...")
    output = run(ssh, 'ls -la /root/Maildir/new/ 2>/dev/null || ls -la /home/smtpuser/Maildir/new/')
    if output.strip() and 'total' not in output.lower():
        print(f"[OK] 收到邮件:")
        print(output)
    else:
        print("[INFO] 邮箱为空")
    print()

    print("[7] 检查最近邮件日志...")
    output = run(ssh, 'sudo tail -30 /var/log/mail.log')
    print(output)
    print()

    print("[8] 检查防火墙状态...")
    output = run(ssh, 'sudo ufw status verbose | grep 25')
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
