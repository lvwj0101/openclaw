#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查SMTP服务日志，查找WAF连接记录"""
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
    print("SMTP服务日志检查 - WAF连接分析")
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

    print("[2] 检查端口25监听...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听:")
        print(output)
    else:
        print("[FAIL] 端口25未监听")
    print()

    print("[3] 检查最近的SMTP邮件日志...")
    output = run(ssh, 'sudo tail -50 /var/log/mail.log')
    print(output)
    print()

    print("[4] 检查最近的SMTP连接记录...")
    output = run(ssh, 'sudo grep -i "connect\|disconnect\|timeout\|refused\|reject" /var/log/mail.log | tail -30')
    if output.strip():
        print("[OK] 发现连接记录:")
        print(output)
    else:
        print("[INFO] 未发现连接记录")
    print()

    print("[5] 检查Postfix错误日志...")
    output = run(ssh, 'sudo tail -50 /var/log/mail.err 2>/dev/null || echo "错误日志文件不存在"')
    if 'not exist' not in output.lower():
        print(output)
    print()

    print("[6] 检查系统日志中的Postfix相关信息...")
    output = run(ssh, 'sudo journalctl -u postfix --since "10 minutes ago" --no-pager')
    if output.strip():
        print(output[:1000])
    print()

    print("[7] 检查邮件队列...")
    output = run(ssh, 'sudo mailq')
    if output.strip() and 'empty' not in output.lower():
        print("[WARNING] 邮件队列中有邮件:")
        print(output)
    else:
        print("[OK] 邮件队列为空")
    print()

    print("[8] 检查Postfix master进程...")
    output = run(ssh, 'ps aux | grep "master" | grep -v grep')
    if output.strip():
        print("[OK] Postfix master进程:")
        print(output)
    else:
        print("[FAIL] Postfix master进程未运行")
    print()

    print("[9] 发送新测试邮件并观察日志...")
    run(ssh, 'echo "WAF Test at $(date)" | mail -s "WAF SMTP Test" root@localhost')
    print("[OK] 测试邮件已发送，等待处理...")
    print()

    print("[10] 检查测试邮件后的日志...")
    output = run(ssh, 'sudo tail -10 /var/log/mail.log')
    print(output)
    print()

    print("[11] 检查邮件接收情况...")
    output = run(ssh, 'ls -la /home/waftest/Maildir/new/ 2>/dev/null | tail -5')
    if output.strip() and 'total' not in output.lower():
        print("[OK] 收到测试邮件:")
        print(output)
    else:
        print("[INFO] waftest邮箱为空或只有系统文件")
    print()

    print("[12] 检查所有邮箱的邮件...")
    output = run(ssh, 'find /home -name "Maildir" -type d -exec ls -la {}/new/ \\; 2>/dev/null | head -20')
    if output.strip():
        print("[OK] 所有邮箱中的邮件:")
        print(output)
    else:
        print("[INFO] 未找到邮件")
    print()

    print("[13] 检查网络连接...")
    output = run(ssh, 'sudo ss -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25网络连接:")
        print(output)
    print()

    print("[14] 检查Postfix配置中的网络设置...")
    output = run(ssh, 'sudo postconf -n | grep -E "(inet|networks|message_size|queue)"')
    print(output)
    print()

    print("[15] 测试服务器能否访问外网...")
    output = run(ssh, 'ping -c 3 8.8.8.8 2>&1 || echo "ping failed"')
    print(output)
    print()

    print("="*60)
    print("日志检查完成")
    print("="*60)
    print()
    print("分析:")
    print("1. 检查日志中是否有来自WAF(49.233.89.28)的连接记录")
    print("2. 检查是否有timeout或连接错误")
    print("3. 检查测试邮件是否被接收")
    print("4. 检查网络连通性")
    print()
    print("请将上述日志发给我，我会分析问题所在！")

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
