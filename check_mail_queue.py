#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查Postfix邮件队列"""
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

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("检查Postfix邮件队列")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查邮件队列...")
    output = run(ssh, 'sudo mailq')
    print(output)
    print()

    print("[2] 检查队列详情（deferred队列）...")
    output = run(ssh, 'sudo mailq | grep -E "(deferred|hold)" | head -20')
    if output.strip():
        print("[发现] 待发送或延迟的邮件:")
        print(output)
    else:
        print("[OK] 没有待发送邮件")
    print()

    print("[3] 检查各队列目录...")
    commands = [
        'sudo ls -la /var/spool/postfix/deferred/',
        'sudo ls -la /var/spool/postfix/hold/',
        'sudo ls -la /var/spool/postfix/incoming/',
        'sudo ls -la /var/spool/postfix/maildrop/',
        'sudo ls -la /var/spool/postfix/active/',
    ]
    for cmd in commands:
        output = run(ssh, cmd)
        if 'total' in output or 'ls: cannot access' not in output.lower():
            print(f"  {output.strip()[:100]}")
    print()

    print("[4] 检查Postfix配置...")
    output = run(ssh, 'sudo postconf -n | grep -E "(queue_directory|deferred_transport)"')
    print(output)
    print()

    print("[5] 检查最近的邮件日志...")
    output = run(ssh, 'sudo tail -30 /var/log/mail.log | grep -E "(to=|from=|status=)"')
    print(output)
    print()

    print("[6] 检查队列统计...")
    output = run(ssh, 'sudo qshape | head -10')
    if output.strip():
        print("[队列统计]:")
        print(output)
    else:
        print("[INFO] qshape未安装")
    print()

    print("[7] 刷新队列（如果需要）...")
    output = run(ssh, 'sudo postsuper -r ALL')
    if output.strip():
        print(f"  刷新结果: {output}")
    else:
        print("[INFO] 队列为空")
    print()

    print("[8] 再次检查队列...")
    output = run(ssh, 'sudo mailq')
    print(output)
    print()

    print("="*60)
    print("队列检查完成")
    print("="*60)
    print()
    print("队列状态分析:")
    print("  1. 如果队列为空，说明所有邮件已发送")
    print("  2. 如果有待发送邮件，说明发送失败或延迟")
    print("  3. 邮件可能在deferred队列中等待")
    print()
    print("建议:")
    print("  1. 如果队列为空，检查QQ邮箱是否收到测试邮件")
    print("  2. 如果有待发送邮件，需要修复Postfix配置")
    print()

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] 检查失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
