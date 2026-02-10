#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""停止Postfix"""
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

    print("[STOP] 停止Postfix...")
    ssh.connect(**SERVER, timeout=10)

    # 停止Postfix
    run(ssh, 'sudo systemctl stop postfix')
    run(ssh, 'sudo systemctl disable postfix')
    
    # 停止master进程
    run(ssh, 'sudo pkill -9 -f postfix')
    run(ssh, 'sudo pkill -9 -f master')

    print("[OK] Postfix已停止")
    
    ssh.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
