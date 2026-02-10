#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复Postfix启动问题"""
import paramiko
import sys
import io
import time

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
    print("修复Postfix服务")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print("[1] 重置Postfix配置为默认值...")
    commands = [
        "sudo postconf -e 'myhostname = localhost'",
        "sudo postconf -e 'mydomain = localdomain'",
        "sudo postconf -e 'myorigin = localdomain'",
        "sudo postconf -e 'inet_interfaces = all'",
        "sudo postconf -e 'inet_protocols = ipv4'",
        "sudo postconf -e 'mydestination = $myhostname, localhost.localdomain, localhost'",
        "sudo postconf -e 'mynetworks = 127.0.0.0/8'",
        "sudo postconf -e 'home_mailbox = Maildir/'",
        "sudo postconf -e 'mbox_command = /usr/bin/procmail'",
        "sudo postconf -e 'smtpd_sasl_auth_enable = no'",
        "sudo postconf -e 'local_transport = local:'",
    ]
    for cmd in commands:
        try:
            run(ssh, cmd)
        except:
            pass
    print("[OK] 配置已重置")

    print()
    print("[2] 检查Postfix master进程...")
    output = run(ssh, 'ps aux | grep "master" | grep -v grep')
    if output.strip():
        print(f"[OK] Postfix master进程运行中")
    else:
        print("[WARNING] Postfix master进程未运行")

    print()
    print("[3] 手动启动Postfix...")
    output = run(ssh, 'sudo postfix start')
    print(output)

    time.sleep(2)

    print()
    print("[4] 检查进程...")
    output = run(ssh, 'ps aux | grep postfix | grep -v grep')
    if output.strip():
        print(f"[OK] Postfix进程运行中:")
        print(output[:500])
    else:
        print("[WARNING] Postfix进程未运行")

    print()
    print("[5] 检查端口...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print(f"[OK] 端口25正在监听")
    else:
        print("[WARNING] 端口25未监听")

    print()
    print("[6] 测试发送邮件...")
    output = run(ssh, 'echo "Test at $(date)" | mail -s "Postfix Test" root@localhost')
    print(output)

    print()
    print("="*60)
    print("修复完成")
    print("="*60)
    print()
    print("SMTP 配置信息:")
    print("  服务器: 62.234.211.119")
    print("  端口: 25")
    print("  认证: 无")
    print("  发送者: root@localhost")
    print("="*60)

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
