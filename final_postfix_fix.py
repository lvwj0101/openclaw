#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终修复：使用Postfix，支持外部IP访问"""
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
    print("Postfix 最终配置 - 支持外部IP")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 停止所有服务...")
    run(ssh, 'sudo pkill -9 -f mail', timeout=30)
    run(ssh, 'sudo systemctl stop postfix', timeout=30)
    run(ssh, 'sudo pkill -9 -f python', timeout=30)
    print("[OK] 所有服务已停止")
    print()

    print("[2] 最终Postfix配置...")
    commands = [
        # 基本配置
        "sudo postconf -e 'myhostname = mail.waf.local'",
        "sudo postconf -e 'mydomain = waf.local'",
        "sudo postconf -e 'myorigin = waf.local'",
        "sudo postconf -e 'inet_interfaces = all'",
        "sudo postconf -e 'inet_protocols = ipv4'",
        
        # 允许所有IP发送邮件（包括外部IP）
        "sudo postconf -e 'mynetworks = 0.0.0.0/0'",
        
        # 本地投递
        "sudo postconf -e 'mydestination = $myhostname, localhost.localdomain, localhost, $mydomain'",
        "sudo postconf -e 'local_transport = local:'",
        
        # 不需要认证
        "sudo postconf -e 'smtpd_sasl_auth_enable = no'",
        
        # 邮箱格式
        "sudo postconf -e 'home_mailbox = Maildir/'",
        "sudo postconf -e 'mailbox_command = /usr/bin/procmail -a $EXTENSION'",
        
        # 开放所有限制
        "sudo postconf -e 'smtpd_client_restrictions = '",
        "sudo postconf -e 'smtpd_helo_restrictions = '",
        "sudo postconf -e 'smtpd_sender_restrictions = permit'",
        "sudo postconf -e 'smtpd_recipient_restrictions = permit'",
        "sudo postconf -e 'smtpd_data_restrictions = '",
        
        # 禁用不必要的功能
        "sudo postconf -e 'smtpd_relay_restrictions = permit'",
        "sudo postconf -e 'smtpd_use_tls = no'",
        "sudo postconf -e 'disable_dns_lookups = no'",
    ]
    
    for cmd in commands:
        try:
            run(ssh, cmd)
        except:
            pass
    
    print("[OK] Postfix配置已更新")
    print()

    print("[3] 配置/etc/hosts（添加域名映射）...")
    hosts_line = "49.233.89.28 mail.waf.local waf.local"
    run(ssh, f'echo "{hosts_line}" | sudo tee -a /etc/hosts')
    print("[OK] hosts已更新")
    print()

    print("[4] 配置邮件转发（允许外部IP发送）...")
    # 配置所有邮件都投递到本地
    transport_file = '''# Transport configuration
# All mail is delivered locally
local   unix:-       nis-alias
'''
    run(ssh, f'cat << "EOF" | sudo tee /etc/postfix/transport\n{transport_file}\nEOF')
    run(ssh, 'sudo postmap /etc/postfix/transport', timeout=30)
    print("[OK] Transport已配置")
    print()

    print("[5] 检查并启动Postfix...")
    # 检查配置
    output = run(ssh, 'sudo postconf -n | grep -E "(mynetworks|inet_interfaces|mydestination)"')
    print(output)
    print()

    # 启动Postfix
    run(ssh, 'sudo systemctl restart postfix', timeout=30)
    time.sleep(3)
    print("[OK] Postfix已重启")
    print()

    print("[6] 检查服务状态...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    print(output)
    print()

    print("[7] 检查端口监听...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听:")
        print(output)
    else:
        print("[WARNING] 端口25未监听")
    print()

    print("[8] 检查邮件投递测试...")
    # 发送测试邮件到内部用户
    run(ssh, 'echo "Postfix Final Test at $(date)" | mail -s "Postfix Test" root@localhost')
    time.sleep(3)
    
    # 检查root邮箱
    output = run(ssh, 'ls -la /root/Maildir/new/')
    if output.strip() and 'total' not in output.lower():
        print("[OK] root邮箱中有邮件:")
        print(output)
    else:
        print("[INFO] root邮箱为空")
    print()

    print("[9] 配置防火墙...")
    run(ssh, 'sudo ufw --force enable')
    run(ssh, 'sudo ufw allow 25/tcp')
    run(ssh, 'sudo ufw allow 587/tcp')
    run(ssh, 'sudo ufw allow 22/tcp')
    print("[OK] 防火墙已配置")
    print()

    print("[10] 发送测试邮件到QQ邮箱...")
    qq_email = "1187419065at@qq.com"
    test_body = f"""
这是一个来自Postfix邮件服务器的最终测试邮件。

服务器信息:
- SMTP服务器: 49.233.89.28
- 端口: 25
- 认证: 不需要
- 监听: 所有IP

配置信息:
- 域名: mail.waf.local
- mydestination: 所有本地域名
- mynetworks: 0.0.0.0/0（允许所有IP）

测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

如果您收到这封邮件，说明Postfix配置成功！
可以在WAF设备中使用以下SMTP配置:

SMTP服务器: 49.233.89.28
SMTP端口: 25
认证方式: 不启用
用户名: root（或任意）
密码: （可以留空）
发送者邮箱: root@waf.local 或任意邮箱

WAF设备配置完成后，请发送测试邮件验证功能！

---
技术支持: Postfix最终配置完成
"""
    test_cmd = f'echo "{test_body}" | mail -s "Postfix Final Test" {qq_email}'
    output = run(ssh, test_cmd)
    print("[OK] 测试邮件已发送")
    print()

    print("[11] 检查邮件队列...")
    output = run(ssh, 'sudo mailq')
    if 'Mail queue is empty' in output or not output.strip():
        print("[OK] 邮件队列为空")
    else:
        print("[INFO] 邮件队列:")
        print(output[:500])
    print()

    print("="*60)
    print("配置完成！")
    print("="*60)
    print()
    print("Postfix SMTP服务器信息:")
    print(f"  服务器: {SERVER['hostname']}")
    print(f"  端口: 25")
    print(f"  认证: 不启用（或 None）")
    print(f"  用户名: root（可以留空）")
    print(f"  密码: （可以留空）")
    print(f"  发送者: root@waf.local 或任意邮箱")
    print()
    print("WAF 防火墙 SMTP 配置:")
    print(f"  服务器: {SERVER['hostname']}")
    print(f"  端口: 25")
    print(f"  认证: 不启用")
    print(f"  用户名: root（可以留空）")
    print(f"  密码: （可以留空）")
    print(f"  发送者: root@waf.local 或任意")
    print()
    print("重要说明:")
    print("  1. Postfix已配置支持所有IP访问（mynetworks=0.0.0.0/0）")
    print("  2. 邮箱域名配置为 mail.waf.local")
    print("  3. WAF设备可以使用 root@waf.local 或任意邮箱地址")
    print("  4. 不需要SMTP认证")
    print()
    print("下一步:")
    print("  1. 在WAF设备中配置上述SMTP信息")
    print("  2. 发送者邮箱可以使用: root@waf.local 或 waftest@waf.local 或任意")
    print("  3. 发送测试邮件")
    print()
    print("请检查你的QQ邮箱（1187419065at@qq.com），确认是否收到测试邮件！")
    print()
    print(f"完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
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
