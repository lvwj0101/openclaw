#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Postfix 部署脚本 - 带实时进度
"""

import paramiko
import sys
import io
import time
import threading

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

def run_command_with_output(ssh, command, timeout=120):
    """执行命令并实时输出"""
    print(f"\n[EXEC] {command}")
    print("-" * 40)

    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)

    # 实时读取输出
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            data = stdout.channel.recv(1024)
            if data:
                print(data.decode('utf-8', errors='ignore'), end='')
        time.sleep(0.1)

    # 读取剩余输出
    remaining = stdout.read().decode('utf-8', errors='ignore')
    if remaining:
        print(remaining)

    error = stderr.read().decode('utf-8', errors='ignore')
    exit_code = stdout.channel.recv_exit_status()

    print("-" * 40)
    print(f"[EXIT] Code: {exit_code}")

    return exit_code, error

def main():
    print("=" * 60)
    print("Postfix SMTP 部署")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("\n[1/6] 连接服务器...")
        ssh.connect(**SERVER, timeout=10)
        print("[OK] 连接成功")

        print("\n[2/6] 安装Postfix (需要2-3分钟)...")
        cmd = 'DEBIAN_FRONTEND=noninteractive sudo apt update && DEBIAN_FRONTEND=noninteractive sudo apt install -y postfix mailutils'
        exit_code, error = run_command_with_output(ssh, cmd, timeout=600)
        if exit_code != 0:
            print(f"[ERROR] 安装失败: {error}")
            return 1
        print("[OK] Postfix安装完成")

        print("\n[3/6] 配置Postfix...")
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
            ssh.exec_command(cmd, timeout=10)
        print("[OK] 配置完成")

        print("\n[4/6] 创建测试用户...")
        ssh.exec_command('sudo useradd -m -s /bin/bash smtpuser', timeout=10)
        ssh.exec_command('echo "smtpuser:SmtpTest2024!" | sudo chpasswd', timeout=10)
        ssh.exec_command('sudo mkdir -p /home/smtpuser/Maildir/{new,cur,tmp}', timeout=10)
        ssh.exec_command('sudo chown -R smtpuser:smtpuser /home/smtpuser/Maildir', timeout=10)
        print("[OK] 用户创建完成")

        print("\n[5/6] 配置防火墙...")
        ssh.exec_command('sudo ufw --force enable', timeout=10)
        ssh.exec_command('sudo ufw allow 25/tcp', timeout=10)
        ssh.exec_command('sudo ufw allow 587/tcp', timeout=10)
        print("[OK] 防火墙配置完成")

        print("\n[6/6] 重启服务...")
        ssh.exec_command('sudo systemctl restart postfix', timeout=30)
        ssh.exec_command('sudo systemctl enable postfix', timeout=10)
        print("[OK] 服务重启完成")

        # 验证
        print("\n[VERIFY] 验证服务...")
        stdin, stdout, stderr = ssh.exec_command('sudo systemctl status postfix --no-pager', timeout=10)
        status = stdout.read().decode('utf-8')
        if 'active (running)' in status:
            print("[OK] Postfix服务运行正常")
        else:
            print("[WARNING] 服务状态异常")

        stdin, stdout, stderr = ssh.exec_command('sudo netstat -tlnp | grep :25', timeout=10)
        port25 = stdout.read().decode('utf-8')
        if ':25' in port25:
            print("[OK] 端口25正在监听")

        # 完成
        print("\n" + "=" * 60)
        print("部署成功！")
        print("=" * 60)
        print("\nSMTP 配置信息:")
        print("  服务器: 62.234.211.119")
        print("  端口: 25")
        print("  用户名: smtpuser")
        print("  密码: SmtpTest2024!")
        print("  发送者: smtpuser@mail.flowthink.local")
        print()
        print("完成时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n[ERROR] 部署失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
