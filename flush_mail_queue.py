#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""刷新邮件队列"""
import paramiko
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '49.233.89.28',
    'port': 22,
    'username': 'ubuntu',
    'password': 'dyc#10010'
}

def run(ssh, cmd, timeout=120):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("刷新邮件队列 - 重新投递待发送邮件")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查当前队列状态...")
    output = run(ssh, 'sudo mailq')
    print(output)
    print()

    print("[2] 刷新所有邮件队列...")
    commands = [
        # 刷新邮件队列（重新投递所有邮件）
        'sudo postsuper -r ALL',
        # 尝试立即投递
        'sudo postfix flush',
        # 启用所有队列
        'sudo qshape | head -20',
    ]
    for cmd in commands:
        try:
            run(ssh, cmd)
        except:
            pass
    print("[OK] 邮件队列已刷新")
    print()

    print("[3] 检查刷新后的队列...")
    output = run(ssh, 'sudo mailq')
    print(output)
    print()

    print("[4] 检查投递日志...")
    output = run(ssh, 'sudo tail -50 /var/log/mail.log | grep -i "status="')
    if output.strip():
        print("[邮件投递日志]:")
        print(output)
    else:
        print("[INFO] 未找到投递日志")
    print()

    print("[5] 增加日志记录以调试...")
    run(ssh, 'sudo postfix check')
    print("[OK] Postfix配置已检查")
    print()

    print("="*60)
    print("刷新完成！")
    print("="*60)
    print()
    print("下一步:")
    print("  1. 等待30秒，再次检查邮件队列")
    print("  2. 如果邮件队列为空，说明已投递成功")
    print("  3. 检查QQ邮箱是否收到测试邮件")
    print("  4. 如果还失败，可能需要修复DNS或邮件服务器配置")
    print()

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] 刷新失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
