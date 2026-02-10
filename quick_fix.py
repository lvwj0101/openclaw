#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速检查和修复"""
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

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 恢复无认证模式...")
    run(ssh, 'sudo postconf -e "smtpd_sasl_auth_enable = no"')
    run(ssh, 'sudo postconf -e "smtpd_sasl_type = "')
    print("[OK] 配置已更新")

    print()
    print("[2] 重启Postfix...")
    run(ssh, 'sudo systemctl restart postfix', timeout=30)
    time.sleep(3)
    print("[OK] Postfix已重启")

    print()
    print("[3] 检查服务状态...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output:
        print("[OK] Postfix服务运行正常")
    elif 'active (exited)' in output:
        print("[WARNING] 服务启动后退出，但端口可能在监听")
    else:
        print("[INFO] 服务状态未知")

    print()
    print("[4] 检查端口...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
    else:
        print("[FAIL] 端口25未监听")

    print()
    print("="*60)
    print("配置完成")
    print("="*60)
    print()
    print("SMTP 配置信息：")
    print("  服务器: 62.234.211.119")
    print("  端口: 25")
    print("  认证方式: 无")
    print("  加密方式: 无")
    print()
    print("防火墙配置：")
    print("  认证: 不启用 / 无")
    print("  用户名: smtpuser（留空也可以）")
    print("  密码: 任意（留空也可以）")
    print("  端口: 25")
    print("="*60)
    print()
    print("请尝试重新配置防火墙：")
    print("1. 认证方式选择：无（或 None）")
    print("2. 用户名和密码可以留空")
    print("3. 服务器: 62.234.211.119")
    print("4. 端口: 25")

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
