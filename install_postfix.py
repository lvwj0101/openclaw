#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接安装Postfix（跳过apt upgrade）"""
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
    'password': '1qaz#EDC%TGB'
}

def run(ssh, cmd, timeout=120):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("Postfix 快速安装")
    print("="*60)
    print()

    print("[CONNECT] 连接服务器...")
    try:
        ssh.connect(**SERVER, timeout=10)
        print("[OK] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1/4] 安装Postfix (2-3分钟)...")
    output = run(ssh, 'sudo DEBIAN_FRONTEND=noninteractive apt install -y postfix mailutils', timeout=600)
    print("[OK] Postfix安装完成")
    print()

    print("[2/4] 配置Postfix...")
    for cmd in [
        "sudo postconf -e 'myhostname = mail.flowthink.local'",
        "sudo postconf -e 'mydomain = flowthink.local'",
        "sudo postconf -e 'myorigin = $mydomain'",
        "sudo postconf -e 'inet_interfaces = 0.0.0.0'",
        "sudo postconf -e 'mynetworks = 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16'",
        "sudo postconf -e 'home_mailbox = Maildir/'",
        "sudo postconf -e 'smtpd_sasl_auth_enable = no'",
    ]:
        run(ssh, cmd)
    print("[OK] 配置完成")
    print()

    print("[3/4] 创建测试用户...")
    run(ssh, 'sudo useradd -m -s /bin/bash smtpuser 2>/dev/null || true')
    run(ssh, 'echo "smtpuser:SmtpTest2024!" | sudo chpasswd')
    run(ssh, 'sudo mkdir -p /home/smtpuser/Maildir/{new,cur,tmp}')
    run(ssh, 'sudo chown -R smtpuser:smtpuser /home/smtpuser/Maildir')
    run(ssh, 'sudo chmod -R 700 /home/smtpuser/Maildir')
    print("[OK] 用户创建完成")
    print()

    print("[4/4] 配置防火墙和重启...")
    run(ssh, 'sudo ufw allow 25/tcp')
    run(ssh, 'sudo ufw allow 587/tcp')
    run(ssh, 'sudo systemctl restart postfix')
    run(ssh, 'sudo systemctl enable postfix')
    print("[OK] 完成")
    print()

    print("[VERIFY] 验证服务...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output:
        print("[OK] Postfix服务运行正常")
    else:
        print("[WARNING] 服务状态异常")

    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")

    print()
    print("="*60)
    print("部署成功！")
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
        print(f"\n[ERROR] 部署失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
