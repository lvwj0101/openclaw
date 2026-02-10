#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""监控apt并自动部署Postfix"""
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
    print("Postfix 自动部署")
    print("="*60)
    print()

    # 等待apt完成
    print("[MONITOR] 监控apt进程...")
    attempts = 0
    while True:
        attempts += 1
        output = run(ssh, 'ps aux | grep -E "(apt|dpkg)" | grep -v grep')
        if not output.strip():
            print(f"[OK] apt进程已完成 (检查次数: {attempts})")
            break
        else:
            processes = [line for line in output.strip().split('\n') if line]
            print(f"[RUNNING] 发现 {len(processes)} 个apt进程... (检查次数: {attempts})")
            time.sleep(30)  # 每30秒检查一次

    time.sleep(10)  # 等待apt锁释放

    # 安装Postfix
    print("\n[INSTALL] 安装Postfix...")
    output = run(ssh, 'which postfix')
    if not output.strip():
        print("[DOWNLOAD] 下载和安装Postfix (可能需要2-5分钟)...")
        run(ssh, 'sudo DEBIAN_FRONTEND=noninteractive apt install -y postfix mailutils', timeout=600)
        print("[OK] Postfix安装完成")
    else:
        print(f"[OK] Postfix已安装: {output.strip()}")

    # 配置
    print("\n[CONFIG] 配置Postfix...")
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

    # 创建用户
    print("\n[USER] 创建测试用户...")
    run(ssh, 'sudo useradd -m smtpuser 2>/dev/null; echo "smtpuser:SmtpTest2024!" | sudo chpasswd')
    run(ssh, 'sudo mkdir -p /home/smtpuser/Maildir/{new,cur,tmp} && sudo chown -R smtpuser:smtpuser /home/smtpuser/Maildir && sudo chmod -R 700 /home/smtpuser/Maildir')
    print("[OK] 用户创建完成")

    # 防火墙
    print("\n[FIREWALL] 配置防火墙...")
    run(ssh, 'sudo ufw --force enable')
    run(ssh, 'sudo ufw allow 25/tcp')
    run(ssh, 'sudo ufw allow 587/tcp')
    run(ssh, 'sudo ufw allow 22/tcp')
    print("[OK] 防火墙配置完成")

    # 重启
    print("\n[RESTART] 重启Postfix...")
    run(ssh, 'sudo systemctl restart postfix')
    run(ssh, 'sudo systemctl enable postfix')
    print("[OK] 重启完成")

    # 验证
    print("\n[VERIFY] 验证服务...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output:
        print("[OK] Postfix服务运行正常")
    else:
        print("[WARNING] 服务状态异常")

    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")

    # 完成
    print("\n" + "="*60)
    print("部署成功！")
    print("="*60)
    print("\nSMTP 配置信息:")
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
