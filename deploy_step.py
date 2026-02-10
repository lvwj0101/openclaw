#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Postfix部署 - 分步执行"""
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

def run(ssh, cmd, timeout=120):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SERVER, timeout=10)

    print("[STEP 1] apt update (1-2分钟)...")
    run(ssh, 'sudo apt update', timeout=180)
    print("[OK] update完成")

    print("\n[STEP 2] 安装Postfix (2-3分钟)...")
    run(ssh, 'sudo DEBIAN_FRONTEND=noninteractive apt install -y postfix mailutils', timeout=600)
    print("[OK] Postfix安装完成")

    print("\n[STEP 3] 配置...")
    for cmd in [
        "sudo postconf -e 'myhostname = mail.flowthink.local'",
        "sudo postconf -e 'mydomain = flowthink.local'",
        "sudo postconf -e 'inet_interfaces = 0.0.0.0'",
        "sudo postconf -e 'mynetworks = 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16'",
    ]:
        run(ssh, cmd)
    print("[OK] 配置完成")

    print("\n[STEP 4] 创建用户...")
    run(ssh, 'sudo useradd -m smtpuser 2>/dev/null; echo "smtpuser:SmtpTest2024!" | sudo chpasswd')
    print("[OK] 用户创建完成")

    print("\n[STEP 5] 防火墙和重启...")
    run(ssh, 'sudo ufw --force enable')
    run(ssh, 'sudo ufw allow 25/tcp')
    run(ssh, 'sudo systemctl restart postfix')
    print("[OK] 完成")

    print("\n" + "="*50)
    print("SMTP 配置信息:")
    print("  服务器: 62.234.211.119")
    print("  端口: 25")
    print("  用户名: smtpuser")
    print("  密码: SmtpTest2024!")
    print("  发送者: smtpuser@mail.flowthink.local")
    print("="*50)

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
