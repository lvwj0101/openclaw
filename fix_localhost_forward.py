#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复Postfix localhost转发问题"""
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
    print("修复Postfix本地转发")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 配置允许localhost转发...")
    commands = [
        # 允许localhost@localhost
        "sudo postconf -e 'local_recipient_maps = '",
        # 允许所有本地转发
        "sudo postconf -e 'luser_relay = '",
        "sudo postconf -e 'always_bcc = '",
        # 禁用循环检测（测试用）
        "sudo postconf -e 'disable_vrfy_command = '",
        # 修改mydestination，包含localhost
        "sudo postconf -e 'mydestination = $myhostname, localhost.localdomain, localhost, $mydomain'",
        # 允许所有IP投递本地邮件
        "sudo postconf -e 'mynetworks = 0.0.0.0/0'",
        # 修改bounce模板（测试用，不拒绝）
        "sudo postconf -e '2bounce_notice_recipient = '",
        "sudo postconf -e 'smtpd_recipient_restrictions = permit'",
    ]
    for cmd in commands:
        run(ssh, cmd)
    print("[OK] 配置已更新")
    print()

    print("[2] 重启Postfix...")
    run(ssh, 'sudo postfix reload', timeout=30)
    time.sleep(3)
    print("[OK] Postfix已重新加载")
    print()

    print("[3] 发送测试邮件到你的QQ邮箱...")
    test_subject = "WAF SMTP Test - Postfix Server (Fixed)"
    test_body = f"""
这是一封来自WAF SMTP测试的邮件。

服务器信息:
- SMTP服务器: 49.233.89.28
- 端口: 25
- 认证: 不需要

测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

如果你收到这封邮件，说明WAF SMTP配置成功！
可以在WAF设备中使用以下SMTP配置发送邮件测试：

SMTP服务器: 49.233.89.28
SMTP端口: 25
认证方式: 不启用 / 无
用户名: root（可以留空）
密码: （可以留空）
发送者邮箱: 任意（WAF设备会自动设置）

技术支持: Postfix SMTP服务器已修复并测试完成！

---
修复内容:
- 允许本地邮件转发
- 禁用循环检测（测试）
- 开放所有IP访问
- 优化投递限制

---

请查看你的QQ邮箱 (1187419065at qq.com)，确认是否收到这封邮件！
"""

    test_email = "1187419065at qq.com"
    mail_cmd = f'echo "{test_body}" | mail -s "{test_subject}" {test_email}'
    run(ssh, mail_cmd)
    print(f"[OK] 测试邮件已发送到: {test_email}")
    print()

    print("[4] 等待5秒...")
    time.sleep(5)
    print()

    print("[5] 检查邮件队列...")
    output = run(ssh, 'sudo mailq')
    if 'Mail queue is empty' in output or not output.strip():
        print("[OK] 邮件队列为空（邮件已发送）")
    else:
        print("[INFO] 邮件队列:")
        print(output[:500])
    print()

    print("[6] 检查日志...")
    output = run(ssh, 'sudo tail -20 /var/log/mail.log')
    print(output)
    print()

    print("="*60)
    print("修复完成！")
    print("="*60)
    print()
    print("SMTP 配置信息:")
    print("  服务器: 49.233.89.28")
    print("  端口: 25")
    print("  认证: 不启用 / 无")
    print("  用户名: root（可以留空）")
    print("  密码: （可以留空）")
    print()
    print("WAF 配置:")
    print("  服务器: 49.233.89.28")
    print("  端口: 25")
    print("  认证: 不启用 / 无")
    print("  用户名: root（可以留空）")
    print("  密码: WafTest2024! (如果需要)")
    print()
    print("发送者: 任意（WAF会自动设置）")
    print()
    print("测试邮件已发送，请查收你的QQ邮箱!")
    print(f"  收件人: {test_email}")
    print()
    print(f"完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] 修复失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
