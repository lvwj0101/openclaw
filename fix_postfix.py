#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查并修复Postfix配置"""
import paramiko
import sys
import io

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
    ssh.connect(**SERVER, timeout=10)

    print("[1] 检查当前配置...")
    output = run(ssh, 'sudo postconf -n')
    print(output)
    print()

    print("[2] 检查配置文件语法...")
    output = run(ssh, 'sudo postfix check')
    print(output)
    print()

    print("[3] 尝试使用简单配置...")
    run(ssh, 'sudo postconf -e "myhostname = localhost"')
    run(ssh, 'sudo postconf -e "mydomain = localdomain"')
    run(ssh, 'sudo postconf -e "myorigin = localdomain"')
    run(ssh, 'sudo postconf -e "inet_interfaces = all"')
    run(ssh, 'sudo postconf -e "inet_protocols = ipv4"')
    print("[OK] 配置已更新")
    print()

    print("[4] 重启Postfix...")
    run(ssh, 'sudo systemctl restart postfix')
    time.sleep(2)
    print("[OK] Postfix已重启")
    print()

    print("[5] 检查状态...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    print(output)
    print()

    print("[6] 检查端口...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if output:
        print("[OK] 端口25正在监听:")
        print(output)
    else:
        print("[WARNING] 端口25未监听")

    print()
    print("="*60)
    print("SMTP 配置信息:")
    print("  服务器: 62.234.211.119")
    print("  端口: 25")
    print("  用户名: smtpuser")
    print("  密码: SmtpTest2024!")
    print("  发送者: smtpuser@localhost")
    print("="*60)

    ssh.close()

if __name__ == "__main__":
    import time
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
