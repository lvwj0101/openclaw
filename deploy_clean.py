#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从头重新部署Postfix"""
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

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SERVER, timeout=10)

    print("="*60)
    print("Postfix 全新部署")
    print("="*60)
    print()

    # 步骤1：停止所有apt进程
    print("[STEP 1] 停止所有apt/dpkg进程...")
    run(ssh, 'sudo pkill -9 -f apt', timeout=10)
    run(ssh, 'sudo pkill -9 -f dpkg', timeout=10)
    run(ssh, 'sudo pkill -9 -f apt-get', timeout=10)
    print("[OK] 进程已停止")
    time.sleep(5)

    # 步骤2：清理所有apt锁
    print("\n[STEP 2] 清理apt锁...")
    run(ssh, 'sudo rm -f /var/lib/apt/lists/lock', timeout=10)
    run(ssh, 'sudo rm -f /var/lib/dpkg/lock*', timeout=10)
    run(ssh, 'sudo rm -f /var/cache/apt/archives/lock', timeout=10)
    run(ssh, 'sudo rm -f /var/lib/dpkg/lock-frontend', timeout=10)
    run(ssh, 'sudo rm -f /var/lib/dpkg/lock', timeout=10)
    run(ssh, 'sudo dpkg --configure -a', timeout=120)
    print("[OK] 锁已清理")

    # 步骤3：apt update
    print("\n[STEP 3] apt update (1-2分钟)...")
    run(ssh, 'sudo apt update', timeout=180)
    print("[OK] update完成")

    # 步骤4：安装Postfix
    print("\n[STEP 4] 安装Postfix (2-3分钟)...")
    run(ssh, 'sudo DEBIAN_FRONTEND=noninteractive apt install -y postfix mailutils', timeout=600)
    print("[OK] Postfix安装完成")

    # 步骤5：配置
    print("\n[STEP 5] 配置Postfix...")
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

    # 步骤6：用户
    print("\n[STEP 6] 创建测试用户...")
    run(ssh, 'sudo useradd -m smtpuser 2>/dev/null || true')
    run(ssh, 'echo "smtpuser:SmtpTest2024!" | sudo chpasswd')
    run(ssh, 'sudo mkdir -p /home/smtpuser/Maildir/{new,cur,tmp}')
    run(ssh, 'sudo chown -R smtpuser:smtpuser /home/smtpuser/Maildir')
    run(ssh, 'sudo chmod -R 700 /home/smtpuser/Maildir')
    print("[OK] 用户创建完成")

    # 步骤7：防火墙
    print("\n[STEP 7] 配置防火墙...")
    run(ssh, 'sudo ufw --force enable', timeout=30)
    run(ssh, 'sudo ufw allow 25/tcp')
    run(ssh, 'sudo ufw allow 587/tcp')
    run(ssh, 'sudo ufw allow 22/tcp')
    print("[OK] 防火墙配置完成")

    # 步骤8：重启
    print("\n[STEP 8] 重启Postfix...")
    run(ssh, 'sudo systemctl restart postfix', timeout=30)
    run(ssh, 'sudo systemctl enable postfix')
    print("[OK] 重启完成")

    # 步骤9：验证
    print("\n[STEP 9] 验证服务...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output:
        print("[OK] Postfix服务运行正常")
    else:
        print("[WARNING] 服务状态异常，但继续...")
        print(output[:300])

    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
    else:
        print("[WARNING] 端口25未监听，但继续...")

    # 完成
    print("\n" + "="*60)
    print("部署完成！")
    print("="*60)
    print("\nSMTP 配置信息:")
    print("  服务器: 62.234.211.119")
    print("  端口: 25")
    print("  用户名: smtpuser")
    print("  密码: SmtpTest2024!")
    print("  发送者: smtpuser@mail.flowthink.local")
    print("\n完成时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
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
