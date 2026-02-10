#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSH连接服务器并执行Postfix配置脚本
"""

import paramiko
import sys
import io

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

# Postfix配置脚本
POSTFIX_SCRIPT = '''#!/bin/bash

# ==========================================
# Postfix SMTP 服务配置脚本
# 用于测试防火墙邮件发送功能
# ==========================================

set -e

echo "========================================="
echo "Postfix SMTP 配置脚本"
echo "========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    echo "sudo bash $0"
    exit 1
fi

echo -e "\\033[1;33m[1/7] 更新系统包...\\033[0m"
apt update
apt upgrade -y

echo -e "\\033[1;33m[2/7] 安装Postfix...\\033[0m"
DEBIAN_FRONTEND=noninteractive apt install -y postfix mailutils

echo -e "\\033[1;33m[3/7] 配置主机名...\\033[0m"
postconf -e 'myhostname = mail.flowthink.local'
postconf -e 'mydomain = flowthink.local'
postconf -e 'myorigin = $mydomain'
postconf -e 'inet_interfaces = 0.0.0.0'
postconf -e 'inet_protocols = all'
postconf -e 'mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain'
postconf -e 'mynetworks = 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16'
postconf -e 'home_mailbox = Maildir/'
postconf -e 'smtpd_sasl_auth_enable = no'
postconf -e 'smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination'
postconf -e 'smtpd_client_restrictions = permit_mynetworks'
postconf -e 'smtpd_helo_required = yes'
postconf -e 'smtpd_helo_restrictions = permit_mynetworks'
postconf -e 'smtpd_sender_restrictions = permit_mynetworks'
postconf -e 'smtpd_recipient_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination'

echo -e "\\033[1;33m[4/7] 创建测试用户...\\033[0m"
if ! id -u smtpuser &>/dev/null; then
    useradd -m -s /bin/bash smtpuser
    echo "smtpuser:SmtpTest2024!" | chpasswd
    echo -e "\\033[0;32m✓ 测试用户已创建: smtpuser / SmtpTest2024!\\033[0m"
else
    echo -e "\\033[0;32m✓ 测试用户已存在\\033[0m"
fi

echo -e "\\033[1;33m[5/7] 配置防火墙...\\033[0m"
if command -v ufw &> /dev/null; then
    ufw allow 25/tcp
    ufw allow 587/tcp
    echo -e "\\033[0;32m✓ 已开放 SMTP 端口: 25, 587\\033[0m"
else
    echo -e "\\033[1;33m⚠ 未检测到 UFW，请手动开放端口 25 和 587\\033[0m"
fi

echo -e "\\033[1;33m[6/7] 重启Postfix服务...\\033[0m"
systemctl restart postfix
systemctl enable postfix

echo -e "\\033[1;33m[7/7] 创建邮箱目录...\\033[0m"
mkdir -p /home/smtpuser/Maildir/{new,cur,tmp}
chown -R smtpuser:smtpuser /home/smtpuser/Maildir
chmod -R 700 /home/smtpuser/Maildir

echo ""
echo -e "\\033[0;32m=========================================${NC}"
echo -e "\\033[0;32mPostfix 配置完成！${NC}"
echo -e "\\033[0;32m=========================================${NC}"
echo ""
echo "SMTP 配置信息："
echo "-----------------------------------"
echo "SMTP 服务器: 62.234.211.119"
echo "SMTP 端口: 25 (未加密) 或 587 (可选)"
echo "用户名: smtpuser"
echo "密码: SmtpTest2024!"
echo "发送者邮箱: smtpuser@mail.flowthink.local"
echo "-----------------------------------"
echo ""

echo -e "\\033[1;33m测试 Postfix 服务...\\033[0m"
echo "Test Email from Postfix" | mail -s "Test Email" smtpuser@localhost

echo ""
echo -e "\\033[0;32m✓ 配置完成！\\033[0m"
'''

def run_ssh_command(ssh, command):
    """执行SSH命令并返回输出"""
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    exit_code = stdout.channel.recv_exit_status()
    return exit_code, output, error

def main():
    print("[CONNECT] 正在连接服务器...")
    print(f"   地址: {SERVER['username']}@{SERVER['hostname']}:{SERVER['port']}")
    print()

    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[SUCCESS] 连接成功！")
        print()

        # 上传脚本到服务器
        print("[UPLOAD] 上Postfix配置脚本...")
        sftp = ssh.open_sftp()
        script_path = '/tmp/setup-postfix-smtp.sh'

        with sftp.file(script_path, 'w') as f:
            f.write(POSTFIX_SCRIPT)

        sftp.chmod(script_path, 0o755)
        print("[SUCCESS] 脚本上传完成")
        print()

        # 执行脚本
        print("[EXECUTE] 执行Postfix配置脚本...")
        print("-" * 60)

        exit_code, output, error = run_ssh_command(ssh, f'sudo bash {script_path}')

        print(output)
        if error:
            print(error, file=sys.stderr)
        print("-" * 60)

        if exit_code == 0:
            print("[SUCCESS] Postfix配置成功！")
        else:
            print(f"[ERROR] 配置失败，退出码: {exit_code}")
            return 1

        # 验证服务
        print()
        print("[VERIFY] 验证Postfix服务...")
        print("-" * 60)

        commands = [
            ("检查服务状态", "systemctl status postfix --no-pager"),
            ("检查端口监听", "netstat -tlnp | grep :25"),
            ("检查端口587", "netstat -tlnp | grep :587"),
        ]

        for name, cmd in commands:
            print(f"\n[CHECK] {name}...")
            exit_code, output, error = run_ssh_command(ssh, cmd)
            print(output)

        print("-" * 60)

        # 清理临时文件
        print()
        print("[CLEANUP] 清理临时文件...")
        run_ssh_command(ssh, f'rm -f {script_path}')
        print("[SUCCESS] 完成")

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
        print("[COMPLETE] 配置完成！现在可以在防火墙设备中使用这些SMTP配置了！")

        return 0

    except paramiko.AuthenticationException:
        print("[ERROR] 认证失败：用户名或密码错误")
        return 1
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
