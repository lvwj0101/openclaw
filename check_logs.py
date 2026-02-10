#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查Postfix邮件日志"""
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

    print("[1] 检查Postfix服务...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    print(output)

    print()
    print("[2] 检查端口...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    print(output)

    print()
    print("[3] 检查最近邮件日志...")
    output = run(ssh, 'sudo tail -50 /var/log/mail.log')
    print(output)

    print()
    print("[4] 检查邮件错误日志...")
    output = run(ssh, 'sudo tail -50 /var/log/mail.err 2>/dev/null || echo "文件不存在"')
    print(output)

    print()
    print("[5] 检查系统日志...")
    output = run(ssh, 'sudo journalctl -u postfix -n 50 --no-pager')
    print(output)

    ssh.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
