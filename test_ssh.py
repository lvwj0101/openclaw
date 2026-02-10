#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试SSH连接"""
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

    print("[CONNECT] 尝试连接...")
    try:
        ssh.connect(**SERVER, timeout=15)
        print("[OK] 连接成功！")
        
        # 测试命令
        stdin, stdout, stderr = ssh.exec_command('hostname && whoami', timeout=10)
        output = stdout.read().decode('utf-8')
        print(f"[INFO] {output}")

        ssh.close()
        return 0
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
