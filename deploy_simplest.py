#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Postfix 简化部署脚本
"""

import paramiko
import sys
import io
import time

# 修复Windows控制台编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '62.234.211.119',
    'port': 22,
    'username': 'ubuntu',
    'password': 'ji_pmrDc6jMCc6_'
}

def run_cmd(ssh, cmd, timeout=300):
    """执行命令"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    code = stdout.channel.recv_exit_status()
    return code, output, error

def main():
    print("[CONNECT] 连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SERVER, timeout=10)
    print("[OK] 已连接")
    print()

    # 安装Postfix
    print("[1/4] 安装Postfix (请耐心等待)...")
    code, out, err = run_cmd(ssh, 'sudo DEBIAN_FRONTEND=noninteractive apt install -y postfix mailutils', timeout=600)
    if code == 0:
        print("[OK] Postfix安装成功")
    else:
        print(f"[ERROR] 安装失败: {err}")
        return 1

    # 配置
    print("\n[2/4] 配置Postfix...")
    for cmd in [
        "sudo postconf -e 'myhostname = mail.flowthink.local'",
        "sudo postconf -e 'mydomain = flowthink.local'",
        "sudo postconf -e 'inet_interfaces = 0.0.0.0'",
        "sudo postconf -e 'mynetworks = 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16'",
    ]:
        run_cmd(ssh, cmd)
    print("[OK] 配置完成")

    # 用户
    print("\n[3/4] 创建用户...")
    run_cmd(ssh, 'sudo useradd -m smtpuser 2>/dev/null; echo "smtpuser:SmtpTest2024!" | sudo chpasswd')
    run_cmd(ssh, 'sudo mkdir -p /home/smtpuser/Maildir/{new,cur,tmp} && sudo chown -R smtpuser:smtpuser /home/smtpuser/Maildir')
    print("[OK] 用户创建完成")

    # 重启
    print("\n[4/4] 重启服务...")
    run_cmd(ssh, 'sudo systemctl restart postfix')
    run_cmd(ssh, 'sudo ufw --force enable')
    run_cmd(ssh, 'sudo ufw allow 25/tcp')
    print("[OK] 完成")
    print()

    # 结果
    print("=" * 60)
    print("部署成功！")
    print("=" * 60)
    print("SMTP 配置:")
    print("  服务器: 62.234.211.119")
    print("  端口: 25")
    print("  用户名: smtpuser")
    print("  密码: SmtpTest2024!")
    print("  发送者: smtpuser@mail.flowthink.local")
    print("=" * 60)

    ssh.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
