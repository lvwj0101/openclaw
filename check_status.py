#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查apt和Postfix状态"""
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

    print("[CONNECT] 连接服务器...")
    try:
        ssh.connect(**SERVER, timeout=10)
        print("[OK] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查apt进程...")
    output = run(ssh, 'ps aux | grep -E "(apt|dpkg)" | grep -v grep')
    if output.strip():
        print(f"[RUNNING] 发现apt进程:")
        print(output)
    else:
        print("[OK] 没有apt进程")

    print()
    print("[2] 检查Postfix...")
    output = run(ssh, 'which postfix')
    if output.strip():
        print(f"[OK] Postfix已安装: {output.strip()}")
    else:
        print("[NOT INSTALLED] Postfix未安装")

    print()
    print("[3] 检查用户smtpuser...")
    output = run(ssh, 'id -u smtpuser')
    if output.strip():
        print("[OK] 用户smtpuser存在")
    else:
        print("[NOT EXIST] 用户smtpuser不存在")

    print()
    print("[4] 检查Postfix服务...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output:
        print("[OK] Postfix服务运行正常")
    elif 'inactive' in output:
        print("[STOPPED] Postfix服务已停止")
    else:
        print("[UNKNOWN] 服务状态未知")

    print()
    print("[5] 检查端口25...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
    else:
        print("[NOT LISTENING] 端口25未监听")

    print()
    print("="*50)
    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
