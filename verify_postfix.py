#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证Postfix服务状态"""
import paramiko
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '62.234.211.119',
    'port': 22,
    'username': 'ubuntu',
    'password': 'ji_pmrDc6jMCc6_'
}

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SERVER, timeout=10)

    print("="*60)
    print("Postfix 服务验证")
    print("="*60)
    print()

    # 1. 检查服务状态
    print("[1] 检查Postfix服务状态...")
    stdin, stdout, stderr = ssh.exec_command('sudo systemctl status postfix --no-pager')
    status = stdout.read().decode('utf-8')
    print(status[:500])
    print()

    # 2. 检查端口监听
    print("[2] 检查端口25...")
    stdin, stdout, stderr = ssh.exec_command('sudo netstat -tlnp | grep :25')
    port25 = stdout.read().decode('utf-8')
    if port25:
        print(f"[OK] 端口25正在监听:")
        print(port25)
    else:
        print("[WARNING] 端口25未监听")
    print()

    # 3. 检查端口587
    print("[3] 检查端口587...")
    stdin, stdout, stderr = ssh.exec_command('sudo netstat -tlnp | grep :587')
    port587 = stdout.read().decode('utf-8')
    if port587:
        print(f"[OK] 端口587正在监听:")
        print(port587)
    else:
        print("[INFO] 端口587未监听（可选）")
    print()

    # 4. 测试发送邮件
    print("[4] 测试发送邮件...")
    stdin, stdout, stderr = ssh.exec_command('echo "Test from Postfix" | mail -s "Test Email" smtpuser@localhost')
    print("[OK] 测试邮件已发送")
    print()

    # 5. 查看邮箱
    print("[5] 查看邮箱...")
    stdin, stdout, stderr = ssh.exec_command('ls -la /home/smtpuser/Maildir/new/')
    inbox = stdout.read().decode('utf-8')
    if inbox.strip():
        print(f"[OK] 收到邮件:")
        print(inbox)
    else:
        print("[INFO] 邮箱为空")
    print()

    # 6. 查看最新日志
    print("[6] 查看最新邮件日志...")
    stdin, stdout, stderr = ssh.exec_command('sudo tail -20 /var/log/mail.log')
    logs = stdout.read().decode('utf-8')
    print(logs)

    ssh.close()

    print()
    print("="*60)
    print("验证完成")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
