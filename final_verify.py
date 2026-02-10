#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终验证"""
import paramiko
import time

SERVER = {
    'hostname': '62.234.211.119',
    'port': 22,
    'username': 'ubuntu',
    'password': '1qaz#EDC%TGB'
}

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SERVER, timeout=10)

    print("[1] Check Postfix processes...")
    output = ssh.exec_command('ps aux | grep master | grep -v grep')[1].read().decode()
    if 'master' in output:
        print(f"[OK] Postfix master running")
    print(output)

    print("\n[2] Check port 25...")
    output = ssh.exec_command('sudo netstat -tlnp | grep :25')[1].read().decode()
    if ':25' in output:
        print(f"[OK] Port 25 listening")
    print(output)

    print("\n[3] Check mail queue...")
    output = ssh.exec_command('sudo mailq')[1].read().decode()
    print(output)

    print("\n" + "="*60)
    print("Postfix Configuration")
    print("="*60)
    print("\nSMTP Info:")
    print("  Server: 62.234.211.119")
    print("  Port: 25")
    print("  Auth: None (no authentication)")
    print("  From: root@localhost")
    print("\nFirewall Config:")
    print("  Auth: Disable / None")
    print("  Username: root (optional)")
    print("  Password: (optional)")
    print("  Port: 25")
    print("\n" + "="*60)
    print("Ready for testing!")
    print("="*60)

    ssh.close()

if __name__ == "__main__":
    main()
