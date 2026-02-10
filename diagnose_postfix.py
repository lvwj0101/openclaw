#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断Postfix问题"""
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

    print("[1] 检查Postfix服务状态...")
    output = run(ssh, 'sudo systemctl status postfix')
    print(output)
    print()

    print("[2] 检查最近的邮件日志...")
    output = run(ssh, 'sudo tail -50 /var/log/mail.log')
    print(output)
    print()

    print("[3] 检查邮件错误日志...")
    output = run(ssh, 'sudo tail -50 /var/log/mail.err 2>/dev/null || echo "文件不存在"')
    print(output)
    print()

    print("[4] 手动启动Postfix...")
    output = run(ssh, 'sudo postfix start')
    print(output)
    print()

    print("[5] 再次检查状态...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    print(output)
    print()

    print("[6] 检查端口...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if output:
        print("[OK] 端口25正在监听:")
        print(output)
    else:
        print("[INFO] 端口25未监听")

    ssh.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
