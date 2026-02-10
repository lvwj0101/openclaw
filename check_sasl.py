#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查SASL认证配置"""
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

    print("[1] 检查Postfix状态...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    print(output)
    print()

    print("[2] 检查SASL配置...")
    output = run(ssh, 'sudo postconf | grep sasl')
    print(output)
    print()

    print("[3] 检查端口25...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    print(output)
    print()

    print("[4] 尝试启动Postfix...")
    output = run(ssh, 'sudo systemctl start postfix')
    print(output)
    print()

    print("[5] 再次检查状态...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    print(output)

    ssh.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
