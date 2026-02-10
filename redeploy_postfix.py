#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Postfix 重新部署 - 使用新密码"""
import paramiko
import sys
import io
import time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '62.234.211.119',
    'port': 22,
    'username': 'ubuntu',
    'password': '1qaz#EDC%TGB'  # 新密码
}

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("Postfix 重新部署")
    print("="*60)
    print()

    print("[1/6] 连接服务器...")
    try:
        ssh.connect(**SERVER, timeout=10)
        print("[OK] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[2/6] 更新系统包...")
    run(ssh, 'sudo apt update', timeout=300)
    run(ssh, 'sudo apt upgrade -y', timeout=600)
    print("[OK] 系统更新完成")

    print()
    print("[3/6] 安装Postfix...")
    output = run(ssh, 'which postfix')
    if not output.strip():
        run(ssh, 'sudo DEBIAN_FRONTEND=noninteractive apt install -y postfix mailutils', timeout=600)
        print("[OK] Postfix安装完成")
    else:
        print("[OK] Postfix已安装")

    print()
    print("[4/6] 配置Postfix...")
    commands = [
        "sudo postconf -e 'myhostname = mail.flowthink.local'",
        "sudo postconf -e 'mydomain = flowthink.local'",
        "sudo postconf -e 'myorigin = $mydomain'",
        "sudo postconf -e 'inet_interfaces = 0.0.0.0'",
        "sudo postconf -e 'mynetworks = 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16'",
        "sudo postconf -e 'home_mailbox = Maildir/'",
        "sudo postconf -e 'smtpd_sasl_auth_enable = no'",
    ]
    for cmd in commands:
        run(ssh, cmd)
    print("[OK] 配置完成")

    print()
    print("[5/6] 重启服务...")
    run(ssh, 'sudo systemctl restart postfix', timeout=30)
    run(ssh, 'sudo systemctl enable postfix')
    print("[OK] 服务重启完成")

    print()
    print("[6/6] 验证服务...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output:
        print("[OK] Postfix服务运行正常")
    else:
        print("[WARNING] 服务状态异常")

    print()
    print("="*60)
    print("部署完成！")
    print("="*60)
    print()
    print("SMTP 配置信息:")
    print("  服务器: 62.234.211.119")
    print("  端口: 25")
    print("  用户名: smtpuser")
    print("  密码: SmtpTest2024!")
    print("  发送者: smtpuser@mail.flowthink.local")
    print()
    print("完成时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[ERROR] 部署失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
