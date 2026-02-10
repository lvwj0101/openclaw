#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断邮件投递失败问题"""
import paramiko
import sys
import io
import time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '49.233.89.28',
    'port': 22,
    'username': 'ubuntu',
    'password': 'dyc#10010'
}

QQ_EMAIL = '1187419065@qq.com'

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("诊断邮件投递失败")
    print("="*60)
    print(f"  目标邮箱: {QQ_EMAIL}")
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查Postfix服务...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    print(output)
    print()

    print("[2] 检查最近的邮件日志...")
    output = run(ssh, 'sudo tail -50 /var/log/mail.log')
    print(output)
    print()

    print("[3] 检查QQ邮箱相关的投递日志...")
    output = run(ssh, f'sudo grep -i "{QQ_EMAIL}" /var/log/mail.log | tail -20')
    if output.strip():
        print("[INFO] QQ邮箱投递日志:")
        print(output)
    else:
        print("[INFO] 未找到QQ邮箱投递日志")
    print()

    print("[4] 检查邮件队列...")
    output = run(ssh, 'sudo mailq')
    print(output)
    print()

    print("[5] 检查deferred队列...")
    output = run(ssh, 'sudo postsuper -d ALL deferred')
    print(output)
    print()

    print("[6] 检查DNS解析...")
    output = run(ssh, f'sudo dig mx {QQ_EMAIL.split("@")[1]} | grep -i mx')
    if output.strip():
        print("[DNS] QQ邮箱MX记录:")
        print(output)
    else:
        print("[INFO] dig命令未找到或DNS查询失败")
    print()

    print("[7] 检查端口25连通性...")
    output = run(ssh, f'sudo timeout 5 nc -zv {QQ_EMAIL.split("@")[1]} 25')
    if output.strip():
        print("[Connect] 端口25测试:")
        print(output)
    else:
        print("[INFO] 端口25测试超时")
    print()

    print("[8] 检查Postfix配置中的关键参数...")
    output = run(ssh, 'sudo postconf -n | grep -E "(mynetworks|inet|relayhost|smtpd_tls)"')
    print(output)
    print()

    print("[9] 检查邮件传输配置...")
    output = run(ssh, 'sudo postconf -n | grep -E "(transport|local_transport|relay)"')
    print(output)
    print()

    print("[10] 发送新测试邮件并观察...")
    test_cmd = f'echo "Diagnosis Test - {time.strftime("%H:%M:%S")}" | mail -s "Diagnosis Test" {QQ_EMAIL}'
    run(ssh, test_cmd)
    print("[OK] 测试邮件已发送")
    print()

    print("[11] 等待5秒后检查...")
    time.sleep(5)
    print()

    print("[12] 再次检查邮件队列...")
    output = run(ssh, 'sudo mailq')
    print(output)
    print()

    print("[13] 检查最新的邮件日志...")
    output = run(ssh, 'sudo tail -30 /var/log/mail.log')
    print(output)
    print()

    print("="*60)
    print("诊断完成！")
    print("="*60)
    print()
    print("可能的原因:")
    print("  1. QQ邮箱拒收（IP信誉问题、SPF、DKIM）")
    print("  2. DNS解析问题")
    print("  3. 端口25被封禁")
    print("  4. Postfix配置问题")
    print()
    print("解决方案:")
    print("  1. 查看下面的日志，找到投递失败的具体原因")
    print("  2. 如果是QQ邮箱拒收，可以尝试使用163邮箱")
    print("  3. 如果是端口25问题，可以配置中继服务器")
    print()
    print(f"完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] 诊断失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
