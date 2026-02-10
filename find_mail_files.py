#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查找已投递的邮件文件"""
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
    print("查找已投递的邮件文件")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查root用户的邮箱位置...")
    # 检查postconf中home_mailbox的配置
    output = run(ssh, 'sudo postconf home_mailbox')
    print(f"  home_mailbox配置: {output}")
    
    # 检查root用户的home目录
    output = run(ssh, 'ls -la /root/ | grep -E "Mail|mail"')
    print(f"  root目录中的邮件相关:")
    print(f"  {output}")
    
    # 查找root用户的Maildir
    output = run(ssh, 'find /root -name "Maildir" -type d 2>/dev/null')
    if output.strip():
        print(f"  找到的Maildir:")
        print(f"  {output}")
    
    # 检查/var/spool/mail目录
    output = run(ssh, 'ls -la /var/spool/mail/ 2>/dev/null')
    if output.strip():
        print(f"  /var/spool/mail/目录:")
        print(f"  {output}")
    
    # 检查root的mbox文件
    output = run(ssh, 'ls -la /root/ | grep mbox')
    if output.strip():
        print(f"  root目录中的mbox:")
        print(f"  {output}")
    
    # 搜索最近的邮件文件
    output = run(ssh, 'sudo find / -name "*.0" -newermt "2026-02-08 17:30" -type f 2>/dev/null | head -10')
    if output.strip():
        print(f"  最近的邮件文件:")
        print(f"  {output}")
    
    print()
    print("[2] 检查waftest用户的邮箱...")
    # 检查waftest用户的home目录
    output = run(ssh, 'ls -la /home/waftest/ | grep -E "Mail|mail"')
    print(f"  waftest目录中的邮件相关:")
    print(f"  {output}")
    
    # 查找waftest用户的Maildir
    output = run(ssh, 'find /home/waftest -name "Maildir" -type d 2>/dev/null')
    if output.strip():
        print(f"  找到的Maildir:")
        print(f"  {output}")
    
    print()
    print("[3] 列出所有Maildir/new目录中的文件...")
    # 列出所有Maildir/new目录
    output = run(ssh, 'sudo find / -type d -name "Maildir" -exec find {} -type d -name "new" -exec ls -la {}/\\; 2>/dev/null | head -20')
    if output.strip():
        print(f"  所有Maildir/new中的文件:")
        print(f"  {output}")
    else:
        print("  未找到邮件文件")
    
    print()
    print("[4] 检查最近的邮件日志...")
    output = run(ssh, 'sudo grep -i "delivered to maildir\|delivered to" /var/log/mail.log | tail -10')
    if output.strip():
        print(f"  最近的投递记录:")
        print(f"  {output}")
    else:
        print("  未找到投递记录")
    
    print()
    print("[5] 检查postconf中的mydestination配置...")
    output = run(ssh, 'sudo postconf mydestination')
    print(f"  mydestination: {output}")
    
    print()
    print("[6] 测试发送新邮件并追踪...")
    # 发送新邮件
    output = run(ssh, 'echo "FIND ME - $(date)" | mail -s "Find My Mail" root@localhost')
    print(f"  新邮件已发送")
    
    # 等待处理
    import time
    time.sleep(3)
    
    # 查找新邮件
    output = run(ssh, 'sudo find / -name "FIND*" -newermt "2026-02-08 17:45" -type f 2>/dev/null')
    if output.strip():
        print(f"  找到新邮件:")
        print(f"  {output}")
        
        # 读取邮件内容
        for line in output.split('\n'):
            if line.strip() and not line.startswith('find:'):
                file_path = line.split()[0]
                print()
                print(f"  读取邮件: {file_path}")
                content = run(ssh, f'sudo cat "{file_path}"')
                print(f"  邮件内容:")
                print(f"  {content}")
    else:
        print("  未找到新邮件")

    print()
    print("="*60)
    print("查找完成")
    print("="*60)

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] 查找失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
