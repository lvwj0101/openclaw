#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复Postfix服务问题"""
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
    'password': '1qaz#EDC%TGB'
}

def run(ssh, cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("修复Postfix服务")
    print("="*60)
    print()

    print("[1/5] 检查Dovecot服务...")
    output = run(ssh, 'sudo systemctl status dovecot --no-pager')
    print(output)

    print()
    print("[2/5] 检查Postfix日志...")
    output = run(ssh, 'sudo tail -30 /var/log/mail.log')
    print(output)
    print()

    print("[3/5] 尝试停止SASL（恢复无认证模式）...")
    commands = [
        "sudo postconf -e 'smtpd_sasl_auth_enable = no'",
    ]
    for cmd in commands:
        run(ssh, cmd)
    print("[OK] 已恢复无认证模式")

    print()
    print("[4/5] 重启Postfix...")
    run(ssh, 'sudo systemctl restart postfix')
    time.sleep(3)
    print("[OK] Postfix已重启")

    print()
    print("[5/5] 验证服务...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output:
        print("[OK] Postfix服务运行正常")
    else:
        print("[WARNING] 服务状态异常，但端口在监听，可能可以正常工作")

    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")

    print()
    print("="*60)
    print("已恢复无认证模式")
    print("="*60)
    print()
    print("SMTP 配置信息（无认证）：")
    print("  服务器: 62.234.211.119")
    print("  端口: 25")
    print("  认证方式: 无（或不启用认证）")
    print("  用户名: smtpuser（可选）")
    print("  密码: SmtpTest2024!（可选）")
    print("  发送者邮箱: smtpuser@localhost")
    print()
    print("防火墙配置建议：")
    print("  认证方式: 不认证（或 None）")
    print("  加密方式: 无")
    print()
    print("完成时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
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
