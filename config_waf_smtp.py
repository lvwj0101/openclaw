#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在新服务器上配置SMTP用于WAF测试"""
import paramiko
import sys
import io
import time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '49.233.89.28',
    'port': 22,
    'username': 'ubuntu',
    'password': 'dyc#10010'
}

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("WAF邮件发送功能 - SMTP服务器配置")
    print("="*60)
    print(f"  服务器: {SERVER['hostname']}")
    print(f"  用户: {SERVER['username']}")
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查服务器信息...")
    output = run(ssh, 'hostname && whoami')
    print(f"[OK] 服务器信息:\n{output}")
    print()

    print("[2] 检查Postfix是否安装...")
    output = run(ssh, 'which postfix')
    postfix_installed = output.strip()

    if postfix_installed:
        print(f"[OK] Postfix已安装: {postfix_installed}")
        print()
        print("[2a] 检查Postfix服务状态...")
        output = run(ssh, 'sudo systemctl status postfix --no-pager')
        print(output)

        print()
        print("[2b] 检查Postfix进程...")
        output = run(ssh, 'ps aux | grep master | grep -v grep')
        if output.strip():
            print(f"[OK] Postfix master进程运行中")
        else:
            print(f"[INFO] Postfix master进程未运行")
    else:
        print("[INFO] Postfix未安装，需要安装")
        print()
        print("[2c] 安装Postfix...")
        output = run(ssh, 'sudo DEBIAN_FRONTEND=noninteractive apt update', timeout=180)
        output = run(ssh, 'sudo DEBIAN_FRONTEND=noninteractive apt install -y postfix mailutils', timeout=600)
        print("[OK] Postfix安装完成")

    print()
    print("[3] 配置Postfix用于WAF测试...")
    commands = [
        "sudo postconf -e 'myhostname = smtp-waf.local'",
        "sudo postconf -e 'mydomain = localdomain'",
        "sudo postconf -e 'myorigin = localdomain'",
        "sudo postconf -e 'inet_interfaces = all'",
        "sudo postconf -e 'inet_protocols = ipv4'",
        "sudo postconf -e 'mydestination = $myhostname, localhost.localdomain, localhost'",
        "sudo postconf -e 'mynetworks = 0.0.0.0/0'",  # 允许所有IP访问，方便WAF测试
        "sudo postconf -e 'home_mailbox = Maildir/'",
        "sudo postconf -e 'smtpd_sasl_auth_enable = no'",  # 不需要认证
        "sudo postconf -e 'smtpd_client_restrictions = permit'",
        "sudo postconf -e 'smtpd_relay_restrictions = permit'",
        "sudo postconf -e 'smtpd_recipient_restrictions = permit'",
    ]
    for cmd in commands:
        run(ssh, cmd)
    print("[OK] Postfix配置已更新")
    print()

    print("[4] 创建测试用户...")
    run(ssh, 'sudo useradd -m -s /bin/bash waftest 2>/dev/null || true')
    run(ssh, 'echo "waftest:WafTest2024!" | sudo chpasswd')
    print("[OK] 测试用户 waftest 已创建")
    print()

    print("[5] 配置防火墙...")
    run(ssh, 'sudo ufw --force enable')
    run(ssh, 'sudo ufw allow 25/tcp')
    run(ssh, 'sudo ufw allow 587/tcp')
    run(ssh, 'sudo ufw allow 22/tcp')
    print("[OK] 防火墙已配置")
    print()

    print("[6] 重启Postfix服务...")
    run(ssh, 'sudo systemctl restart postfix', timeout=30)
    run(ssh, 'sudo systemctl enable postfix')
    time.sleep(3)
    print("[OK] Postfix服务已重启")
    print()

    print("[7] 验证服务...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output or 'active (exited)' in output:
        print("[OK] Postfix服务运行正常")
    else:
        print("[WARNING] Postfix服务状态异常")

    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
    else:
        print("[WARNING] 端口25未监听")

    print()
    print("[8] 测试发送邮件...")
    run(ssh, 'echo "WAF Test Email from Postfix - $(date)" | mail -s "WAF SMTP Test" waftest@localhost')
    print("[OK] 测试邮件已发送到 waftest@localhost")
    print()

    print("[9] 检查Postfix配置...")
    output = run(ssh, 'sudo postconf -n | grep -E "(inet|myhostname|mydomain|mynetworks|smtpd_sasl)"')
    print(output)
    print()

    print("="*60)
    print("配置完成！")
    print("="*60)
    print()
    print("WAF 防火墙 SMTP 配置信息:")
    print("  服务器: 49.233.89.28")
    print("  端口: 25")
    print("  认证方式: 无（不启用认证）")
    print("  用户名: waftest（可以留空）")
    print("  密码: WafTest2024!（可以留空）")
    print("  发送者邮箱: waftest@localhost 或任意邮箱")
    print()
    print("在WAF设备中配置:")
    print("  SMTP服务器: 49.233.89.28")
    print("  SMTP端口: 25")
    print("  加密方式: 无（或不加密）")
    print("  认证: 不启用")
    print("  用户名: waftest（或留空）")
    print("  密码: （留空）")
    print("  发送者: waftest@localhost")
    print()
    print("测试步骤:")
    print("  1. 在WAF设备中配置上述SMTP信息")
    print("  2. 发送测试邮件")
    print("  3. 检查邮件是否发送成功")
    print()
    print("完成时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] 配置失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
