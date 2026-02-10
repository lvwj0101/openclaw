#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速部署Postfix - 简化版
"""

import paramiko
import sys
import io
import time

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 服务器配置
SERVER = {
    'hostname': '62.234.211.119',
    'port': 22,
    'username': 'ubuntu',
    'password': 'ji_pmrDc6jMCc6_'
}

def run_command(ssh, command):
    """执行SSH命令"""
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    exit_code = stdout.channel.recv_exit_status()
    return exit_code, output, error

def main():
    print("[CONNECT] 连接服务器...")
    print(f"   地址: {SERVER['username']}@{SERVER['hostname']}:{SERVER['port']}")
    print()

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[SUCCESS] 连接成功！")
        print()

        # 步骤1：检查并安装Postfix
        print("[STEP 1/5] 检查Postfix...")
        exit_code, output, error = run_command(ssh, 'which postfix')
        if exit_code == 0:
            print("[OK] Postfix已安装")
        else:
            print("[INSTALL] 安装Postfix...")
            run_command(ssh, 'sudo DEBIAN_FRONTEND=noninteractive apt install -y postfix mailutils')
            print("[OK] Postfix安装完成")
        print()

        # 步骤2：配置Postfix
        print("[STEP 2/5] 配置Postfix...")
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
            run_command(ssh, cmd)
        print("[OK] Postfix配置完成")
        print()

        # 步骤3：创建测试用户
        print("[STEP 3/5] 创建测试用户...")
        exit_code, output, error = run_command(ssh, 'id -u smtpuser')
        if exit_code != 0:
            run_command(ssh, 'sudo useradd -m -s /bin/bash smtpuser')
            run_command(ssh, 'echo "smtpuser:SmtpTest2024!" | sudo chpasswd')
            print("[OK] 用户 smtpuser 已创建")
        else:
            print("[OK] 用户 smtpuser 已存在")

        # 创建邮箱目录
        run_command(ssh, 'sudo mkdir -p /home/smtpuser/Maildir/{new,cur,tmp}')
        run_command(ssh, 'sudo chown -R smtpuser:smtpuser /home/smtpuser/Maildir')
        run_command(ssh, 'sudo chmod -R 700 /home/smtpuser/Maildir')
        print("[OK] 邮箱目录已创建")
        print()

        # 步骤4：配置防火墙
        print("[STEP 4/5] 配置防火墙...")
        run_command(ssh, 'sudo ufw allow 25/tcp')
        run_command(ssh, 'sudo ufw allow 587/tcp')
        print("[OK] 防火墙已配置")
        print()

        # 步骤5：重启服务
        print("[STEP 5/5] 重启Postfix...")
        run_command(ssh, 'sudo systemctl restart postfix')
        run_command(ssh, 'sudo systemctl enable postfix')
        print("[OK] Postfix已重启")
        print()

        # 验证
        print("[VERIFY] 验证服务状态...")
        exit_code, output, error = run_command(ssh, 'sudo systemctl status postfix --no-pager | head -5')
        print(output)

        print()
        print("=" * 60)
        print("SMTP 配置信息")
        print("=" * 60)
        print("SMTP 服务器: 62.234.211.119")
        print("SMTP 端口: 25 (未加密)")
        print("用户名: smtpuser")
        print("密码: SmtpTest2024!")
        print("发送者邮箱: smtpuser@mail.flowthink.local")
        print("=" * 60)
        print()
        print("[COMPLETE] 配置完成！")
        print()
        print("下一步：")
        print("1. 在防火墙设备中使用上述SMTP配置")
        print("2. 发送测试邮件")
        print("3. 查看日志: sudo tail -f /var/log/mail.log")

        return 0

    except Exception as e:
        print(f"[ERROR] {e}")
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
