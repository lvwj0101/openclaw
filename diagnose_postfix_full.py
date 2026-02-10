#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全面检查和修复Postfix"""
import paramiko
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '62.234.211.119',
    'port': 22,
    'username': 'ubuntu',
    'password': '1qaz#EDC%TGB'
}

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("WAF邮件发送功能 - 全面诊断")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查Postfix服务状态...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    print(output)

    print()
    print("[2] 检查Postfix进程...")
    output = run(ssh, 'ps aux | grep -E "master|qmgr|pickup|cleanup|bounce" | grep -v grep')
    if output.strip():
        print("[OK] Postfix进程运行中:")
        print(output)
    else:
        print("[FAIL] Postfix进程未运行")

    print()
    print("[3] 检查端口25监听...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听:")
        print(output)
    else:
        print("[FAIL] 端口25未监听")

    print()
    print("[4] 检查端口587监听...")
    output = run(ssh, 'sudo netstat -tlnp | grep :587')
    if ':587' in output:
        print("[OK] 端口587正在监听")
    else:
        print("[INFO] 端口587未监听（可选）")

    print()
    print("[5] 检查Postfix配置...")
    output = run(ssh, 'sudo postconf -n | grep -E "(inet|myhostname|mydomain|mynetworks|smtpd_sasl)"')
    print(output)

    print()
    print("[6] 检查邮件队列...")
    output = run(ssh, 'sudo mailq')
    if 'Mail queue is empty' in output or not output.strip():
        print("[OK] 邮件队列为空")
    else:
        print("[WARNING] 邮件队列中有邮件:")
        print(output)

    print()
    print("[7] 检查系统防火墙...")
    output = run(ssh, 'sudo ufw status numbered | head -15')
    print(output)

    print()
    print("[8] 检查邮件日志...")
    output = run(ssh, 'sudo tail -20 /var/log/mail.log 2>/dev/null || echo "日志文件不存在"')
    print(output)

    print()
    print("[9] 检查错误日志...")
    output = run(ssh, 'sudo tail -20 /var/log/mail.err 2>/dev/null || echo "错误日志文件不存在"')
    print(output)

    print()
    print("[10] 检查邮件别名...")
    output = run(ssh, 'sudo postconf alias_maps')
    print(output)

    print()
    print("="*60)
    print("诊断完成")
    print("="*60)

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[ERROR] 诊断失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
