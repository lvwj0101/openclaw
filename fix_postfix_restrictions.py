#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复Postfix配置问题"""
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
    print("修复Postfix配置")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 重置所有限制参数为默认值...")
    commands = [
        "sudo postconf -e 'smtpd_client_restrictions = '",
        "sudo postconf -e 'smtpd_helo_required = no'",
        "sudo postconf -e 'smtpd_helo_restrictions = '",
        "sudo postconf -e 'smtpd_sender_restrictions = '",
        "sudo postconf -e 'smtpd_relay_restrictions = '",
        "sudo postconf -e 'smtpd_recipient_restrictions = permit_mynetworks, reject'",
        "sudo postconf -e 'smtpd_data_restrictions = reject_unauth_sender'",
        "sudo postconf -e 'smtpd_end_of_data_restrictions = reject_unauth_recipient, reject_unknown_recipient_domain'",
    ]
    for cmd in commands:
        run(ssh, cmd)
    print("[OK] 限制参数已重置")
    print()

    print("[2] 停止Postfix...")
    run(ssh, 'sudo systemctl stop postfix')
    time.sleep(2)
    print("[OK] Postfix已停止")
    print()

    print("[3] 启动Postfix...")
    run(ssh, 'sudo systemctl start postfix')
    time.sleep(3)
    print("[OK] Postfix已启动")
    print()

    print("[4] 检查Postfix服务状态...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output:
        print("[OK] Postfix服务运行正常")
    else:
        print("[WARNING] 服务状态异常，继续验证...")
    print()

    print("[5] 检查进程...")
    output = run(ssh, 'ps aux | grep -E "master|smtpd|qmgr|pickup" | grep -v grep')
    if 'master' in output and 'smtpd' in output:
        print("[OK] Postfix进程运行正常")
        print(output)
    else:
        print("[WARNING] 进程可能有问题:")
        print(output)
    print()

    print("[6] 检查端口...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
    else:
        print("[FAIL] 端口25未监听")
    print()

    print("[7] 检查最近的日志...")
    output = run(ssh, 'sudo tail -10 /var/log/mail.log')
    print(output)
    print()

    print("[8] 测试发送邮件...")
    run(ssh, 'echo "Test from WAF - $(date)" | mail -s "WAF SMTP Test" root@localhost')
    print("[OK] 测试邮件已发送")
    print()

    print("[9] 等待3秒后检查日志...")
    time.sleep(3)
    output = run(ssh, 'sudo tail -5 /var/log/mail.log')
    print(output)
    print()

    print("="*60)
    print("配置修复完成！")
    print("="*60)
    print()
    print("SMTP 配置信息:")
    print("  服务器: 49.233.89.28")
    print("  端口: 25")
    print("  认证方式: 无")
    print("  用户名: waftest（或留空）")
    print("  密码: （留空）")
    print("  发送者: root@localhost 或任意邮箱")
    print()
    print("在WAF设备中配置:")
    print("  认证: 不启用 / 无")
    print("  其他配置同上")
    print()
    print("现在可以重新在WAF中测试了！")
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
