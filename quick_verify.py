#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速验证Postfix"""
import paramiko
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '62.234.211.119',
    'port': 22,
    'username': 'ubuntu',
    'password': 'ji_pmrDc6jMCc6_'
}

def run(ssh, cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SERVER, timeout=10)

    # 1. 端口25
    print("[PORT 25] 检查...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
    else:
        print("[FAIL] 端口25未监听")

    # 2. Postfix进程
    print("\n[PROCESS] 检查Postfix进程...")
    output = run(ssh, 'ps aux | grep postfix | grep -v grep')
    if output.strip():
        print(f"[OK] Postfix进程运行中")
    else:
        print("[FAIL] Postfix进程未运行")

    ssh.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
