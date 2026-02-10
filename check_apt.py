#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查服务器上的apt进程"""
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

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SERVER, timeout=10)

    print("[CHECK] 检查apt进程...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep -E "(apt|dpkg)" | grep -v grep', timeout=10)
    output = stdout.read().decode('utf-8')
    if output.strip():
        print("[RUNNING] 发现apt进程:")
        print(output)
    else:
        print("[INFO] 没有apt进程在运行")

    print("\n[CHECK] 检查Postfix安装状态...")
    stdin, stdout, stderr = ssh.exec_command('which postfix', timeout=10)
    output = stdout.read().decode('utf-8')
    if output.strip():
        print("[OK] Postfix已安装:", output.strip())
    else:
        print("[NOT INSTALLED] Postfix未安装")

    ssh.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
