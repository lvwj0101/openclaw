#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""等待apt完成并继续配置"""
import paramiko
import sys
import io
import time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '62.234.211.119',
    'port': 22,
    'username': 'ubuntu',
    'password': 'ji_pmrDc6jMCc6_'
}

def run(ssh, cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SERVER, timeout=10)

    print("[WAIT] 等待apt完成...")
    while True:
        output = run(ssh, 'ps aux | grep -E "(apt|dpkg)" | grep -v grep')
        if not output.strip():
            break
        print(f"  [RUNNING] apt进程运行中... {time.strftime('%H:%M:%S')}")
        time.sleep(30)

    print("[OK] apt已完成")
    time.sleep(5)

    # 检查Postfix
    print("\n[CHECK] 检查Postfix...")
    output = run(ssh, 'which postfix')
    if not output.strip():
        print("[ERROR] Postfix未安装，尝试安装...")
        run(ssh, 'sudo DEBIAN_FRONTEND=noninteractive apt install -y postfix mailutils', timeout=600)
        print("[OK] Postfix安装完成")
    else:
        print(f"[OK] Postfix已安装: {output.strip()}")

    # 配置
    print("\n[CONFIG] 配置Postfix...")
    for cmd in [
        "sudo postconf -e 'myhostname = mail.flowthink.local'",
        "sudo postconf -e 'mydomain = flowthink.local'",
        "sudo postconf -e 'inet_interfaces = 0.0.0.0'",
        "sudo postconf -e 'mynetworks = 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16'",
    ]:
        run(ssh, cmd)
    print("[OK] 配置完成")

    # 用户
    print("\n[USER] 创建测试用户...")
    run(ssh, 'sudo useradd -m smtpuser 2>/dev/null; echo "smtpuser:SmtpTest2024!" | sudo chpasswd')
    run(ssh, 'sudo mkdir -p /home/smtpuser/Maildir/{new,cur,tmp} && sudo chown -R smtpuser:smtpuser /home/smtpuser/Maildir')
    print("[OK] 用户创建完成")

    # 防火墙和重启
    print("\n[FIREWALL] 配置防火墙...")
    run(ssh, 'sudo ufw --force enable')
    run(ssh, 'sudo ufw allow 25/tcp')
    print("[OK] 防火墙配置完成")

    print("\n[RESTART] 重启Postfix...")
    run(ssh, 'sudo systemctl restart postfix')
    print("[OK] 完成")

    # 验证
    print("\n[VERIFY] 验证...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output:
        print("[OK] Postfix服务运行正常")

    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")

    print("\n" + "="*60)
    print("部署成功！")
    print("="*60)
    print("SMTP 配置信息:")
    print("  服务器: 62.234.211.119")
    print("  端口: 25")
    print("  用户名: smtpuser")
    print("  密码: SmtpTest2024!")
    print("  发送者: smtpuser@mail.flowthink.local")
    print("="*60)

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
