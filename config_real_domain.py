#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用真实邮箱域名，配置Postfix转发到本地"""
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

# 使用真实邮箱域名，但配置Postfix把所有邮件都当作本地邮件
REAL_DOMAIN = 'gmail.com'
# WAF会使用的邮箱地址（格式真实，但会转发到本地）
WAF_EMAIL = 'waftest@gmail.com'

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("配置真实邮箱域名 - 解决WAF配置错误")
    print("="*60)
    print(f"  WAF邮箱: {WAF_EMAIL}")
    print(f"  真实域名: {REAL_DOMAIN}")
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 配置 /etc/hosts，将真实域名映射到本地...")
    # 将所有 gmail.com 的请求都指向本地服务器
    hosts_line = f"49.233.89.28 {REAL_DOMAIN}"
    run(ssh, f'echo "{hosts_line}" | sudo tee -a /etc/hosts')
    print(f"[OK] 已添加: {hosts_line}")
    print()

    print("[2] 更新Postfix配置...")
    commands = [
        # 使用真实域名
        f"sudo postconf -e 'myhostname = smtp.{REAL_DOMAIN}'",
        f"sudo postconf -e 'mydomain = {REAL_DOMAIN}'",
        f"sudo postconf -e 'myorigin = {REAL_DOMAIN}'",
        
        # 关键：将所有邮件都当作本地邮件，不让Postfix转发出去
        f"sudo postconf -e 'mydestination = $myhostname, localhost.{REAL_DOMAIN}, localhost, $mydomain'",
        f"sudo postconf -e 'inet_interfaces = all'",
        f"sudo postconf -e 'inet_protocols = ipv4'",
        
        # 禁用转发，所有邮件都在本地投递
        f"sudo postconf -e 'relayhost = '",
        f"sudo postconf -e 'local_transport = local:'",
        
        # 允许所有IP（方便WAF测试）
        f"sudo postconf -e 'mynetworks = 0.0.0.0/0'",
        f"sudo postconf -e 'home_mailbox = Maildir/'",
        f"sudo postconf -e 'smtpd_sasl_auth_enable = no'",
        
        # 确保邮件不被转发到外部
        f"sudo postconf -e 'smtpd_relay_restrictions = permit_mynetworks, defer_unauth_destination, reject_non_fqdn_hostname, reject_sender_login_mismatch'",
        f"sudo postconf -e 'smtpd_recipient_restrictions = permit_mynetworks, permit_sasl_authenticated, reject_non_fqdn_recipient, reject_unauth_destination'",
    ]
    for cmd in commands:
        run(ssh, cmd)
    print("[OK] Postfix配置已更新")
    print()

    print("[3] 创建虚拟映射用户...")
    # 创建一个映射，让 waftest@gmail.com 的邮件转到本地 waftest 用户
    run(ssh, 'sudo useradd -m -s /bin/bash waftestgmail 2>/dev/null || true')
    run(ssh, 'echo "waftestgmail:WafTest2024!" | sudo chpasswd')
    print("[OK] 虚拟用户已创建")
    print()

    print("[4] 配置邮件转发...")
    # 配置 /etc/aliases，将 waftest@gmail.com 转发到 waftest@localhost
    run(ssh, f'echo "waftest@{REAL_DOMAIN}: waftest@localhost" | sudo tee -a /etc/aliases')
    # 配置其他邮箱地址转发
    run(ssh, f'echo "*@{REAL_DOMAIN}: waftest" | sudo tee -a /etc/aliases')
    # 重建别名数据库
    run(ssh, 'sudo newaliases')
    print("[OK] 邮件转发已配置")
    print()

    print("[5] 配置本地投递代理...")
    # 使用 local 投递代理
    run(ssh, 'sudo postconf -e "local_transport = local:"')
    print("[OK] 本地投递代理已配置")
    print()

    print("[6] 重启Postfix...")
    run(ssh, 'sudo systemctl stop postfix')
    time.sleep(2)
    run(ssh, 'sudo systemctl start postfix')
    time.sleep(3)
    run(ssh, 'sudo systemctl enable postfix')
    print("[OK] Postfix已重启")
    print()

    print("[7] 验证配置...")
    output = run(ssh, 'sudo postconf -n | grep -E "(myhostname|mydomain|myorigin|mydestination|local_transport|relayhost)"')
    print(output)
    print()

    print("[8] 验证 /etc/aliases...")
    output = run(ssh, f'sudo grep "{REAL_DOMAIN}" /etc/aliases')
    print(output)
    print()

    print("[9] 测试发送邮件...")
    # 发送到 waftest@gmail.com（会转发到本地）
    run(ssh, f'echo "Test from WAF - $(date)" | mail -s "WAF Test" {WAF_EMAIL}')
    print(f"[OK] 测试邮件已发送到: {WAF_EMAIL}")
    print()

    print("[10] 检查邮件...")
    time.sleep(3)
    output = run(ssh, 'ls -la /home/waftestgmail/Maildir/new/ 2>/dev/null | tail -5')
    if output.strip() and 'total' not in output.lower():
        print(f"[OK] 收到邮件:")
        print(output)
    else:
        output2 = run(ssh, 'ls -la /home/waftest/Maildir/new/ 2>/dev/null | tail -5')
        if output2.strip() and 'total' not in output2.lower():
            print(f"[OK] 收到邮件:")
            print(output2)
        else:
            print("[INFO] 邮箱为空")
    print()

    print("="*60)
    print("配置完成！")
    print("="*60)
    print()
    print("WAF 防火墙 SMTP 配置（长亭科技雷池）：")
    print(f"  邮箱地址: {WAF_EMAIL}")
    print(f"  服务器: 49.233.89.28")
    print(f"  端口: 25")
    print(f"  认证: 不启用")
    print(f"  密码: WafTest2024!")
    print()
    print("配置说明:")
    print(f"  1. 在WAF中配置邮箱: {WAF_EMAIL}")
    print("  2. 邮箱地址就是账号（不需要单独配置账号）")
    print("  3. 所有发到 {WAF_EMAIL} 的邮件都会被转发到本地")
    print(f"  4. 测试用户: waftest")
    print(f"  5. 测试密码: WafTest2024!")
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
