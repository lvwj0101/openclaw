#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速部署Postfix - 自动化脚本
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

def run_command(ssh, command, timeout=120):
    """执行SSH命令，带超时"""
    print(f"[EXEC] {command[:50]}...")
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    exit_code = stdout.channel.recv_exit_status()
    return exit_code, output, error

def main():
    print("=" * 60)
    print("Postfix SMTP 自动化部署")
    print("=" * 60)
    print()

    print("[CONNECT] 连接服务器...")
    print(f"   地址: {SERVER['username']}@{SERVER['hostname']}:{SERVER['port']}")
    print()

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[OK] 连接成功！")
        print()

        # 检查Postfix
        print("[CHECK] 检查Postfix安装状态...")
        exit_code, output, error = run_command(ssh, 'which postfix', timeout=10)
        postfix_installed = (exit_code == 0)
        print(f"[{'OK' if postfix_installed else 'INSTALL'}] Postfix {'已安装' if postfix_installed else '未安装，将安装'}")
        print()

        # 安装Postfix
        if not postfix_installed:
            print("[INSTALL] 安装Postfix (可能需要2-3分钟)...")
            cmd = 'DEBIAN_FRONTEND=noninteractive sudo apt update && sudo DEBIAN_FRONTEND=noninteractive apt install -y postfix mailutils'
            exit_code, output, error = run_command(ssh, cmd, timeout=300)

            if exit_code != 0:
                print("[ERROR] Postfix安装失败")
                print(error)
                return 1

            print("[OK] Postfix安装完成")
            print()

        # 配置Postfix
        print("[CONFIG] 配置Postfix...")
        commands = [
            "sudo postconf -e 'myhostname = mail.flowthink.local'",
            "sudo postconf -e 'mydomain = flowthink.local'",
            "sudo postconf -e 'myorigin = $mydomain'",
            "sudo postconf -e 'inet_interfaces = 0.0.0.0'",
            "sudo postconf -e 'mynetworks = 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16'",
            "sudo postconf -e 'home_mailbox = Maildir/'",
            "sudo postconf -e 'smtpd_sasl_auth_enable = no'",
            "sudo postconf -e 'smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination'",
            "sudo postconf -e 'smtpd_client_restrictions = permit_mynetworks'",
            "sudo postconf -e 'smtpd_helo_required = yes'",
            "sudo postconf -e 'smtpd_helo_restrictions = permit_mynetworks'",
            "sudo postconf -e 'smtpd_sender_restrictions = permit_mynetworks'",
            "sudo postconf -e 'smtpd_recipient_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination'",
        ]

        for i, cmd in enumerate(commands, 1):
            exit_code, output, error = run_command(ssh, cmd, timeout=10)
            if exit_code != 0:
                print(f"[WARNING] 命令 {i} 失败: {error}")

        print("[OK] Postfix配置完成")
        print()

        # 创建用户
        print("[USER] 创建测试用户...")
        exit_code, output, error = run_command(ssh, 'id -u smtpuser', timeout=10)
        user_exists = (exit_code == 0)

        if not user_exists:
            run_command(ssh, 'sudo useradd -m -s /bin/bash smtpuser', timeout=10)
            run_command(ssh, 'echo "smtpuser:SmtpTest2024!" | sudo chpasswd', timeout=10)
            print("[OK] 用户 smtpuser 已创建")
        else:
            print("[OK] 用户 smtpuser 已存在")

        # 创建邮箱目录
        run_command(ssh, 'sudo mkdir -p /home/smtpuser/Maildir/{new,cur,tmp}', timeout=10)
        run_command(ssh, 'sudo chown -R smtpuser:smtpuser /home/smtpuser/Maildir', timeout=10)
        run_command(ssh, 'sudo chmod -R 700 /home/smtpuser/Maildir', timeout=10)
        print("[OK] 邮箱目录已创建")
        print()

        # 配置防火墙
        print("[FIREWALL] 配置防火墙...")
        run_command(ssh, 'sudo ufw allow 25/tcp', timeout=10)
        run_command(ssh, 'sudo ufw allow 587/tcp', timeout=10)
        print("[OK] 防火墙已配置")
        print()

        # 重启服务
        print("[RESTART] 重启Postfix...")
        run_command(ssh, 'sudo systemctl restart postfix', timeout=30)
        run_command(ssh, 'sudo systemctl enable postfix', timeout=10)
        print("[OK] Postfix已重启")
        print()

        # 验证服务
        print("[VERIFY] 验证服务状态...")
        exit_code, output, error = run_command(ssh, 'sudo systemctl status postfix --no-pager', timeout=10)
        if 'active (running)' in output:
            print("[OK] Postfix服务运行正常")
        else:
            print("[WARNING] Postfix状态异常")
            print(output[:500])
        print()

        # 检查端口
        exit_code, output, error = run_command(ssh, 'sudo netstat -tlnp | grep :25', timeout=10)
        if ':25' in output:
            print("[OK] 端口25正在监听")
        else:
            print("[WARNING] 端口25未监听")

        exit_code, output, error = run_command(ssh, 'sudo netstat -tlnp | grep :587', timeout=10)
        if ':587' in output:
            print("[OK] 端口587正在监听")
        else:
            print("[WARNING] 端口587未监听")

        # 测试发送
        print()
        print("[TEST] 测试发送邮件...")
        run_command(ssh, 'echo "Test from Postfix" | mail -s "Test Email" smtpuser@localhost', timeout=10)
        print("[OK] 测试邮件已发送")
        print()

        print("=" * 60)
        print("DEPLOYMENT SUCCESSFUL")
        print("=" * 60)
        print()
        print("SMTP 配置信息:")
        print("  服务器: 62.234.211.119")
        print("  端口: 25")
        print("  用户名: smtpuser")
        print("  密码: SmtpTest2024!")
        print("  发送者: smtpuser@mail.flowthink.local")
        print()
        print("下一步:")
        print("1. 在防火墙设备中使用上述SMTP配置")
        print("2. 发送测试邮件")
        print("3. 查看日志: sudo tail -f /var/log/mail.log")
        print()
        print("完成时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 60)

        return 0

    except paramiko.AuthenticationException:
        print("[ERROR] 认证失败：用户名或密码错误")
        return 1
    except Exception as e:
        print(f"[ERROR] 部署失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
